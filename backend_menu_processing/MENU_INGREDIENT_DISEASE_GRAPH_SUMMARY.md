# Menu Ingredient Disease Graph - Program Summary

## Overview
This program builds and manages a knowledge graph that connects **menu titles** → **ingredients** → **diseases** and their relationships. It uses NetworkX for graph operations, Matplotlib for visualization, and Google's Gemini AI for semantic menu matching.

---

## Key Components

### 1. API Initialization
**Function:** `init_api_keys()`
- Loads environment variables from `.env` file
- Initializes Google Gemini API with configuration
- Sets up API key for generative AI responses

**Function:** `generate_response_gemini(prompt: str)`
- Sends prompts to Gemini 2.5 Flash Lite model
- Configuration: temperature 0.01, max 32,000 output tokens (conservative settings for precise responses)
- Handles API errors gracefully

---

### 2. Main Class: MenuIngredientDiseaseGraph

#### Initialization (`__init__`)
Initializes a NetworkX graph and builds three dictionaries for efficient node lookup:
- `menu_node_dict`: Maps normalized menu titles to actual nodes
- `ingredient_node_dict`: Maps normalized ingredients to actual nodes
- `disease_node_dict`: Maps normalized diseases to actual nodes
- Calls the main graph construction method

#### Graph Construction (`connect_graph_from_menu_title_to_ingredient_to_disease`)

**Step 1: Menu → Ingredient Relationships**
- Reads `standardized_menu_ingredients.csv`
- Adds menu nodes (type='menu') and ingredient nodes (type='ingredient')
- Creates edges with relation='has_ingredient'
- Handles HTML decoding and encoding issues

**Step 2: Ingredient → Disease Relationships**
- Reads three disease relationship files:
  - `ingredient_diabetes_relation.csv`
  - `ingredient_cardiovascular_disease_relation.csv`
  - `ingredient_kidney_disease_relation.csv`
- Adds disease nodes (type='disease')
- Creates edges with attributes:
  - `effect`: positive, negative, very negative, or neutral
  - `reason`: explanation for the relationship
  - `relation`: ingredient_disease

**Step 3: Normalization**
- Creates lookup dictionaries mapping `lowercase_stripped` strings to actual node names
- Enables case-insensitive matching

---

### 3. Graph Query Methods

#### `get_menu_ingredient_disease_subgraph(menu_node)`
Returns a subgraph containing:
- The specified menu node
- All directly connected ingredients
- All diseases connected to those ingredients via effect edges
- Only includes ingredient→disease edges with effect attributes

#### `get_ingredient_disease_edges(ingredient_nodes, disease_node)`
Returns all edges from a set of ingredients to a disease where effect is one of:
- `positive`, `negative`, `very negative` (excludes neutral)

#### `get_ingredient_neighbors_of_menu(menu_node)`
Returns all ingredient nodes directly connected to a menu node

#### Node Lookup Methods
- `get_menu_node_from_string(menu_string)`: Case-insensitive menu lookup
- `get_disease_node_from_string(disease_string)`: Case-insensitive disease lookup
- `get_ingredient_node_from_string(ingredient_string)`: Case-insensitive ingredient lookup

---

### 4. Menu Matching (`find_best_matched_menu_in_graph`)

**Two-stage matching approach:**

1. **Exact Match (Stage 1)**
   - Performs case-insensitive exact match against menu nodes
   - Returns immediately if found

2. **Semantic AI Matching (Stage 2)** (if exact match fails)
   - Uses Google Gemini to compare ingredient lists
   - Sends prompt with input menu and full menu list
   - Extracts matched menu from AI response using regex
   - Returns normalized menu if semantically similar

**Returns:** Dictionary containing:
```python
{
    'matched_menu': str or None,
    'is_exact': bool
}
```

---

### 5. Graph Visualization (`visualize_menu_ingredient_disease_graph`)

**Static method** that visualizes the graph with:

**Color Scheme:**
- Menu nodes: Blue (#1f77b4)
- Ingredient nodes: Light cyan (#C7E6EE)
- Disease nodes: Magenta (#d62796)

**Edge Colors by Relationship:**
- Menu → Ingredient: Gray (#7f7f7f)
- Ingredient → Disease (Positive): Green (#19f336)
- Ingredient → Disease (Negative): Orange (#ff7f0e)
- Ingredient → Disease (Very Negative): Red (#ff0101)

**Node Sizing:**
- Disease nodes: Size 2400 (largest)
- Menu nodes: Size 300 (medium)
- Ingredient nodes: Size 175 (smallest)

**Layout:**
- Three vertical columns:
  - Column 0 (x=0): Menu titles
  - Column 1 (x=1): Ingredients
  - Column 2 (x=2): Diseases
- Y-coordinates distributed evenly to avoid overlap

**Features:**
- Filters to top N menus (default: 5)
- Excludes neutral effects
- Includes legend explaining node types and edge types
- Figure size: 18x10 inches

---

## Data Flow

```
standardized_menu_ingredients.csv
    ↓
[Menu Title] ──has_ingredient──> [Ingredient]
    ↑
[Graph Construction]
    ↓
ingredient_*_relation.csv files
    ↓
[Ingredient] ──positive/negative/very_negative──> [Disease]
    ↓
Connected Graph: Menu → Ingredient → Disease
    ↓
[Query & Visualization]
```

---

## CSV File Requirements

### `standardized_menu_ingredients.csv`
| Column | Type | Notes |
|--------|------|-------|
| title | string | Menu title |
| standardized_ingredients | string | Comma-separated ingredient list |

### Disease Relation Files (e.g., `ingredient_diabetes_relation.csv`)
| Column | Type | Notes |
|--------|------|-------|
| ingredient | string | Ingredient name |
| effect | string | positive, negative, very negative, neutral |
| reason | string | Explanation of the relationship |

---

## Usage Example

```python
# Initialize graph
graph = MenuIngredientDiseaseGraph()

# Find menu by name
result = graph.find_best_matched_menu_in_graph("rice and chicken")
if result['matched_menu']:
    menu_node = result['matched_menu']
    
    # Get subgraph for this menu
    subgraph = graph.get_menu_ingredient_disease_subgraph(menu_node)
    
    # Visualize
    MenuIngredientDiseaseGraph.visualize_menu_ingredient_disease_graph(subgraph, top_n_menus=5)
```

---

## Key Features

✅ **Flexible Matching:** Exact match + AI-powered semantic matching  
✅ **Robust CSV Parsing:** Handles encoding issues, HTML entities, and malformed data  
✅ **Efficient Node Lookup:** Normalized dictionaries for O(1) case-insensitive lookups  
✅ **Rich Graph Queries:** Multiple methods to traverse relationships  
✅ **Professional Visualization:** Color-coded, multi-column layout with legend  
✅ **Defensive Coding:** Error handling for missing files and malformed data  

---

## Dependencies

```
networkx
matplotlib
google.generativeai
openai
python-dotenv
```

---

## Notes

- Graph supports multiple disease types simultaneously
- Only non-neutral effects (positive/negative/very negative) are visualized
- Menu matching defaults to Gemini for fallback semantic search
- All node lookups are case-insensitive via normalization dictionaries
