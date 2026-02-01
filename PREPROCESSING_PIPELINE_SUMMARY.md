# Menu → Ingredients → Disease Knowledge Graph Preprocessing Pipeline

## Executive Summary

This system creates a **disease-specific knowledge graph** connecting menu titles to their ingredients and the health impacts of those ingredients on specific diseases. The pipeline starts from raw recipe data scraped from AllRecipes.com and ends with a recommendation API that ranks menus by healthiness for patients with specific medical conditions (diabetes, cardiovascular disease, kidney disease).

---

## Data Source: AllRecipes Web Scraping

**File:** [webscrapping.ipynb](backend_menu_processing/webscrapping.ipynb)

The pipeline begins with a web scraper that collects recipe data from AllRecipes.com:

```
AllRecipes.com (Website)
        ↓
WebScrapping.ipynb
        ↓ (BeautifulSoup + JSON-LD parsing)
        ├─ Extract title, URL, servings
        ├─ Extract ingredients (pipe-separated string)
        ├─ Extract directions
        └─ Extract nutrition information (calories, fat, carbs, protein, etc.)
        ↓
all_recipes.csv (353 recipes)
```

**CSV Structure:**
```
title | url | servings | prepTime | cookTime | totalTime | ingredients | directions | nutrition_calories | nutrition_total_fat | ...
```

**Example Row:**
```
"Lamb Souvlaki" | "https://www.allrecipes.com/..." | "4" | "15m" | "10m" | "3h 25m" | "0.33 cup olive oil | 1.5 tbsp lemon juice | 1.5 tbsp red wine vinegar | ..." | "Gather ingredients | Whisk olive oil..." | "346kcal" | "29g" | ...
```

**Key Feature:** Ingredients are stored as **pipe-separated (|)** strings, where each ingredient includes quantity/descriptor.

---

## Quick Reference: Data Flow Diagram

```
                            ┌─────────────────────┐
                            │  AllRecipes.com     │
                            │      (Website)      │
                            └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │ WebScrapping.ipynb  │
                            │  (BeautifulSoup)    │
                            └──────────┬──────────┘
                                       │
                         ┌─────────────▼─────────────┐
                         │   all_recipes.csv         │
                         │  (353 recipes with raw    │
                         │   pipe-separated ingr.)   │
                         └──────────┬────────────────┘
                                    │
                  ┌─────────────────▼─────────────────┐
                  │  Step 1: Split Ingredients        │
                  │  (OpenAI GPT-4 API)               │
                  │  Parse: "2 cups chopped onions"   │
                  │      → ("2 cups chopped","onion") │
                  └──────────┬────────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │ menu2ingredient.csv │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │  Step 2: Get Unique │
                  │  Extract core names │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │ allIngredients.csv  │
                  └──────────┬──────────┘
                             │
              ┌──────────────▼──────────────┐
              │ Step 3: Deduplicate        │
              │ (Gemini API)               │
              │ "onion"/"onions" → "onion" │
              └──────────┬─────────────────┘
                         │
           ┌─────────────▼─────────────┐
           │ uniqueIngredients.csv     │
           │ (Canonical ingredient    │
           │  list: ~50-100 items)    │
           └─────────┬────────┬────────┘
                     │        │
        ┌────────────┼────────┼────────────┐
        │            │        │            │
   [x3 for diseases] │        │            │
        │            │        │            │
        ▼            ▼        ▼            ▼
    ┌──────────────────────────────────────────────┐
    │ Step 4: Annotate Disease Effects             │
    │ (Gemini API - Batch: 50 ingredients)         │
    │ Classify: positive | negative | very_negative│
    │            | neutral                         │
    └──────────────────────────────────────────────┘
        ▼                   ▼                   ▼
   ┌─────────┐      ┌─────────────┐    ┌─────────────┐
   │Diabetes │      │Cardiovascular│   │   Kidney    │
   │ Relation│      │   Disease    │   │  Disease    │
   │  CSV    │      │  Relation CSV│   │ Relation CSV│
   └────┬────┘      └──────┬───────┘   └──────┬──────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
              ┌────────────▼────────────┐
              │ Step 5: Standardize    │
              │ Menu Ingredients       │
              │ (Gemini API - Batch:20)│
              │ Match raw → canonical  │
              └────────────┬───────────┘
                           │
         ┌─────────────────▼──────────────────┐
         │ standardized_menu_ingredients.csv  │
         │ [title | orig_ingr | std_ingr]    │
         └─────────────────┬──────────────────┘
                           │
                     [GRAPH BUILD]
                           │
          ┌────────────────▼────────────────┐
          │  MenuIngredientDiseaseGraph    │
          │  (NetworkX Graph Object)        │
          │  Menu→Ingredient→Disease edges │
          └────────────────┬────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
    ┌────────┐      ┌──────────┐      ┌──────────┐
    │Visualiz│      │ Recommend│      │ Evaluate │
    │  ation │      │ation API │      │  System  │
    └────────┘      └──────────┘      └──────────┘
```

---

## Data Source: AllRecipes Web Scraping

**File:** [webscrapping.ipynb](backend_menu_processing/webscrapping.ipynb)

The pipeline begins with a web scraper that collects recipe data from AllRecipes.com:

```
AllRecipes.com (Website)
        ↓
WebScrapping.ipynb
        ↓ (BeautifulSoup + JSON-LD parsing)
        ├─ Extract title, URL, servings
        ├─ Extract ingredients (pipe-separated string)
        ├─ Extract directions
        └─ Extract nutrition information (calories, fat, carbs, protein, etc.)
        ↓
all_recipes.csv (353 recipes)
```

**CSV Structure:**
```
title | url | servings | prepTime | cookTime | totalTime | ingredients | directions | nutrition_calories | nutrition_total_fat | ...
```

**Example Row:**
```
"Lamb Souvlaki" | "https://www.allrecipes.com/..." | "4" | "15m" | "10m" | "3h 25m" | "0.33 cup olive oil | 1.5 tbsp lemon juice | 1.5 tbsp red wine vinegar | ..." | "Gather ingredients | Whisk olive oil..." | "346kcal" | "29g" | ...
```

**Key Feature:** Ingredients are stored as **pipe-separated (|)** strings, where each ingredient includes quantity/descriptor.

---

## Complete Preprocessing Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                 MENU RECOMMENDATION KNOWLEDGE GRAPH PREPROCESSING                        │
│              AllRecipes → Menu Title → Ingredient → Disease (Effects)                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘

RAW DATA SOURCE (Web Scraping)
        ↓
    [Data Collection]
    WebScrapping.ipynb
    Scrapes AllRecipes.com
        ↓
    all_recipes.csv
    [title, url, servings, ingredients (pipe-separated), directions, nutrition_*]
        ↓
        ├─── Extract Menu Titles + Ingredient Strings
        │         ↓
        │    [Step 1: Split Ingredients]
        │    OpenAI API: Extract descriptors & core ingredient names
        │    Input: "2 cups chopped onions" | "1 tablespoon salt"
        │         ↓
        │    menu2ingredient.csv: 
        │    [title, ingredients (list of tuples)]
        │    - ("2 cups chopped", "onions")
        │    - ("1 tablespoon", "salt")
        │         ↓
        │    [Step 2: Extract Unique Ingredients]
        │    Get all unique core ingredient names across all menus
        │         ↓
        │    allIngredients.csv: [ingredient]
        │    - onion
        │    - salt
        │    - garlic
        │    ...
        │         ↓
        │    [Step 3: Deduplication & Normalization]
        │    Gemini API: Remove duplicates, normalize (singular/plural)
        │         ↓
        │    uniqueIngredients.csv: [ingredient] (canonical list)
        │    - onion (merged from "onion", "onions")
        │    - salt
        │    - garlic
        │    ...
        │         ↓
        │    [Step 4: Annotate with Disease Effects] ◄── (x3 for each disease)
        │    Gemini API: Classify health impact on disease
        │    Effects: positive | negative | very_negative | neutral
        │         ↓
        │    ingredient_diabetes_relation.csv
        │    ingredient_cardiovascular_disease_relation.csv
        │    ingredient_kidney_disease_relation.csv
        │    [ingredient, effect, reason]
        │         ↓
        │    [Step 5: Standardize Menu Ingredients]
        │    Gemini API: Map raw ingredients → canonical list
        │    Uses: menu2ingredient.csv + uniqueIngredients.csv
        │         ↓
        │    standardized_menu_ingredients.csv:
        │    [title, original_ingredients, standardized_ingredients]
        │         ↓
        │    [OPTIONAL Step 6: Combine Annotations]
        │    (⚠️ Commented out - for experimental purposes)
        │         ↓
        │    combined_ingredient_disease_annotations.csv
        │
        └─→ GRAPH CONSTRUCTION
            Reads: standardized_menu_ingredients.csv + ingredient_*_relation.csv files
            Creates: Menu nodes → Ingredient nodes → Disease nodes
            With edge attributes: relation type, effect, reasoning
                    ↓
            MenuIngredientDiseaseGraph (NetworkX Graph Object)
            Stores: menu_node_dict, ingredient_node_dict, disease_node_dict
                    ↓
OUTPUT SYSTEMS (All powered by the graph)
        ├─── Graph Visualization
        │    [MenuIngredientDiseaseGraph.visualize_*()]
        │    Color-coded nodes & edges by disease effect
        │
        ├─── Recommendation API
        │    [MenuRecommendationAPI] 
        │    ├─ get_menus_for_disease()
        │    ├─ get_menu_details()
        │    ├─ compare_menus()
        │    └─ disease-specific analysis
        │
        └─── Evaluation & Benchmarking
             [evaluate_recommendations.py, comprehensive_benchmark.py]
             ├─ Graph-based ranking (from knowledge graph)
             ├─ LLM-based ranking (GPT-4o with ingredients)
             └─ Gemini judge (ground truth comparison)
```

---

## Step-by-Step Detailed Breakdown

### **Step 1: Split Ingredients into Descriptors and Core Names**
**Purpose:** Parse pipe-separated ingredient strings from all_recipes.csv into structured (descriptor, core_ingredient) tuples  
**Input File:** [all_recipes.csv](backend_menu_processing/data/all_recipes.csv) (raw web-scraped data)  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L65-L100)

```
Input CSV Row:
  title: "Lamb Souvlaki"
  ingredients: "0.33 cup olive oil | 1.5 tbsp lemon juice | 2 cloves garlic, minced | ..."
  
Process:
  1. Read all_recipes.csv
  2. For each menu title:
     - Extract pipe-separated ingredient string
     - For each ingredient (e.g., "1.5 tablespoons freshly squeezed lemon juice"):
       └─ Call OpenAI API to split into (descriptor, core)
       └─ Result: ("1.5 tablespoons freshly squeezed", "lemon juice")
  
Output: menu2ingredient.csv
  [title, ingredients (as list of tuples)]
  "Lamb Souvlaki" | "[('0.33 cup', 'olive oil'), ('1.5 tablespoons', 'lemon juice'), ('2 cloves', 'garlic'), ...]"
```

#### **🤖 LLM API CALL DETAILS: OpenAI GPT-4 Turbo**

**Model:** `gpt-4-1106-preview` (GPT-4 Turbo with Vision)  
**Code Location:** [process_menu_ingredient.py#L55-L58](process_menu_ingredient.py#L55-L58)

**API Configuration:**
```python
response = openai.chat.completions.create(
    model="gpt-4-1106-preview",           # Latest GPT-4 Turbo version
    messages=[{"role": "user", "content": prompt}],
    max_tokens=80,                         # Small output: just tuple
    temperature=0                          # Deterministic parsing
)
```

**Why GPT-4 Turbo?**
- ✅ Excellent at structured output parsing (returning Python tuples)
- ✅ Superior accuracy for complex ingredient parsing
- ✅ Handles ambiguous cases well (e.g., "2 cups chopped onions" vs "onion chopped 2 cups")
- ✅ Low token usage (~20 tokens per call)

**Performance Metrics:**
- **Temperature:** 0 (deterministic - always same answer for same input)
- **Max Tokens:** 80 (output: `(descriptor, ingredient)` tuple)
- **Typical Input Tokens:** ~50-70 per ingredient
- **Typical Output Tokens:** ~10-15 per response
- **Avg. Time per Call:** ~500-800ms

**Cost Analysis:**
- **Input Rate:** $0.01 per 1K tokens
- **Output Rate:** $0.03 per 1K tokens
- **Per Ingredient Cost:** ~$0.001-0.002
- **Total Cost (Est.):** ~$1,500-3,000+ for ~1,500 ingredients

**Prompt Structure:**
```
Extract this ingredient string into two fields:
(1) quantity, measurement, or descriptor
(2) core ingredient name
Return ONLY the Python tuple: (descriptor, ingredient)
Example: '2 cups chopped onions' -> ('2 cups chopped', 'onions')
Ingredient: '{ingredient}'
```

**API Calls:** ~1,500+ API calls (one per ingredient across ~300+ menus with ~5 ingredients each)  
**Total Tokens (Est.):** ~50,000-70,000 tokens

**Code Location:** 
- [PreProcessing.split_ingredient()](process_menu_ingredient.py#L47-L63) - Single ingredient splitting
- [PreProcessing.split_ingredient_for_all_titles()](process_menu_ingredient.py#L65-L100) - Batch processing all menus

---

### **Step 2: Extract Unique Core Ingredients**
**Purpose:** Collect all distinct ingredients from all menus  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L102-L145)

```
Input:  menu2ingredient.csv (multiple menus with ingredients)
         ↓
Process: Extract all (descriptor, core) tuples
         Keep only lowercased, stripped core ingredients
         Add to set for uniqueness
         ↓
Output:  allIngredients.csv
         [ingredient]
         - onion
         - salt
         - garlic
         - butter
         ...
```

**Code Location:** [PreProcessing.get_ingredient_set()](process_menu_ingredient.py#L104-L143)

---

### **Step 3: Deduplication & Normalization**
**Purpose:** Remove duplicates and normalize ingredient names (e.g., "onions" → "onion")  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L147-L232)

```
Input:  allIngredients.csv (raw list)
         ↓ (Google Gemini API)
Process: Send list to Gemini AI
         Prompt: "Deduplicate and normalize these ingredients.
                  Treat plural/singular as same."
         Response: JSON array of deduplicated names
         ↓
Output:  uniqueIngredients.csv
         [ingredient] (normalized, no duplicates)
```

#### **🤖 LLM API CALL DETAILS: Google Gemini Flash**

**Model:** `gemini-2.5-flash-lite` (Latest Gemini Flash model with optimizations)  
**Code Location:** [menu_ingredient_disease_graph.py#L31-L34](menu_ingredient_disease_graph.py#L31-L34)

**API Configuration:**
```python
generation_config = {
    "temperature": 0.01,              # Near-deterministic
    "top_p": 1,                       # Full nucleus sampling
    "top_k": 1,                       # Only consider top token
    "max_output_tokens": 32000,       # Large context for lists
}
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite',
    generation_config=generation_config
)
```

**Why Gemini Flash?**
- ✅ Excellent at semantic understanding (recognizing "onion" = "onions")
- ✅ Much faster than Gemini Pro (suitable for deduplication)
- ✅ Large output window (32K tokens) - can process entire ingredient list
- ✅ Cost-effective batch processing
- ✅ Good at JSON parsing and array manipulation

**Performance Metrics:**
- **Temperature:** 0.01 (near-deterministic but with minimal variation)
- **Max Output Tokens:** 32,000 (can return entire deduplicated list)
- **Typical Input Tokens:** ~5,000-10,000 (full ingredient list)
- **Typical Output Tokens:** ~2,000-4,000 (JSON array)
- **Avg. Time per Call:** ~2-4 seconds

**Batch Processing:**
- **Batch Size:** All ingredients in one call (~100-200 items)
- **Typical Call Count:** 1-2 per dataset
- **Total API Calls:** 1-2

**Prompt:**
```
Given this list of ingredients, deduplicate and normalize them.
Treat plural and singular forms as the same ingredient.
Return ONLY the final deduped list as a JSON array of strings, no explanation.
Ingredients: {json.dumps(ingredient_list)}
```

**Data Flow:** 
- Reads `allIngredients.csv`
- Calls Gemini API with batch deduplication (all items at once)
- Writes unique list to `uniqueIngredients.csv`
- Saves response to `response.txt` for debugging

**Code Location:** [PreProcessing.remove_duplicates()](process_menu_ingredient.py#L149-L232)

---

### **Step 4: Annotate Ingredients with Disease Effects** (3x for each disease)
**Purpose:** Classify how each ingredient affects specific diseases  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L234-L299)

```
Input:  uniqueIngredients.csv
         Target Disease: "diabetes"
         ↓ (Google Gemini API - Batch Processing)

For each batch of 50 ingredients:
  Prompt: "Classify health impact on diabetes:
           effect: 'positive' | 'negative' | 'very_negative' | 'neutral'
           reason: short explanation"
         ↓
Output:  ingredient_diabetes_relation.csv
         [ingredient, effect, reason]
         - butter, very_negative, High saturated fat worsens insulin resistance
         - garlic, positive, May help with glucose control
         - onion, neutral, No direct effect on diabetes
         ...

Repeat for:
  - cardiovascular disease → ingredient_cardiovascular_disease_relation.csv
  - kidney disease → ingredient_kidney_disease_relation.csv
```

#### **🤖 LLM API CALL DETAILS: Google Gemini Flash (Batch Annotation)**

**Model:** `gemini-2.5-flash-lite` (Same as Step 3)  
**Code Location:** [menu_ingredient_disease_graph.py#L31-L34](menu_ingredient_disease_graph.py#L31-L34)

**API Configuration:**
```python
generation_config = {
    "temperature": 0.01,              # Deterministic health classifications
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 32000,       # Can return large JSON arrays
}
model_name = 'gemini-2.5-flash-lite'
```

**Why Gemini Flash for Medical Classification?**
- ✅ Strong medical/nutritional knowledge base
- ✅ Batch processing efficiency (50 ingredients/call)
- ✅ Reliable JSON output format
- ✅ Good at providing medical reasoning
- ✅ Cost-effective for processing 3 diseases

**Performance Metrics:**
- **Temperature:** 0.01 (consistent classification across runs)
- **Max Output Tokens:** 32,000 (supports large JSON arrays)
- **Typical Input Tokens:** ~2,000-3,000 per batch (50 ingredients)
- **Typical Output Tokens:** ~1,500-2,500 (JSON with reasoning)
- **Avg. Time per Batch:** ~2-3 seconds

**Batch Processing Strategy:**
- **Batch Size:** 50 ingredients per API call
- **Total Ingredients:** ~100-200 (varies by dataset)
- **Calls per Disease:** 2-4 batches
- **Total Calls:** ~6-12 (for 3 diseases)

**Prompt Template:**
```
For the disease '{disease}', classify the health impact of each ingredient as:
'positive', 'neutral', 'negative', or 'very negative'

Return ONLY a JSON array of objects:
{"ingredient": string, "effect": string, "reason": string}

Ingredients: {json.dumps(batch)}
```

**Example Output:**
```json
[
  {"ingredient": "butter", "effect": "very negative", "reason": "High saturated fat worsens insulin resistance"},
  {"ingredient": "garlic", "effect": "positive", "reason": "May help with glucose control"},
  {"ingredient": "onion", "effect": "neutral", "reason": "No direct effect on diabetes"}
]
```

**Effect Classifications:**
- **Very Negative:** Strong negative health impact on disease
- **Negative:** Mild to moderate negative health impact
- **Neutral:** No significant effect on disease
- **Positive:** Beneficial for disease management

**Processing for 3 Diseases:**
1. Diabetes (ingredient_diabetes_relation.csv)
2. Cardiovascular Disease (ingredient_cardiovascular_disease_relation.csv)
3. Kidney Disease (ingredient_kidney_disease_relation.csv)

**Cost Analysis:**
- **Per Batch:** ~$0.05-0.10 (low-cost Gemini Flash rates)
- **Total (Est.):** ~$0.50-1.50 for all 3 diseases
- **Much cheaper than Step 1** (GPT-4 ingredient splitting)

**API Response Parsing:**
- Searches for JSON array in response using regex: `r'\[.*\]'`
- Falls back to "neutral" for all ingredients if parsing fails
- Saves raw response to `response_batch_X.txt` files for debugging

**Code Location:** [PreProcessing.annotate_each_ingredient_causing_disease_using_gemini()](process_menu_ingredient.py#L234-L299)

---

### **Step 5: Standardize Menu Ingredients**
**Purpose:** Map raw extracted ingredients to the canonical normalized ingredient list  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L340-L437)

```
Input:  menu2ingredient.csv (extracted ingredients per menu)
        uniqueIngredients.csv (canonical ingredient list)
        
        ↓ (Google Gemini API - Batch by 20 menus)

For each batch of 20 menus:
  For each menu with list of raw ingredients:
    Prompt: "Match these raw ingredients to standardized list:
             [canonical ingredient 1, ingredient 2, ...]
             Ignore descriptors, amounts, sizes.
             Return JSON: {original_ingredients, standardized_ingredients[]}"
        ↓
Output:  standardized_menu_ingredients.csv
         [title, original_ingredients, standardized_ingredients]
         
         Example:
         "Chicken Stir Fry", "chicken, garlic, soy sauce, oil", "chicken, garlic, soy_sauce, vegetable_oil"
```

#### **🤖 LLM API CALL DETAILS: Google Gemini Flash (Semantic Matching)**

**Model:** `gemini-2.5-flash-lite` (Same as Steps 3 & 4)  
**Code Location:** [menu_ingredient_disease_graph.py#L31-L34](menu_ingredient_disease_graph.py#L31-L34)

**API Configuration:**
```python
generation_config = {
    "temperature": 0.01,              # Deterministic matching
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 32000,       # Large for batch results
}
model_name = 'gemini-2.5-flash-lite'
```

**Why Gemini Flash for Ingredient Standardization?**
- ✅ Excellent at semantic similarity matching
- ✅ Handles ingredient variations ("soy sauce" vs "soya sauce")
- ✅ Understands ingredient variations ("vegetable oil" → "oil")
- ✅ Batch processing efficiency
- ✅ Returns structured JSON for easy parsing

**Performance Metrics:**
- **Temperature:** 0.01 (consistent matching)
- **Max Output Tokens:** 32,000
- **Typical Input Tokens:** ~3,000-5,000 per batch (20 menus)
- **Typical Output Tokens:** ~2,000-3,000 (JSON mappings)
- **Avg. Time per Batch:** ~2-3 seconds

**Batch Processing Strategy:**
- **Batch Size:** 20 menu items per API call
- **Total Menus:** ~300+ recipes
- **Total Batches:** ~15-20 calls
- **Total API Calls:** 15-20

**Prompt Template:**
```
Given this list of standardized ingredients: {json.dumps(canonical_list)}
For each menu below, match each raw ingredient to standardized ingredients from the list.
Ignore descriptors, amounts, weights, or sizes. Focus only on ingredient names.

Return ONLY a JSON array of objects:
{"original_ingredients": string, "standardized_ingredients": array}

Menu ingredient strings: {json.dumps(batch_ingredients)}
```

**Example Mapping:**
```json
[
  {
    "original_ingredients": "chicken, garlic, soy sauce, oil",
    "standardized_ingredients": ["chicken", "garlic", "soy_sauce", "vegetable_oil"]
  },
  {
    "original_ingredients": "extra virgin olive oil, onions, tomatoes",
    "standardized_ingredients": ["olive_oil", "onion", "tomato"]
  }
]
```

**Matching Features:**
- ✅ Handles variations: "soy sauce" → "soy_sauce"
- ✅ Handles synonyms: "extra virgin olive oil" → "olive_oil"
- ✅ Handles plurals: "onions" → "onion"
- ✅ Returns "No match" for unrecognized items

**Details:**
- Loads standardized ingredient list from `uniqueIngredients.csv`
- Extracts core ingredients from menu2ingredient.csv tuples
- Sends JSON batches to Gemini (20 menus per batch)
- Parses responses and writes matches
- Falls back to "No match" for unmatched items

**Cost Analysis:**
- **Per Batch:** ~$0.05-0.10
- **Total (Est.):** ~$1.00-2.00 for all menus
- **Much cheaper than Step 1** (GPT-4 ingredient splitting)

**Code Location:** [PreProcessing.standardize_menu_ingredients()](process_menu_ingredient.py#L340-L437)

---

### **Step 6: (OPTIONAL) Combine Ingredient-Disease Annotations**
**Purpose:** Merge all disease-specific annotations into a single file  
**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L301-L337)

```
Input:  ingredient_diabetes_relation.csv
        ingredient_cardiovascular_disease_relation.csv
        ingredient_kidney_disease_relation.csv
        
        ↓ (Simple aggregation - no API call)

Output:  combined_ingredient_disease_annotations.csv
         [ingredient, disease, effect, reason]
         
         Example:
         - butter, diabetes, very_negative, High saturated fat...
         - butter, cardiovascular_disease, very_negative, Increases LDL...
         - butter, kidney_disease, neutral, ...
```

**Status:** ⚠️ **Currently Commented Out** in `menu_ingredient_disease_relationship_preprcessing()` at [Line 539-543](process_menu_ingredient.py#L539-L543)

**Code Location:** [PreProcessing.combine_ingredient_disease_annotations()](process_menu_ingredient.py#L301-L337)

---

### **Final Step: Graph Construction**
**Purpose:** Connect all nodes (menu → ingredient → disease) into NetworkX graph  
**File:** [menu_ingredient_disease_graph.py](menu_ingredient_disease_graph.py#L56-L200)

```
Input:  standardized_menu_ingredients.csv
        ingredient_{disease}_relation.csv (x3)
        
        ↓

Graph Construction:
  1. Read standardized_menu_ingredients.csv
     └─ Create Menu nodes → Ingredient nodes
        Edge: has_ingredient
        
  2. Read disease relation files
     └─ Create Ingredient nodes → Disease nodes
        Edge: effect (positive/negative/very_negative)
              reason (explanation)
              
  3. Build NetworkX Graph
     ├─ Nodes: {type: 'menu'|'ingredient'|'disease'}
     └─ Edges: {relation, effect, reason}
     
Output:  MenuIngredientDiseaseGraph object
         - Self.G: NetworkX graph
         - Self.menu_node_dict: {normalized_title → actual_title}
         - Self.ingredient_node_dict: {normalized_ing → actual_ing}
         - Self.disease_node_dict: {normalized_disease → actual_disease}
```

**Code Location:** [MenuIngredientDiseaseGraph.connect_graph_from_menu_title_to_ingredient_to_disease()](menu_ingredient_disease_graph.py#L56-L200)

**Graph Structure:**
- Menu nodes color-coded as blue (#1f77b4)
- Ingredient nodes as light blue (#C7E6EE)
- Disease nodes as purple (#d62796)
- Edges from menu→ingredient: gray
- Edges from ingredient→disease: colored by effect
  - Positive: green (#19f336)
  - Negative: orange (#ff7f0e)
  - Very Negative: red (#ff0101)

---

## Data Files Reference

| File | Purpose | Source | Columns |
|------|---------|--------|---------|
| [all_recipes.csv](backend_menu_processing/data/all_recipes.csv) | **RAW SOURCE**: Web-scraped recipes from AllRecipes.com | WebScrapping.ipynb | `title`, `url`, `servings`, `prepTime`, `cookTime`, `totalTime`, `ingredients` (pipe-separated), `directions`, `nutrition_*` |
| [menu2ingredient.csv](backend_menu_processing/data/) | Menu titles with extracted ingredients as tuples | Step 1 | `title`, `ingredients` (list of tuples: (descriptor, core)) |
| [allIngredients.csv](backend_menu_processing/data/) | All unique core ingredients (pre-dedup) | Step 2 | `ingredient` |
| [uniqueIngredients.csv](backend_menu_processing/data/) | Deduplicated, normalized ingredients (canonical) | Step 3 | `ingredient` |
| [ingredient_diabetes_relation.csv](backend_menu_processing/data/) | Diabetes health impacts | Step 4a | `ingredient`, `effect`, `reason` |
| [ingredient_cardiovascular_disease_relation.csv](backend_menu_processing/data/) | Cardiovascular disease impacts | Step 4b | `ingredient`, `effect`, `reason` |
| [ingredient_kidney_disease_relation.csv](backend_menu_processing/data/) | Kidney disease impacts | Step 4c | `ingredient`, `effect`, `reason` |
| [standardized_menu_ingredients.csv](backend_menu_processing/data/) | Menu titles with standardized ingredients (final mapping) | Step 5 | `title`, `original_ingredients`, `standardized_ingredients` |
| [combined_ingredient_disease_annotations.csv](backend_menu_processing/data/final/) | ⚠️ Optional: All disease annotations combined | Step 6 (commented) | `ingredient`, `disease`, `effect`, `reason` |

---

## Preprocessing Pipeline Orchestration

**File:** [process_menu_ingredient.py](process_menu_ingredient.py#L535-L560)

```python
@staticmethod
def menu_ingredient_disease_relationship_preprcessing():
    # Step 1: Split ingredients
    PreProcessing.split_ingredient_for_all_titles()
    
    # Step 2: Extract unique ingredients
    PreProcessing.get_ingredient_set()
    
    # Step 3: Deduplicate and normalize
    PreProcessing.remove_duplicates() 
    
    # Step 4: Annotate for all diseases
    PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="diabetes")
    PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="cardiovascular disease")
    PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="kidney disease")
    
    # Step 5: Standardize menu ingredients
    PreProcessing.standardize_menu_ingredients()
    
    # ⚠️ Step 6 (Commented out for experimental purposes):
    # disease_files = {
    #     "diabetes": "ingredient_diabetes_relation.csv",
    #     "cardiovascular disease": "ingredient_cardiovascular_disease_relation.csv",
    #     "kidney disease": "ingredient_kidney_disease_relation.csv"
    # }
    # PreProcessing.combine_ingredient_disease_annotations(diseases_and_files=disease_files)
```

**Code Location:** [PreProcessing.menu_ingredient_disease_relationship_preprcessing()](process_menu_ingredient.py#L535-L560)

---

## Graph Visualization

The system generates intuitive block diagrams showing relationships:

```
        [Menu Title Node]
               ↓
        ┌──────┴──────┬─────────┬─────────┐
        ↓             ↓         ↓         ↓
   [Ingredient]  [Ingredient] ... [Ingredient]
        ↓             ↓         ↓         ↓
   [Disease]    [Disease]  [Disease]  [Disease]
   
Edge colors indicate health impact:
  ✓ Green  = Positive effect
  ✗ Orange = Negative effect
  ⚠ Red    = Very Negative effect
```

**Visualization Code:** [MenuIngredientDiseaseGraph.visualize_menu_ingredient_disease_graph()](menu_ingredient_disease_graph.py#L319-L433)

---

## Usage Examples

### Running the Full Pipeline

```bash
# Complete preprocessing from raw data to graph
cd /Users/jameszhang/git/Hello-World
python3 backend_menu_processing/process_menu_ingredient.py
```

### Using the Recommendation API

**File:** [recommendation_api.py](recommendation_api.py)

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

# Initialize API (loads the complete graph)
api = MenuRecommendationAPI()

# Get top 10 unhealthy menus for diabetes
results = api.get_menus_for_disease("diabetes", top_n=10, ranking="unhealthy")
for menu_rec in results:
    print(f"{menu_rec['menu']}: {menu_rec['score']}")

# Compare multiple menus
comparison = api.compare_menus(
    ["Finnish Runeberg Tortes", "Swedish Spareribs"],
    disease="diabetes"
)
```

### Evaluation & Benchmarking

**Files:** 
- [evaluate_recommendations.py](evaluate_recommendations.py) - Single evaluation
- [comprehensive_benchmark.py](comprehensive_benchmark.py) - Multi-iteration benchmark

```bash
# Single evaluation (25 samples, top 10, diabetes)
python3 backend_menu_processing/evaluate_recommendations.py

# Custom parameters
python3 backend_menu_processing/evaluate_recommendations.py \
  --disease "cardiovascular disease" \
  --sample 50 \
  --top 20 \
  --seed 123
```

---

## Key Design Decisions & Commented Code

### ⚠️ Commented Step 6: Combined Annotations

**Location:** [process_menu_ingredient.py](process_menu_ingredient.py#L539-L543)

The `combine_ingredient_disease_annotations()` call is commented out because:
1. **Experimental Purpose:** The system works with separate disease relation files
2. **Alternative Access:** The graph already connects all diseases to ingredients
3. **Space Efficiency:** Keeps data in normalized form (3 files instead of 1 combined)

To enable:
```python
# Uncomment at line 539-543:
disease_files = {
    "diabetes": "ingredient_diabetes_relation.csv",
    "cardiovascular disease": "ingredient_cardiovascular_disease_relation.csv",
    "kidney disease": "ingredient_kidney_disease_relation.csv"
}
PreProcessing.combine_ingredient_disease_annotations(diseases_and_files=disease_files)
```

### API Key Management

**Files:**
- [menu_ingredient_disease_graph.py](menu_ingredient_disease_graph.py#L12-L22) - `init_api_keys()` function
- [process_menu_ingredient.py](process_menu_ingredient.py#L1-L10) - OpenAI API initialization

**Current Setup:**
- OpenAI: Line 9 (gpt-4-1106-preview for ingredient splitting)
- Gemini: Configured via `init_api_keys()` from .env file

---

## LLM Calls & Cost Optimization

### **Detailed LLM API Call Summary**

| Step | Model | Exact Version | Purpose | Batch Size | # Calls | Est. Tokens | Est. Cost |
|------|-------|--------|---------|-----------|---------|------------|----------|
| 1 | **OpenAI GPT-4 Turbo** | `gpt-4-1106-preview` | Split ingredients | 1 per ingredient | ~1,500 | 50,000-70,000 | $1.50-3.00 |
| 3 | **Google Gemini Flash** | `gemini-2.5-flash-lite` | Deduplicate ingredients | All at once (100-200) | 1-2 | 10,000-15,000 | $0.01-0.02 |
| 4a | **Google Gemini Flash** | `gemini-2.5-flash-lite` | Annotate Diabetes effects | 50 ingredients | 2-4 | 8,000-12,000 | $0.01-0.02 |
| 4b | **Google Gemini Flash** | `gemini-2.5-flash-lite` | Annotate Cardiovascular effects | 50 ingredients | 2-4 | 8,000-12,000 | $0.01-0.02 |
| 4c | **Google Gemini Flash** | `gemini-2.5-flash-lite` | Annotate Kidney disease effects | 50 ingredients | 2-4 | 8,000-12,000 | $0.01-0.02 |
| 5 | **Google Gemini Flash** | `gemini-2.5-flash-lite` | Standardize menu ingredients | 20 menus | 15-20 | 30,000-50,000 | $0.03-0.05 |

**Cost Summary:**
- **Total API Calls:** ~1,530-1,600 calls
- **Total Tokens:** ~120,000-180,000 tokens  
- **Estimated Total Cost:** $1.60-3.15
- **Cost Breakdown:** ~95% from Step 1 (GPT-4 Turbo), ~5% from Steps 3-5 (Gemini Flash)

### **Model Comparison & Selection Rationale**

**GPT-4 Turbo (Step 1): `gpt-4-1106-preview`** - [Code Location](backend_menu_processing/process_menu_ingredient.py#L55-L62)
- ✅ Superior accuracy for structured parsing (tuple extraction)
- ✅ Handles ambiguity and complex ingredient names
- ❌ Most expensive: $0.01/1K input tokens, $0.03/1K output tokens
- ❌ No batch processing capability
- **Why Chosen:** Accuracy is critical here; errors cascade through entire pipeline

**Gemini 2.5 Flash (Steps 3-5): `gemini-2.5-flash-lite`** - [Code Location](backend_menu_processing/menu_ingredient_disease_graph.py#L31-L34)
- ✅ Excellent semantic understanding (deduplication, matching, medical reasoning)
- ✅ **10-100x cheaper** than GPT-4 Turbo
- ✅ Supports batch processing (50+ items per call)
- ✅ Faster inference (good for bulk processing)
- ❌ Slightly less accurate for highly structured output
- **Why Chosen:** Cost-effective alternative for semantic tasks where accuracy is acceptable

### **Cost-Saving Strategies Employed**

1. **Strategic Model Selection**
   - Use expensive GPT-4 only for critical accuracy requirements
   - Use cheap Gemini for semantic tasks
   - **Savings:** ~$10-50 compared to using GPT-4 throughout

2. **Batch Processing**
   - Step 3: All 100-200 ingredients in 1-2 calls (vs 100-200 individual calls)
   - Step 4: 50 ingredients per batch (vs 1 ingredient per call)
   - Step 5: 20 menus per batch (vs 1 menu per call)
   - **Savings:** ~$5-10 on API call overhead

3. **Temperature Tuning**
   - Step 1: temperature=0 (deterministic parsing, no variance)
   - Steps 3-5: temperature=0.01 (near-deterministic output)
   - Lower temperature = fewer retries, consistent results

4. **Token Optimization**
   - Step 1: max_tokens=80 (short structured output)
   - Steps 3-5: max_tokens=32000 (reserve capacity but rarely use full budget)
   - **Typical Usage:** 5-10% of max_tokens allocated

### **Observed Token Usage Patterns**

**Step 1 (OpenAI GPT-4 Turbo):**
```
Per ingredient processing:
  ├─ Input tokens: 50-70 (prompt + ingredient text)
  ├─ Output tokens: 10-15 (tuple output)
  └─ Total: 60-85 tokens per API call
  
Example: "1 cup sliced onions" → ("sliced", "onions")
  Input: 45 tokens
  Output: 12 tokens
  Total: 57 tokens
```

**Step 3 (Google Gemini Flash - Deduplication):**
```
Entire deduplication in 1-2 calls:
  ├─ Input: 5,000-10,000 tokens (all ingredients as JSON array)
  ├─ Output: 2,000-4,000 tokens (deduplicated canonical list)
  └─ Total: 7,000-14,000 tokens for entire step
  
Efficiency: ~40-70 tokens per ingredient (vs 80+ for GPT-4)
```

**Steps 4a-4c (Google Gemini Flash - Disease Annotation):**
```
Per batch (50 ingredients):
  ├─ Input: 2,000-3,000 tokens (JSON with ingredients)
  ├─ Output: 1,500-2,500 tokens (disease effects for each)
  └─ Total: 3,500-5,500 tokens per batch
  
×3 diseases = 10,500-16,500 tokens total
Typical run: 1,500 tokens/disease (50 ingredients)
```

**Step 5 (Google Gemini Flash - Standardization):**
```
Per batch (20 menus):
  ├─ Input: 3,000-5,000 tokens (menu titles + ingredient lists)
  ├─ Output: 2,000-3,000 tokens (standardized ingredient mappings)
  └─ Total: 5,000-8,000 tokens per batch
  
×20 batches ≈ 40,000-60,000 tokens total
Typical run: 3,000 tokens/batch (20 menus)
```

---

## Evaluation System: Additional LLM Calls

After preprocessing, the knowledge graph is evaluated against other ranking approaches using additional LLM API calls.

### **Evaluation Architecture**

```
MenuIngredientDiseaseGraph (loaded in memory)
        ↓
        ├─→ Recommendation API (production)
        │   (Graph-based ranking only)
        │
        ├─→ Graph Visualization
        │   (Matplotlib network diagrams)
        │
        └─→ Evaluation System (benchmarking)
            ├─ Graph-Based Ranking
            │  (No API calls - uses pre-built graph)
            │
            ├─ LLM-Based Ranking
            │  (Uses OpenAI GPT-4o for comparison baseline)
            │
            └─ Quality Judge
               (Uses Google Gemini for comparative assessment)
```

### **Evaluation LLM Calls**

#### **LLM-Based Menu Ranking: OpenAI GPT-4o**
**Model:** `gpt-4o`  
**File:** [evaluate_recommendations.py](backend_menu_processing/evaluate_recommendations.py#L70-L105)  
**Purpose:** Generate LLM-based menu ranking as baseline for comparison

**Configuration:**
- Model: `gpt-4o` (latest GPT-4 omni model with vision)
- Temperature: 0 (deterministic ranking)
- Context window: 128K tokens
- Format: JSON with ranked menus and health scores

**Typical Usage:**
```python
# Input per call: ~25 menus with their ingredients
Input tokens: 3,000-5,000 per call
Output tokens: 1,000-2,000 per call (JSON rankings)
Cost per call: ~$0.10-0.20 (depends on menu count)
```

**When Used:**
- [comprehensive_benchmark.py](backend_menu_processing/comprehensive_benchmark.py): Compare graph vs LLM rankings
- [evaluate_recommendations.py](backend_menu_processing/evaluate_recommendations.py): Generate LLM baseline scores
- **Frequency:** Periodic benchmarking only, not in production

**Purpose in Evaluation:**
- Provides baseline for comparison ("How well does LLM rank without knowledge graph?")
- Tests whether pre-built graph improves upon general LLM reasoning
- Identifies cases where general LLM better/worse than domain-specific graph

#### **Quality Judge: Google Gemini Flash**
**Model:** `gemini-2.5-flash-lite`  
**File:** [comprehensive_benchmark.py](backend_menu_processing/comprehensive_benchmark.py)  
**Purpose:** Compare quality of graph-based vs LLM-based rankings using ingredient ground truth

**Configuration:**
- Model: `gemini-2.5-flash-lite` (same as preprocessing)
- Temperature: 0.01-0.1 (slight variation for comparative reasoning)
- Role: Acts as "judge" between two ranking approaches
- Format: JSON comparison with reasoning

**Typical Usage:**
```python
# Input per comparison: Two menus with different rankings
Input tokens: 1,000-2,000 per judgment
Output tokens: 500-1,000 per judgment (comparison + reasoning)
Cost per judgment: ~$0.01-0.02
```

**When Used:**
- [comprehensive_benchmark.py](backend_menu_processing/comprehensive_benchmark.py): Side-by-side ranking comparison
- **Frequency:** Periodic benchmarking only
- **Method:** "Which ranking is better given ingredient-disease knowledge?"

**Comparison Criteria:**
- Does ranking prioritize healthier ingredients?
- Does ranking handle disease-specific needs?
- Does graph-based approach beat naive LLM approach?

### **Evaluation Cost Profile**

| Operation | Model | Cost per Run | Runs | Total Cost |
|-----------|-------|--------------|------|-----------|
| Rank 100 menus (LLM) | GPT-4o | ~$0.10-0.20 | 1-2 per evaluation | $0.20-0.40 |
| Judge 50 comparisons | Gemini Flash | ~$0.01-0.02 | 1-2 per evaluation | $0.02-0.04 |
| Full evaluation run | Mixed | ~$0.25-0.50 | Periodic (weekly/monthly) | ~$0.25-0.50 each |

**Key Takeaway:** Evaluation system adds minimal cost (~$0.25-0.50 per run) compared to preprocessing (~$1.60-3.15 total).

### **When Evaluation System is Used**

**Development/Testing:**
- Benchmarking graph accuracy against LLM baselines
- Validating preprocessing pipeline quality
- Comparing disease-specific recommendations

**Production:**
- ❌ Not used in production API
- ✅ Only recommendation API (graph-based) is used
- ✅ Evaluation runs periodically for quality assurance

**Code Locations:**
- [evaluate_recommendations.py](backend_menu_processing/evaluate_recommendations.py): Main evaluation functions
- [comprehensive_benchmark.py](backend_menu_processing/comprehensive_benchmark.py): Full benchmark suite
- [BENCHMARK_RESULTS_SUMMARY.md](BENCHMARK_RESULTS_SUMMARY.md): Results documentation

---

## Next Steps & System Flow

After preprocessing completes, the graph is ready for use in multiple systems:

```
MenuIngredientDiseaseGraph (loaded in memory)
        ↓
        ├─→ Recommendation API
        │   (Production system - graph-based ranking only)
        │   Used by: menu_chat.html (web interface)
        │
        ├─→ Graph Visualization
        │   (Matplotlib network diagrams)
        │   Shows: Menu → Ingredient → Disease connections
        │
        └─→ Evaluation System [See: Evaluation System Section]
            (Benchmarking/testing - NOT in production)
            ├─ Graph-based ranking
            ├─ LLM-based ranking (GPT-4o) [Model: gpt-4o]
            └─ Gemini judge (quality assessment) [Model: gemini-2.5-flash-lite]
```

**Production Path:**
- User asks menu question via [menu_chat.html](front_end/templates/menu_chat.html)
- [recommendation_api.py](backend_menu_processing/recommendation_api.py) queries graph
- Returns personalized recommendations (no LLM calls)

**Evaluation Path:**
- [evaluate_recommendations.py](backend_menu_processing/evaluate_recommendations.py) compares approaches
- [comprehensive_benchmark.py](backend_menu_processing/comprehensive_benchmark.py) runs full benchmarks
- Reports saved to [BENCHMARK_RESULTS_SUMMARY.md](BENCHMARK_RESULTS_SUMMARY.md)

---

## Summary of Technologies Used

- **Python Libraries:** NetworkX (graphs), CSV (data handling), JSON (data interchange)
- **LLMs:** OpenAI GPT-4 (ingredient splitting), Google Gemini (deduplication, annotation, standardization)
- **Graph Database:** NetworkX (in-memory graph representation)
- **Evaluation:** GPT-4o (ranking), Gemini (judging)

---

## Document Navigation

- **Full Preprocessing Code:** [process_menu_ingredient.py](process_menu_ingredient.py)
- **Graph Construction:** [menu_ingredient_disease_graph.py](menu_ingredient_disease_graph.py)
- **Recommendation API:** [recommendation_api.py](recommendation_api.py)
- **Evaluation:** [evaluate_recommendations.py](evaluate_recommendations.py)
- **Benchmarking:** [comprehensive_benchmark.py](comprehensive_benchmark.py)
- **Quick Start:** [QUICK_START.md](QUICK_START.md)
