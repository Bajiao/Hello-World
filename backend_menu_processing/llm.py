"""
Centralized LLM API Module
This module provides unified interfaces for all LLM API calls used across the project:
- OpenAI GPT-4 (ingredient splitting, menu ranking, vision analysis)
- Google Gemini Flash (deduplication, annotation, standardization)

All API keys are loaded from .env file. No keys should be hardcoded anywhere.
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Tuple, List, Dict, Optional, Any
from dotenv import load_dotenv
import openai
import google.generativeai as genai
from openai import OpenAI
import httpx


# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

def load_env_variables(env_file: Optional[str] = None) -> None:
    """
    Load environment variables from .env file.
    Searches in multiple locations for flexibility.
    
    Args:
        env_file: Optional explicit path to .env file. If not provided, searches:
                  1. Current directory (.env)
                  2. Parent directory (../.env)
                  3. Root project directory
    """
    if env_file is None:
        # Try multiple locations
        possible_paths = [
            Path(".env"),
            Path("../.env"),
            Path("../../.env"),
            Path.home() / ".env.hello-world",
        ]
        
        for path in possible_paths:
            if path.exists():
                load_dotenv(dotenv_path=path)
                print(f"✓ Loaded environment from: {path}")
                return
        
        # If none found, try loading from current directory anyway (in case it's in PATH)
        load_dotenv()
        print("✓ Loaded environment from default locations")
    else:
        load_dotenv(dotenv_path=env_file)
        print(f"✓ Loaded environment from: {env_file}")


def get_api_key(key_name: str, allow_empty: bool = False) -> str:
    """
    Safely retrieve API key from environment.
    
    Args:
        key_name: Name of the environment variable (e.g., 'OPENAI_API_KEY')
        allow_empty: If True, return empty string if not found. If False, raise error.
    
    Returns:
        API key value
    
    Raises:
        ValueError: If key not found and allow_empty is False
    """
    key = os.getenv(key_name)
    
    if key is None or key == "":
        if allow_empty:
            return ""
        raise ValueError(
            f"Required API key '{key_name}' not found in environment. "
            f"Please set it in your .env file. See .env.sample for format."
        )
    
    return key


# ============================================================================
# OPENAI API FUNCTIONS
# ============================================================================

class OpenAIClient:
    """Centralized OpenAI API client with connection pooling."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        load_env_variables()
        api_key = get_api_key("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))
        self._initialized = True
    
    def get_client(self) -> OpenAI:
        """Get OpenAI client instance."""
        return self.client


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client singleton."""
    return OpenAIClient().get_client()


def split_ingredient_openai(ingredient: str) -> Tuple[str, str]:
    """
    Split an ingredient string into (descriptor, core_ingredient) using OpenAI GPT-4.
    
    Used in: Step 1 of preprocessing pipeline
    Model: gpt-4-1106-preview
    Cost: ~$0.01 input, $0.03 output per 1K tokens
    
    Args:
        ingredient: Raw ingredient string (e.g., "2 cups chopped onions")
    
    Returns:
        Tuple of (descriptor, core_ingredient)
        Example: ("2 cups chopped", "onions")
    
    Example:
        >>> split_ingredient_openai("1 cup sliced onions")
        ('1 cup sliced', 'onions')
    """
    prompt = (
        f"Extract this ingredient string into two fields: "
        f"(1) quantity, measurement, or descriptor; "
        f"(2) core ingredient name. The core ingredient name is usually the last word or words "
        f"in the string, but not always. It should not include preparation methods or other descriptors. "
        f"Return ONLY the Python tuple: (descriptor, ingredient). Do not include any explanation or extra text. "
        f"Example: '2 cups chopped onions' -> ('2 cups chopped', 'onions'). "
        f"Ingredient: '{ingredient}'"
    )
    
    client = get_openai_client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
        temperature=0
    )
    
    result = response.choices[0].message.content.strip()
    try:
        return ast.literal_eval(result)
    except Exception as e:
        print(f"Error parsing ingredient split result: {result}\nException: {e}")
        return (None, ingredient)


def rank_menus_openai(
    client: Optional[OpenAI] = None,
    menus_with_ingredients: List[Dict[str, Any]] = None,
    disease: str = "diabetes",
    top_k: int = 10
) -> Optional[List[Dict[str, Any]]]:
    """
    Rank menus by health risk for a specific disease using OpenAI GPT-4o.
    
    Used in: Evaluation system for menu ranking
    Model: gpt-4o
    Cost: ~$0.10-0.20 per call
    
    Args:
        client: OpenAI client (if None, creates new one)
        menus_with_ingredients: List of dicts with 'menu' and 'ingredients' keys
        disease: Target disease ('diabetes', 'cardiovascular', 'kidney')
        top_k: Return top k menus
    
    Returns:
        List of ranked menus with scores and reasoning, or None if error
    
    Example:
        >>> menus = [
        ...     {'menu': 'Burger', 'ingredients': ['beef', 'salt', 'bun']},
        ...     {'menu': 'Salad', 'ingredients': ['lettuce', 'oil', 'vinegar']}
        ... ]
        >>> ranks = rank_menus_openai(menus=menus, disease='diabetes')
    """
    if client is None:
        client = get_openai_client()
    
    if not menus_with_ingredients:
        return None
    
    entries = [
        {"menu": item.get("menu", "Unknown"), "ingredients": item.get("ingredients", [])}
        for item in menus_with_ingredients[:top_k]
    ]
    
    prompt_system = (
        f"You are a medical nutritionist expert. Your task is to rank restaurant menus "
        f"by how NOT RECOMMENDED they are for patients with {disease}. "
        f"Score each menu 0-100 where 100 = extremely NOT RECOMMENDED, 0 = recommended.\n\n"
        f"Return ONLY a valid JSON array of objects with keys: menu, score(0-100), reasoning"
    )
    
    prompt_user = f"Menus with ingredients:\n{json.dumps(entries, ensure_ascii=False, indent=2)}"
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": prompt_user}
            ],
            temperature=0
        )
        text = resp.choices[0].message.content
        
        # Extract JSON from response
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error ranking menus with OpenAI: {e}")
        return None


def extract_recipes_from_image(image_path: str) -> Optional[List[str]]:
    """
    Extract recipe names from a menu image using OpenAI GPT-4 Vision.
    
    Used in: Frontend image upload feature
    Model: gpt-4.1 (vision enabled)
    
    Args:
        image_path: Path to image file (PNG, JPG, JPEG)
    
    Returns:
        List of recipe names extracted from image, or empty list if extraction fails
    
    Example:
        >>> recipes = extract_recipes_from_image("menu_photo.jpg")
        >>> print(recipes)
        ['Burger', 'Fries', 'Salad']
    """
    import base64
    
    client = get_openai_client()
    
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        
        ext = image_path.rsplit('.', 1)[1].lower()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/{ext};base64,{image_base64}"
        
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "system",
                    "content": "Extract ALL dish/recipe names uniquely from the image. "
                              "Ignore drinks, prices, descriptions, categories. "
                              "Return only JSON adhering to the schema."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Parse this menu and return all recipe names."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "menu_recipes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "recipes": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Unique recipe or dish names found in the image"
                            }
                        },
                        "required": ["recipes"],
                        "additionalProperties": False
                    },
                    "strict": True
                },
            },
            temperature=0
        )
        
        obj = json.loads(response.choices[0].message.content)
        recipes = obj.get("recipes", [])
        
        # Clean all recipes: strip whitespace including newlines
        cleaned_recipes = []
        for recipe in recipes:
            # Remove all types of whitespace including \n, \r, \t
            cleaned = recipe.strip()
            # Remove literal backslash-n (two character sequence)
            cleaned = cleaned.replace('\\n', ' ')
            # Remove actual newlines and other whitespace
            cleaned = re.sub(r'[\n\r\t]+', ' ', cleaned)
            # Remove multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned:  # Only add non-empty recipes
                cleaned_recipes.append(cleaned)
        
        return cleaned_recipes
    
    except Exception as e:
        print(f"Error extracting recipes from image: {e}")
        return []


def ask_openai_follow_up(
    question: str,
    context: str = "",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Optional[str]:
    """
    Ask GPT-4o a follow-up question with context.
    
    Used in: Frontend follow-up questions after image upload
    Model: gpt-4o
    
    Args:
        question: User's question
        context: Background context (extracted recipes, health data, etc.)
        conversation_history: Previous messages in conversation
    
    Returns:
        Model's response or None if error
    
    Example:
        >>> answer = ask_openai_follow_up(
        ...     "Is this menu healthy?",
        ...     context="Extracted recipes: Burger, Fries, Salad"
        ... )
    """
    client = get_openai_client()
    
    messages = conversation_history or []
    
    if context:
        messages.insert(0, {
            "role": "system",
            "content": f"You are a helpful nutritionist assistant.\n\nContext: {context}"
        })
    else:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful nutritionist assistant."
        })
    
    messages.append({"role": "user", "content": question})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error asking OpenAI follow-up: {e}")
        return None


# ============================================================================
# GOOGLE GEMINI API FUNCTIONS
# ============================================================================

class GeminiClient:
    """Centralized Gemini API client."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        load_env_variables()
        api_key = get_api_key("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        self._initialized = True


def get_gemini_client() -> None:
    """Initialize Gemini client."""
    GeminiClient()


def generate_response_gemini(prompt: str, model: str = "gemini-2.5-flash-lite") -> Optional[str]:
    """
    Send a prompt to Google Gemini and get response.
    
    Used in: Steps 3-5 of preprocessing (dedup, annotation, standardization)
    Model: gemini-2.5-flash-lite (default)
    Temperature: 0.01 (near-deterministic)
    Max output tokens: 32,000
    
    Args:
        prompt: The prompt to send
        model: Gemini model to use (default: gemini-2.5-flash-lite)
    
    Returns:
        Model's text response or None if error
    
    Example:
        >>> response = generate_response_gemini(
        ...     "Deduplicate these ingredients: onions, onion, lettuce"
        ... )
    """
    get_gemini_client()
    
    generation_config = {
        "temperature": 0.01,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 32000,
    }
    
    try:
        model_obj = genai.GenerativeModel(
            model_name=model,
            generation_config=generation_config
        )
        response = model_obj.generate_content([prompt])
        
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            print("No valid response text returned from Gemini")
            return None
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return None


def deduplicate_ingredients_gemini(ingredients: List[str]) -> Optional[List[str]]:
    """
    Remove duplicate and similar ingredients using Gemini.
    
    Used in: Step 3 of preprocessing
    
    Args:
        ingredients: List of ingredient names
    
    Returns:
        List of deduplicated canonical ingredient names
    
    Example:
        >>> dedupe = deduplicate_ingredients_gemini(['onion', 'onions', 'lettuce'])
        >>> print(dedupe)
        ['onion', 'lettuce']
    """
    prompt = (
        "Remove duplicate and semantically similar ingredients. "
        "Return a JSON array of unique canonical ingredient names. "
        "Do not use plural forms if singular exists. "
        f"Ingredients: {json.dumps(ingredients)}"
    )
    
    response_text = generate_response_gemini(prompt)
    if not response_text:
        return None
    
    try:
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error parsing Gemini deduplication response: {e}")
        return None


def annotate_ingredient_disease_gemini(
    ingredients: List[str],
    disease: str = "diabetes"
) -> Optional[List[Dict[str, str]]]:
    """
    Annotate ingredients with health effects for a specific disease using Gemini.
    
    Used in: Step 4 of preprocessing (3 calls for 3 diseases)
    Batch size: 50 ingredients per call
    
    Args:
        ingredients: List of ingredient names
        disease: Target disease ('diabetes', 'cardiovascular', 'kidney')
    
    Returns:
        List of dicts with keys: ingredient, effect, reason
        effect in: ['positive', 'neutral', 'negative', 'very negative']
    
    Example:
        >>> annotations = annotate_ingredient_disease_gemini(
        ...     ['sugar', 'lettuce', 'salt'],
        ...     disease='diabetes'
        ... )
    """
    prompt = (
        f"For the disease '{disease}', classify the health impact of each ingredient "
        f"as 'positive', 'neutral', 'negative', or 'very negative'. "
        f"Return ONLY a JSON array of objects with keys: "
        f"'ingredient', 'effect', 'reason' (short explanation if not neutral). "
        f"If no known effect, use 'neutral'. "
        f"Ingredients: {json.dumps(ingredients)}"
    )
    
    response_text = generate_response_gemini(prompt)
    if not response_text:
        return None
    
    try:
        match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error parsing Gemini annotation response: {e}")
        return None


def standardize_ingredients_gemini(
    menu_ingredients: Dict[str, List[str]],
    canonical_ingredients: List[str]
) -> Optional[Dict[str, List[str]]]:
    """
    Standardize menu ingredients to canonical list using Gemini.
    
    Used in: Step 5 of preprocessing
    
    Args:
        menu_ingredients: Dict mapping menu names to ingredient lists
        canonical_ingredients: List of canonical ingredient names
    
    Returns:
        Dict mapping menu names to standardized ingredient lists
    
    Example:
        >>> menus = {'Burger': ['beef patty', 'bun', 'lettuce']}
        >>> canonical = ['beef', 'bun', 'lettuce']
        >>> standard = standardize_ingredients_gemini(menus, canonical)
    """
    prompt = (
        f"Map the following menu ingredients to the canonical ingredient list. "
        f"For each menu ingredient, find the closest match in the canonical list. "
        f"Return ONLY a JSON object mapping menu names to lists of canonical ingredients. "
        f"Menu ingredients: {json.dumps(menu_ingredients)}\n"
        f"Canonical list: {json.dumps(canonical_ingredients)}"
    )
    
    response_text = generate_response_gemini(prompt)
    if not response_text:
        return None
    
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error parsing Gemini standardization response: {e}")
        return None


def judge_rankings_gemini(
    disease: str,
    ground_truth: List[Dict[str, Any]],
    graph_ranking: List[Dict[str, Any]],
    llm_ranking: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """
    Judge which ranking (graph-based vs LLM-based) is better using Gemini.
    
    Used in: Evaluation system for menu ranking comparison
    
    Args:
        disease: Target disease
        ground_truth: Ground truth menu-ingredient mappings
        graph_ranking: Graph-based ranking results
        llm_ranking: LLM-based ranking results
    
    Returns:
        Dict with keys: winner, explanation, differences
    
    Example:
        >>> verdict = judge_rankings_gemini(
        ...     disease='diabetes',
        ...     ground_truth=[...],
        ...     graph_ranking=[...],
        ...     llm_ranking=[...]
        ... )
    """
    payload = {
        "instruction": (
            f"You are a neutral expert judge. Target disease: '{disease}'. "
            "You are given:\n"
            "1) Ground truth: canonical ingredient lists per menu\n"
            "2) Ranking A: graph-based results with score and reasoning\n"
            "3) Ranking B: LLM-based results with score and reasoning\n\n"
            "Task: Using ONLY ground-truth ingredients as evidence, decide which ranking "
            "is better at identifying NOT RECOMMENDED menus. "
            "Return JSON with keys: winner (graph/llm/tie), explanation, differences."
        ),
        "ground_truth": ground_truth[:10],  # Limit to reduce tokens
        "graph_ranking": graph_ranking[:5],
        "llm_ranking": llm_ranking[:5]
    }
    
    prompt_text = (
        f"{payload['instruction']}\n\n"
        f"GROUND_TRUTH:\n{json.dumps(payload['ground_truth'], ensure_ascii=False, indent=2)}\n\n"
        f"GRAPH_RANKING:\n{json.dumps(payload['graph_ranking'], ensure_ascii=False, indent=2)}\n\n"
        f"LLM_RANKING:\n{json.dumps(payload['llm_ranking'], ensure_ascii=False, indent=2)}"
    )
    
    response_text = generate_response_gemini(prompt_text)
    if not response_text:
        return None
    
    try:
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception as e:
        print(f"Error parsing Gemini judge response: {e}")
        return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_project_root() -> Path:
    """
    Get the project root directory (where .git or main README exists).
    
    Returns:
        Path object pointing to project root
    """
    current = Path.cwd()
    
    # Look for .git or project markers
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists() or (parent / "README.md").exists():
            return parent
    
    return current


def get_data_dir(relative_path: str = "backend_menu_processing/data") -> Path:
    """
    Get data directory with support for relative paths.
    
    Args:
        relative_path: Path relative to project root
    
    Returns:
        Absolute Path to data directory
    """
    return get_project_root() / relative_path


if __name__ == "__main__":
    # Test loading environment
    print("Testing LLM module...")
    load_env_variables()
    print(f"OpenAI API Key loaded: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"Gemini API Key loaded: {'✓' if os.getenv('GOOGLE_API_KEY') else '✗'}")
    print("LLM module ready!")
