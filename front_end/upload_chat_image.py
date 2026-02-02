"""
Menu Chat Image Upload Application

This Flask application provides a web interface for:
1. Uploading menu images and extracting recipe names using OpenAI Vision API
2. Searching for matching recipes in a FAISS vector database
3. Providing health-related information (disease risk scores and reasoning)
4. Answering follow-up questions about recipes based on extracted information

The application uses:
- OpenAI Vision API for menu image analysis
- FAISS vector database for semantic recipe similarity search
- LangChain for embedding generation and vector operations
- Flask for the web interface
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, render_template, send_from_directory
import pickle
import json
import html
import re

# Add parent directory to path to import llm module
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import pandas as pd
import markdown

# Import centralized LLM functions
from backend_menu_processing.llm import (
    load_env_variables,
    get_openai_client,
    extract_recipes_from_image,
    ask_openai_follow_up,
    get_project_root
)
from backend_menu_processing.recommendation_api import MenuRecommendationAPI
from difflib import SequenceMatcher, get_close_matches


# ============================================================================
# SETUP AND INITIALIZATION
# ============================================================================
# Load environment variables and initialize clients needed for the application

# Load environment variables
load_env_variables()

# Get OpenAI client
client = get_openai_client()

# Define base directories using functions (no hardcoded paths)
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = get_project_root()

print(f"Base directory: {BASE_DIR}")
print(f"Project root: {PROJECT_ROOT}")


# === Custom Embeddings Class ===
class CustomOpenAIEmbeddings(Embeddings):
    """
    Custom embedding model wrapper for LangChain compatibility.
    
    Wraps OpenAI's text-embedding-3-large model to work with LangChain's
    FAISS vector store interface. Handles both single queries and document
    batches.
    
    Attributes:
        client: OpenAI client instance used for API calls
    """

    def __init__(self, client):
        """Initialize embeddings with an OpenAI client."""
        self.client = client

    def embed_documents(self, texts):
        """
        Generate embeddings for multiple documents/texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (lists of floats)
        """
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        """
        Generate embedding for a single query text.
        
        Args:
            text: Single text string to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        return self._embed(text)

    def _embed(self, text):
        """
        Internal method to call OpenAI embedding API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector from OpenAI's text-embedding-3-large model
        """
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding


# === Initialize embeddings ===
embeddings = CustomOpenAIEmbeddings(client)
print(f"✓ Embeddings initialized: {embeddings}")

# === Load FAISS vectorstore with resilient path resolution ===
# Try multiple possible locations to find the FAISS vectorstore
vectorstore_paths = [
    BASE_DIR / "faiss_vectorstore_recipes",
    BASE_DIR / "." / "faiss_vectorstore_recipes",
    PROJECT_ROOT / "front_end" / "faiss_vectorstore_recipes",
]

vectorstore = None
vectorstore_path = None
for path in vectorstore_paths:
    try:
        if path.exists():
            vectorstore = FAISS.load_local(
                folder_path=str(path),
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )
            vectorstore_path = path
            print(f"✓ Successfully loaded FAISS vectorstore from: {path}")
            break
    except Exception as e:
        print(f"Debug: Failed to load from {path}: {e}")
        continue

if vectorstore is None:
    raise ValueError(
        f"Could not load FAISS vectorstore from any of: {vectorstore_paths}"
    )

# === Load metadata with resilient path resolution ===
# Metadata contains disease scoring information for recipes
metadata_paths = [
    vectorstore_path / "faiss_vectorstore_metadatas.pkl",
    BASE_DIR / "faiss_vectorstore_recipes" / "faiss_vectorstore_metadatas.pkl",
    PROJECT_ROOT / "front_end" / "faiss_vectorstore_recipes" / "faiss_vectorstore_metadatas.pkl",
]

metadatas = None
for path in metadata_paths:
    if path.exists():
        try:
            with open(path, "rb") as f:
                metadatas = pickle.load(f)
            print(f"✓ Loaded metadata from: {path}")
            break
        except Exception as e:
            print(f"  ⚠️  Failed to load metadata from {path}: {e}")
            continue

if metadatas is None:
    raise ValueError(
        f"Could not find faiss_vectorstore_metadatas.pkl in any of: {metadata_paths}"
    )

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================
# Configure Flask app with template and static file directories

# Initialize Flask app with explicit paths
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_FOLDER = TEMPLATE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR)
)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"✓ Upload folder configured: {UPLOAD_FOLDER}")

# Helper to check allowed file type
def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        True if file has an allowed extension (png, jpg, jpeg), False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# In-memory store for uploaded analysis results: { filename: {answer, recipes, matches} }
UPLOAD_ANALYSIS_RESULTS = {}


def normalize_menu_name(name: str) -> str:
    """Normalize menu/title string similar to preprocessing: strip, lower, unescape, remove extra punctuation and collapse spaces."""
    if not name:
        return ""
    s = html.unescape(name)
    s = s.strip()
    s = re.sub(r'\\s+', ' ', s)
    s = s.strip()
    # remove surrounding quotes and trailing punctuation
    s = s.strip('"\'')
    s = re.sub(r'[\t\r\n]+', ' ', s)
    s = s.strip()
    return s

# ============================================================================
# CHAT AND PROCESSING FUNCTIONS
# ============================================================================

def ask_openai_image(image_path):
    """
    Extract recipe names from an image and find matching recipes with health data.
    
    Process flow:
    1. Use OpenAI Vision API to extract all dish/recipe names from the menu image
    2. For each extracted recipe, search the FAISS vector store for the best match
    3. Retrieve disease risk scores and reasoning from recipe metadata
    4. Generate an HTML table displaying results
    
    Args:
        image_path: File path to the image to process
        
    Returns:
        Tuple of (html_output, empty_string, empty_string):
        - html_output: HTML string with extracted recipes list and results table
        - Unused strings maintained for interface compatibility
    """
    try:
        # Use centralized function from llm.py to extract recipes
        recipes = extract_recipes_from_image(image_path)
        
        if not recipes:
            print("No recipes extracted from image")
            return "", "<p>No recipes found in image</p>", ""

        print(f"Raw recipes received from extract_recipes_from_image:")
        for i, r in enumerate(recipes):
            print(f"  Recipe {i}: {repr(r)}", flush=True)
            has_literal_n = '\\n' in r
            has_newline = '\n' in r
            print(f"    Has literal backslash-n: {has_literal_n}, Has newline: {has_newline}", flush=True)

        # Show extracted recipes first - handle recipes as a list and clean whitespace aggressively
        # Strip each recipe and remove any internal newlines/special characters
        if isinstance(recipes, str):
            # If it's a string, split by newlines and clean each part
            recipes_str = recipes.replace('\\n', '\n')  # Ensure we have real newlines
            cleaned_recipes = []
            for line in recipes_str.split('\n'):
                cleaned = line.strip()
                # Remove any remaining escape sequences or special chars
                cleaned = re.sub(r'[\r\n\t\\]+', ' ', cleaned)
                if cleaned:
                    cleaned_recipes.append(cleaned)
        else:
            # If it's already a list, clean each item thoroughly
            cleaned_recipes = []
            for r in recipes:
                if isinstance(r, str):
                    # Strip and remove all newlines and special whitespace
                    cleaned_r = r.strip()
                    # Remove literal backslash-n sequences (two character sequence)
                    cleaned_r = cleaned_r.replace('\\n', ' ')
                    # Remove actual newlines
                    cleaned_r = re.sub(r'[\n\r\t]+', ' ', cleaned_r)
                    # Remove multiple consecutive spaces
                    cleaned_r = re.sub(r'\s+', ' ', cleaned_r).strip()
                    if cleaned_r:
                        cleaned_recipes.append(cleaned_r)
        
        print(f"Cleaned recipes: {cleaned_recipes}", flush=True)
        print(f"Cleaned recipes repr: {repr(cleaned_recipes)}", flush=True)
        
        # Format recipes list as HTML bullet points with proper line breaks
        # Use html.escape() to safely handle any special characters and prevent XSS
        recipes_html = '<br>'.join([f"• {html.escape(r)}" for r in cleaned_recipes])
        extracted_html = f"<b>Extracted recipes from image:</b><br>{recipes_html}<br><br>"
        print(f"Extracted HTML (first 500 chars): {repr(extracted_html[:500])}", flush=True)

        # Step 2: For each extracted recipe, run vector search and collect results
        # Use cleaned_recipes instead of original recipes to avoid newline characters
        all_keys = set()
        recipe_results = []
        for recipe_query in cleaned_recipes:
            # Search FAISS vector store for most similar recipe (k=1 means top 1 match)
            docs_and_scores = vectorstore.similarity_search_with_score(recipe_query, k=1)
            if docs_and_scores:
                # Keys to display: disease scores and health reasoning
                selected_keys = [
                    'score_cardiovascular', 'reasoning-cardiovascular',
                    'score_diabetes', 'reasoning-diabetes',
                    'score_kidney', 'reasoning-kidney'
                ]
                for doc, score in docs_and_scores:
                    meta = doc.metadata if hasattr(doc, 'metadata') else {}
                    recipe_name = meta.get('name') or (doc.page_content.split('\n')[0] if doc.page_content else 'Unknown')
                    # Filter metadata to only selected keys and add similarity score
                    meta_filtered = {k: meta.get(k, '') for k in selected_keys}
                    meta_filtered['similarity_score'] = float(score) if score is not None else ''
                    all_keys.update(meta_filtered.keys())
                    recipe_results.append({
                        'query': recipe_query,
                        'matched': recipe_name,
                        'meta': meta_filtered
                    })
            else:
                recipe_results.append({
                    'query': recipe_query,
                    'matched': 'No relevant recipe found.',
                    'meta': {}
                })

        all_keys = sorted(all_keys)
        display_keys = ['matched', 'similarity_score']
        
        # Build table HTML with styling for better readability
        results_table = '''
        <div style="overflow-x:auto; margin-top:12px; max-height:500px;">
        <table border="1" style="border-collapse:collapse; width:98%; min-width:800px; background:#fff; font-size:1rem;">
            <thead style="background:#f2f2f2; position:sticky; top:0; z-index:2;">
                <tr>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Recipe Query</th>
'''
        # Add column headers
        for k in display_keys:
            header_label = 'Most Matched Recipe' if k == 'matched' else k
            results_table += f'<th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">{header_label}</th>'
        results_table += '''
                </tr>
            </thead>
            <tbody>
'''
        # Add data rows
        for result in recipe_results:
            results_table += f'<tr>'
            # Clean the query: strip all whitespace including newlines and escape for HTML
            clean_query = result["query"].strip()
            clean_query = clean_query.replace('\\n', ' ')  # Remove literal backslash-n
            clean_query = re.sub(r'[\n\r\t]+', ' ', clean_query)  # Remove actual whitespace
            clean_query = re.sub(r'\s+', ' ', clean_query).strip()
            results_table += f'<td style="padding:8px;">{html.escape(clean_query)}</td>'
            for k in display_keys:
                val = result["meta"].get(k, '')
                if isinstance(val, float):
                    val = f"{val:.3f}"
                results_table += f'<td style="padding:8px;">{val}</td>'
            results_table += '</tr>'
        
        results_table += '''
            </tbody>
        </table>
        </div>
'''
        final_html = extracted_html + results_table
        # CRITICAL: Aggressive final cleanup for escape sequences
        # Remove ALL variants of escaped newlines - this is the key issue!
        final_html = final_html.replace('\\n', '')  # backslash-n (two chars)
        final_html = final_html.replace('\\\\n', '')  # double-escaped backslash-n
        final_html = final_html.replace('&#92;n', '')  # HTML entity for backslash-n
        final_html = final_html.replace('&bsol;n', '')  # HTML entity variant
        final_html = re.sub(r'\\[rnt]', '', final_html)  # Any escaped whitespace chars
        final_html = re.sub(r'\n\n\n+', '\n', final_html)  # Collapse multiple newlines
        
        # One more pass - remove spaces that are just \n patterns that we missed
        # This catches if they somehow slipped through with spaces around them
        pattern = r'\s*\\\s*n\s*'
        final_html = re.sub(pattern, '', final_html, flags=re.IGNORECASE)
        
        final_html = final_html.strip()
        
        # Verification: Check what's actually in the final HTML
        print(f"DEBUG: Final HTML length: {len(final_html)}", flush=True)
        print(f"DEBUG: Final HTML repr (last 500 chars): {repr(final_html[-500:])}", flush=True)
        has_backslash_n = '\\n' in final_html
        print(f"DEBUG: Has literal backslash-n? {has_backslash_n}", flush=True)
        has_pattern = bool(re.search(pattern, final_html))
        print(f"DEBUG: Has backslash-n pattern? {has_pattern}", flush=True)
        
        return final_html
    except Exception as e:
        print(f"Error in ask_openai_image: {e}")
        return f"Error: {str(e)}", "<p>Error processing image</p>", ""


def ask_openai_over_image_output(answer: str, question: str) -> str:
    """
    Answer a follow-up question based on extracted recipe information.
    
    Uses OpenAI to generate contextual responses about the recipes and their
    health implications based on the extracted and analyzed recipe data.
    
    Args:
        answer: HTML string containing extracted recipe information from ask_openai_image
        question: User's follow-up question about the recipes
        
    Returns:
        HTML string containing the response (converted from markdown for proper rendering)
    """
    try:
        response = ask_openai_follow_up(
            question=question,
            context=f"Extracted recipe information:\n{answer}"
        )
        if response:
            # First pass: Fix numbered list formatting where content appears on next line
            # Pattern: "1.\n" should become "1. " (number, dot, space on same line as content)
            response = re.sub(r'(\d+\.)\s*\n\s+', r'\1 ', response)
            
            # Second pass: Fix bulleted list formatting
            response = re.sub(r'([-•*])\s*\n\s+', r'\1 ', response)
            
            # Clean up the markdown: remove excessive blank lines but keep formatting
            lines = response.split('\n')
            cleaned_lines = []
            blank_count = 0
            for line in lines:
                if line.strip():
                    cleaned_lines.append(line)
                    blank_count = 0
                else:
                    blank_count += 1
                    if blank_count < 2:  # Allow max 1 blank line between content
                        cleaned_lines.append(line)
            
            cleaned_response = '\n'.join(cleaned_lines).strip()
            # Convert markdown to HTML for proper rendering without adding extra line breaks
            html_response = markdown.markdown(cleaned_response)
            # Post-process to clean up list formatting
            # Remove <p> tags from inside <li> items to keep number and content on same line
            html_response = re.sub(r'<li>\s*<p>(.+?)</p>\s*</li>', r'<li>\1</li>', html_response, flags=re.DOTALL)
            # Remove unwanted <br> tags that markdown adds after list items
            html_response = re.sub(r'(</li>)\s*<br>\s*', r'\1', html_response)
            return html_response
        return "<p>Could not generate a response</p>"
    except Exception as e:
        print(f"Error in ask_openai_over_image_output: {e}")
        return f"<p>Error: {str(e)}</p>"


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Main upload and chat interface endpoint.
    
    Handles three types of requests:
    1. Image upload: Extract recipes and disease risk information
    2. Follow-up question with existing answer: Answer based on previous extraction
    3. Follow-up question without answer: Find most recent upload and process it
    
    Returns:
        Rendered HTML template with filename, question, answer, and followup results
    """
    filename = None
    question = None
    answer = None
    followup = None
    recommendation = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        question = request.form.get('question')
        # Fields for customized analysis
        condition = request.form.get('condition')
        customQuestion = request.form.get('customQuestion')

        if uploaded_file and allowed_file(uploaded_file.filename):
            # Handle image upload
            filename = uploaded_file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                answer = ask_openai_image(file_path)
                # Immediately parse recipes and perform matching (exact or LLM fallback)
                try:
                    bullets = re.findall(r'•\s*([^<\n]+)', answer)
                    # Normalize and lowercase to match graph keys
                    parsed_recipes = [normalize_menu_name(html.unescape(b).strip()).lower() for b in bullets if b and b.strip()]
                except Exception:
                    parsed_recipes = []

                matches = []
                try:
                    api = MenuRecommendationAPI()
                    for recipe in parsed_recipes:
                        # Try exact lookup in graph
                        node = api.graph.get_menu_node_from_string(recipe)
                        if node:
                            try:
                                matched_key = api.graph.normalize_string(node)
                            except Exception:
                                matched_key = str(node).strip().lower()
                            matches.append({
                                'query': recipe,
                                'matched_menu': node,
                                'matched_key': matched_key,
                                'is_exact': True
                            })
                        else:
                            # Use LLM/graph fallback as in process_menu_ingredient.main()
                            try:
                                best = api.graph.find_best_matched_menu_in_graph(recipe)
                                matched_menu = best.get('matched_menu') if isinstance(best, dict) else None
                                is_exact = best.get('is_exact', False) if isinstance(best, dict) else False
                                # If LLM fallback failed (None), try local vectorstore similarity as a backup
                                if not matched_menu:
                                    try:
                                        docs = vectorstore.similarity_search_with_score(recipe, k=3)
                                        for doc, sc in docs:
                                            meta_name = ''
                                            try:
                                                meta_name = doc.metadata.get('name') if hasattr(doc, 'metadata') else ''
                                            except Exception:
                                                meta_name = ''
                                            if meta_name:
                                                cand = normalize_menu_name(meta_name).lower()
                                                node2 = api.graph.get_menu_node_from_string(cand)
                                                if not node2:
                                                    # try fuzzy match against graph keys
                                                    from difflib import get_close_matches
                                                    close = get_close_matches(cand, list(api.graph.menu_node_dict.keys()), n=1, cutoff=0.6)
                                                    if close:
                                                        node2 = api.graph.menu_node_dict.get(close[0])
                                                if node2:
                                                    matched_menu = node2
                                                    is_exact = False
                                                    break
                                    except Exception:
                                        pass
                                # Build candidate list (fuzzy + vectorstore metadata)
                                candidates = []
                                try:
                                    menu_key = api.graph.normalize_string(recipe)
                                    # difflib fuzzy candidates
                                    close = get_close_matches(menu_key, list(api.graph.menu_node_dict.keys()), n=3, cutoff=0.4)
                                    for c in close:
                                        node_label = api.graph.menu_node_dict.get(c)
                                        # compute ratio
                                        ratio = SequenceMatcher(None, menu_key, c).ratio()
                                        candidates.append({'candidate_key': c, 'candidate_label': node_label, 'source': 'fuzzy', 'score': float(ratio)})
                                except Exception:
                                    pass
                                # Add vectorstore metadata candidates
                                try:
                                    docs = vectorstore.similarity_search_with_score(recipe, k=3)
                                    for doc, sc in docs:
                                        meta_name = ''
                                        try:
                                            meta_name = doc.metadata.get('name') if hasattr(doc, 'metadata') else ''
                                        except Exception:
                                            meta_name = ''
                                        if meta_name:
                                            cand_key = api.graph.normalize_string(meta_name)
                                            node2 = api.graph.menu_node_dict.get(cand_key)
                                            candidates.append({'candidate_key': cand_key, 'candidate_label': node2 or meta_name, 'source': 'vector', 'score': float(sc) if sc is not None else 0.0})
                                except Exception:
                                    pass

                                try:
                                    mk = api.graph.normalize_string(matched_menu) if matched_menu else None
                                except Exception:
                                    mk = matched_menu.lower() if matched_menu else None
                                matches.append({
                                    'query': recipe,
                                    'matched_menu': matched_menu,
                                    'matched_key': mk,
                                    'is_exact': is_exact,
                                    'candidates': candidates
                                })
                            except Exception:
                                matches.append({
                                    'query': recipe,
                                    'matched_menu': None,
                                    'is_exact': False
                                })
                except Exception as e:
                    print(f"Error computing matches at upload: {e}")

                # Save for later use by Analyze
                print(f"DEBUG: Saving upload analysis for file={filename}. recipes={parsed_recipes}, matches={matches}", flush=True)
                UPLOAD_ANALYSIS_RESULTS[filename] = {
                    'answer': answer,
                    'recipes': parsed_recipes,
                    'matches': matches
                }
                # Persist analysis results to disk for debugging and offline testing
                try:
                    analysis_path = Path(app.config['UPLOAD_FOLDER']) / 'analysis_results.json'
                    with open(analysis_path, 'w', encoding='utf-8') as af:
                        # Convert to plain serializable structure
                        json.dump(UPLOAD_ANALYSIS_RESULTS, af, ensure_ascii=False, indent=2)
                    print(f"DEBUG: Wrote analysis results to {analysis_path}", flush=True)
                except Exception as e:
                    print(f"DEBUG: Failed to write analysis results to disk: {e}", flush=True)
        
        elif question and answer:
            # Handle follow-up question with existing answer
            followup = ask_openai_over_image_output(answer, question)

        # Customized condition analysis flow
        elif condition:
            # Use saved upload analysis if available for the most recent upload
            try:
                upload_dir = Path(app.config['UPLOAD_FOLDER'])
                uploaded_files = [f for f in upload_dir.iterdir() if f.is_file() and allowed_file(f.name)]
                if uploaded_files:
                    latest_file = max(uploaded_files, key=lambda p: p.stat().st_mtime)
                    filename = latest_file.name
                    saved = UPLOAD_ANALYSIS_RESULTS.get(filename)
                    print(f"DEBUG: Found latest uploaded file: {filename}. saved exists: {bool(saved)}", flush=True)
                    if saved:
                        # restore the extracted image analysis HTML so the UI keeps showing it
                        try:
                            answer = saved.get('answer')
                            print(f"DEBUG: Restored saved answer for {filename} (len={len(answer) if answer else 0})", flush=True)
                        except Exception as e:
                            print(f"DEBUG: Failed to restore saved answer: {e}", flush=True)
                    api = MenuRecommendationAPI()
                    md = f"# Recommendations for {condition}\n\n"

                    # Precompute top menus for disease to fetch scores/ranks
                    try:
                        top_menus = api.get_menus_for_disease(condition, top_n=200, ranking="unhealthy")
                    except Exception:
                        top_menus = []

                    if not saved:
                        # Fallback: run extraction+matching now (should be rare)
                        answer = ask_openai_image(str(latest_file))
                        bullets = re.findall(r'•\s*([^<\n]+)', answer)
                        recipes = [normalize_menu_name(html.unescape(b).strip()) for b in bullets if b and b.strip()]
                        matches = []
                        for recipe in recipes:
                            node = api.graph.get_menu_node_from_string(recipe)
                            if node:
                                try:
                                    matched_key = api.graph.normalize_string(node)
                                except Exception:
                                    matched_key = str(node).strip().lower()
                                matches.append({'query': recipe, 'matched_menu': node, 'matched_key': matched_key, 'is_exact': True})
                            else:
                                best = api.graph.find_best_matched_menu_in_graph(recipe)
                                matched_menu = best.get('matched_menu') if isinstance(best, dict) else None
                                is_exact = best.get('is_exact', False) if isinstance(best, dict) else False
                                # If LLM fallback failed, try vectorstore similarity as a backup
                                if not matched_menu:
                                    try:
                                        docs = vectorstore.similarity_search_with_score(recipe, k=3)
                                        for doc, sc in docs:
                                            meta_name = ''
                                            try:
                                                meta_name = doc.metadata.get('name') if hasattr(doc, 'metadata') else ''
                                            except Exception:
                                                meta_name = ''
                                            if meta_name:
                                                cand = normalize_menu_name(meta_name).lower()
                                                node2 = api.graph.get_menu_node_from_string(cand)
                                                if not node2:
                                                    from difflib import get_close_matches
                                                    close = get_close_matches(cand, list(api.graph.menu_node_dict.keys()), n=1, cutoff=0.6)
                                                    if close:
                                                        node2 = api.graph.menu_node_dict.get(close[0])
                                                if node2:
                                                    matched_menu = node2
                                                    is_exact = False
                                                    break
                                    except Exception:
                                        pass
                                matches.append({'query': recipe, 'matched_menu': matched_menu, 'is_exact': is_exact})
                        print(f"DEBUG: Fallback extraction produced recipes={recipes} and matches={matches}", flush=True)
                    else:
                            recipes = saved.get('recipes', [])
                            matches = saved.get('matches', [])
                            print(f"DEBUG: Using saved recipes={recipes}", flush=True)
                            print(f"DEBUG: Using saved matches={matches}", flush=True)
                            # Apply any user overrides submitted in the form (override_0, override_1, ...)
                            try:
                                for idx, m in enumerate(matches):
                                    key = f'override_{idx}'
                                    if key in request.form:
                                        val = request.form.get(key)
                                        if val:
                                            # If override value corresponds to a normalized key in the graph, use it
                                            node_override = api.graph.menu_node_dict.get(val)
                                            if node_override:
                                                m['matched_menu'] = node_override
                                                m['is_exact'] = False
                                                m['user_override'] = True
                            except Exception as e:
                                print(f"DEBUG: Failed applying overrides: {e}", flush=True)

                    if not recipes:
                        md += "No recipes could be extracted from the image for analysis."
                    else:
                        # Build structured info per recipe so we can sort by severity (very negative first)
                        recipe_infos = []
                        for idx, recipe in enumerate(recipes):
                            info = {"recipe": recipe, "details": None, "breakdown": [], "vneg": 0, "neg": 0}
                            matched = matches[idx] if idx < len(matches) else {'matched_menu': None, 'is_exact': False}
                            matched_menu = matched.get('matched_menu')
                            print(f"DEBUG: Processing recipe='{recipe}' matched_menu={matched_menu} is_exact={matched.get('is_exact', False)}", flush=True)
                            if matched_menu:
                                try:
                                    details = api.get_menu_details(matched_menu, disease=condition)
                                except Exception as e:
                                    print(f"DEBUG: api.get_menu_details failed for matched_menu={matched_menu}: {e}", flush=True)
                                    details = {'error': str(e)}
                                info['matched_closest'] = matched_menu
                                info['is_exact'] = matched.get('is_exact', False)
                            else:
                                try:
                                    details = api.get_menu_details(recipe, disease=condition)
                                except Exception as e:
                                    print(f"DEBUG: api.get_menu_details fallback failed for recipe={recipe}: {e}", flush=True)
                                    details = {'error': str(e)}
                            if isinstance(details, dict) and details.get('error'):
                                info['details'] = details
                                recipe_infos.append(info)
                                continue

                            info['details'] = details
                            breakdown = details.get(f'disease_analysis_{condition}', []) if isinstance(details, dict) else []
                            info['breakdown'] = breakdown
                            info['vneg'] = sum(1 for b in breakdown if b.get('effect','').lower() == 'very negative')
                            info['neg'] = sum(1 for b in breakdown if b.get('effect','').lower() == 'negative')
                            recipe_infos.append(info)

                        # Sort recipes by severity (vneg first, then neg)
                        recipe_infos.sort(key=lambda r: (r['vneg'], r['neg']), reverse=True)

                        # Render recipes with most discouraged at top
                        for info in recipe_infos:
                            recipe = info['recipe']
                            details = info.get('details') or {}
                            md += f"## {recipe}\n\n"
                            if info.get('matched_closest'):
                                md += f"- Closest match in knowledge graph: **{info['matched_closest']}** (exact={info.get('is_exact', False)})\n\n"

                            if isinstance(details, dict) and details.get('error'):
                                md += f"- Not found in knowledge graph: {details.get('error')}\n\n"
                                match = next((m for m in top_menus if m['menu'].lower() == recipe.lower()), None)
                                if match:
                                    md += f"- Matched in ranking: score {match['score']}\n\n"
                                continue

                            # Ingredients
                            ingredients = details.get('ingredients', [])
                            md += f"**Ingredients:** {', '.join(ingredients) if ingredients else 'N/A'}\n\n"

                            # Disease-specific breakdown from knowledge graph
                            breakdown = details.get(f'disease_analysis_{condition}', [])
                            if breakdown:
                                md += "**Knowledge Graph Reasoning:**\n"
                                for b in breakdown:
                                    ingr = b.get('ingredient', '')
                                    eff = b.get('effect', '')
                                    reason = b.get('reason', '')
                                    md += f"- **{ingr}** — {eff}. {reason}\n"
                                md += "\n"
                            else:
                                md += "- No direct ingredient->disease links found in knowledge graph for this menu.\n\n"

                            # Ranking info if available
                            found = next((r for r in top_menus if r['menu'].lower() == details.get('menu','').lower()), None)
                            if found:
                                rank = next((i for i, r in enumerate(top_menus, 1) if r['menu'] == found['menu']), None)
                                md += f"- Knowledge graph score: {found['score']}"
                                if rank:
                                    md += f" (rank {rank} of {len(top_menus)})"
                                md += "\n\n"

                            # Alerts and recommendations
                            vneg = info.get('vneg', 0)
                            neg = info.get('neg', 0)
                            if vneg > 0 or neg > 0:
                                md += f"**ALERT:** This menu contains {vneg} very negative and {neg} negative ingredients for {condition}. Consider requesting modifications (e.g., reduce salt, avoid fried items, remove added sugars).\n\n"
                            else:
                                md += f"**Note:** No strongly negative ingredients detected for {condition}.\n\n"

                    # Robust markdown cleanup: normalize whitespace and collapse blank lines
                    try:
                        # Normalize CRLF and trailing spaces
                        md = md.replace('\r\n', '\n')
                        md = re.sub(r'[ \t]+\n', '\n', md)
                        # Collapse multiple blank lines into a single blank line (one empty line between blocks)
                        md = re.sub(r'\n\s*\n+', '\n\n', md)
                        # Ensure exactly one blank line after headings
                        md = re.sub(r'(#{1,6} .*?)\n\s*\n+', r'\1\n\n', md)
                        # Remove stray blank line immediately before list items
                        md = re.sub(r'\n\s*\n(?=[*-]\s)', '\n', md)
                        # Remove leading/trailing whitespace
                        md = md.strip() + '\n'
                    except Exception:
                        pass

                    # Optional post-processing with gpt5-nano for custom question
                    if customQuestion:
                        try:
                            client = get_openai_client()
                            prompt = f"You are a medical nutritionist. Context:\n{md}\nUser question: {customQuestion}\nProvide a concise answer focusing on actionable recommendations and concise alerts. Return plain text." 
                            resp = client.chat.completions.create(
                                model="gpt5-nano",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.7
                            )
                            post = resp.choices[0].message.content
                            md += "\n---\n### Additional Analysis\n\n" + post
                        except Exception as e:
                            print(f"gpt5-nano post-processing failed: {e}")

                    # Build compact HTML directly (tighter spacing, div blocks)
                    html_parts = [f"<div class=\"rec-root\"><h1>Recommendations for {html.escape(condition)}</h1>"]
                    for info in recipe_infos:
                        recipe = html.escape(info['recipe'])
                        details = info.get('details') or {}
                        html_parts.append(f"<div class=\"rec-recipe\"><div class=\"rec-title\">{recipe}</div>")
                        if info.get('matched_closest'):
                            mc = html.escape(info['matched_closest'])
                            html_parts.append(f"<div class=\"rec-match\">Closest match: <strong>{mc}</strong> (exact={info.get('is_exact', False)})</div>")
                        if isinstance(details, dict) and details.get('error'):
                            html_parts.append(f"<div class=\"rec-error\">Not found in knowledge graph: {html.escape(details.get('error'))}</div>")
                        else:
                            ingredients = details.get('ingredients', [])
                            html_parts.append(f"<div class=\"rec-ingredients\"><strong>Ingredients:</strong> {html.escape(', '.join(ingredients) if ingredients else 'N/A')}</div>")
                            breakdown = details.get(f'disease_analysis_{condition}', [])
                            if breakdown:
                                html_parts.append('<div class=\"rec-breakdown\">')
                                for b in breakdown:
                                    ingr = html.escape(b.get('ingredient',''))
                                    eff = html.escape(b.get('effect',''))
                                    reason = html.escape(b.get('reason',''))
                                    html_parts.append(f"<div class=\"rec-item\"><strong>{ingr}</strong> — {eff}. {reason}</div>")
                                html_parts.append('</div>')
                            else:
                                html_parts.append('<div class=\"rec-breakdown\">No direct ingredient->disease links found.</div>')
                            # Alerts
                            vneg = info.get('vneg', 0)
                            neg = info.get('neg', 0)
                            if vneg > 0 or neg > 0:
                                html_parts.append(f"<div class=\"rec-alert\"><strong>ALERT:</strong> This menu contains {vneg} very negative and {neg} negative ingredients for {html.escape(condition)}.</div>")
                            else:
                                html_parts.append(f"<div class=\"rec-note\">No strongly negative ingredients detected for {html.escape(condition)}.</div>")
                        html_parts.append('</div>')
                    html_parts.append('</div>')
                    recommendation = '\n'.join(html_parts)
                else:
                    recommendation = "<p>No uploaded images found to analyze.</p>"
            except Exception as e:
                print(f"Error during customized analysis: {e}")
                recommendation = f"<p>Error during analysis: {e}</p>"
        
        elif question:
            # If no answer yet, try to find the most recently uploaded image
            try:
                upload_dir = Path(app.config['UPLOAD_FOLDER'])
                uploaded_files = [f for f in upload_dir.iterdir() if f.is_file() and allowed_file(f.name)]
                if uploaded_files:
                    latest_file = max(uploaded_files, key=lambda p: p.stat().st_mtime)
                    filename = latest_file.name
                    answer = ask_openai_image(str(latest_file))
                    if answer:
                        followup = ask_openai_over_image_output(answer, question)
            except Exception as e:
                print(f"Error finding previous upload: {e}")

    # Provide saved matches/recipes to the template so users can override suggested matches
    template_matches = None
    template_recipes = None
    if filename and filename in UPLOAD_ANALYSIS_RESULTS:
        saved = UPLOAD_ANALYSIS_RESULTS.get(filename, {})
        template_matches = saved.get('matches')
        template_recipes = saved.get('recipes')

    return render_template('menu_chat.html',
                         filename=filename,
                         question=question,
                         answer=answer,
                         followup=followup,
                         recommendation=recommendation,
                         matches=template_matches,
                         recipes=template_recipes)


@app.route('/uploads/<filename>')
def uploaded_file(filename: str):
    """
    Serve uploaded files from the uploads directory.
    
    Args:
        filename: Name of the file to serve
        
    Returns:
        File from uploads folder or 404 if not found
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Start Flask development server on localhost:5001
    # debug=False to avoid issues with auto-reloading
    app.run(debug=False, host='127.0.0.1', port=5001)
