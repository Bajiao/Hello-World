# Quick Start Guide - Menu Recommendation API

## Installation

The system is already set up! Just ensure Python packages are installed:

```bash
source /opt/anaconda3/bin/activate py311
pip install openai httpx networkx google-generativeai pandas python-dotenv
```

## Quick Examples

### 1. Get Top 10 Unhealthy Menus for Diabetes

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

api = MenuRecommendationAPI()
results = api.get_menus_for_disease("diabetes", top_n=10, ranking="unhealthy")

for rank, menu_rec in enumerate(results, 1):
    print(f"{rank}. {menu_rec['menu']}")
    print(f"   Risk Score: {menu_rec['score']}")
    print(f"   Very Negative: {menu_rec['very_negative_count']}, "
          f"Negative: {menu_rec['negative_count']}, "
          f"Positive: {menu_rec['positive_count']}")
    print()
```

### 2. Get Details for a Specific Menu

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

api = MenuRecommendationAPI()
details = api.get_menu_details("Finnish Runeberg Tortes", disease="diabetes")

print(f"Menu: {details['menu']}")
print(f"Total Ingredients: {details['ingredient_count']}")
print(f"Ingredients: {', '.join(details['ingredients'])}")

# Get disease-specific analysis
if 'disease_analysis_diabetes' in details:
    print("\nDisease Analysis for Diabetes:")
    for ing_analysis in details['disease_analysis_diabetes']:
        print(f"  - {ing_analysis['ingredient']}: {ing_analysis['effect']}")
```

### 3. Compare Multiple Menus

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

api = MenuRecommendationAPI()
menus = ["Swedish Spareribs", "Korean Street Toast", "Finnish Runeberg Tortes"]
comparison = api.compare_menus(menus, disease="diabetes")

print(f"Comparison for DIABETES:")
for rec in comparison:
    print(f"{rec['menu']}: {rec['score']} "
          f"(v_neg: {rec['very_negative']}, neg: {rec['negative']}, pos: {rec['positive']})")
```

### 4. List Available Options

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

api = MenuRecommendationAPI()

print("Available Diseases:")
print(api.get_available_diseases())

print("\nTotal Menus in Graph:")
print(len(api.get_available_menus()))
```

## Command Line Usage

### Run Full Evaluation (Graph vs LLM vs Judge)

```bash
cd /Users/jacob/git/Hello-World
source /opt/anaconda3/bin/activate py311

# Basic run (25 samples, top 10, diabetes)
python3 backend_menu_processing/evaluate_recommendations.py

# Custom options
python3 backend_menu_processing/evaluate_recommendations.py \
  --disease "cardiovascular disease" \
  --sample 50 \
  --top 20 \
  --seed 123
```

**Options:**
- `--disease`: Target disease (default: "diabetes")
- `--sample`: Number of menus to sample (default: 25)
- `--top`: Top-K results to produce (default: 10)
- `--seed`: Random seed for reproducibility (default: 42)

**Output Files:**
- `graph_ranked.json` - Graph-based ranking with full breakdown
- `llm_ranked.json` - LLM-based ranking (uses GPT-4o)
- `gemini_judgement.txt` - Expert judge's assessment

## Integration with Upload Chat

Add this to your `upload_chat_image.py`:

```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

# After extracting menu from image
def get_health_recommendations(menu_name, disease):
    api = MenuRecommendationAPI()
    
    # Get menu details
    details = api.get_menu_details(menu_name, disease=disease)
    
    # Get comparison with top unhealthy alternatives
    top_unhealthy = api.get_menus_for_disease(disease, top_n=5, ranking="unhealthy")
    top_healthy = api.get_menus_for_disease(disease, top_n=5, ranking="healthy")
    
    return {
        "menu_details": details,
        "similar_unhealthy": top_unhealthy,
        "healthier_alternatives": top_healthy
    }
```

## API Reference

### MenuRecommendationAPI

#### `__init__()`
Initialize the API and load the knowledge graph.

#### `get_menus_for_disease(disease, top_n=10, ranking="unhealthy")`
Get ranked menus for a specific disease.

**Parameters:**
- `disease` (str): Disease name
- `top_n` (int): Number of results to return
- `ranking` (str): "unhealthy" or "healthy"

**Returns:** List of dicts with menu, score, ingredients, breakdown

#### `get_menu_details(menu_name, disease=None)`
Get detailed information about a specific menu.

**Parameters:**
- `menu_name` (str): Menu name
- `disease` (str, optional): Filter analysis by disease

**Returns:** Dict with menu details, ingredients, optional disease analysis

#### `compare_menus(menu_names, disease)`
Compare multiple menus for a specific disease.

**Parameters:**
- `menu_names` (List[str]): List of menu names
- `disease` (str): Disease to evaluate

**Returns:** Sorted list of comparison dicts

#### `get_available_diseases()`
Get list of all diseases in the knowledge graph.

**Returns:** List of disease names

#### `get_available_menus()`
Get list of all menus in the knowledge graph.

**Returns:** List of menu names

## Scoring Details

### Score Calculation
```
Score = (3 × very_negative_count) + (1 × negative_count) - (1 × positive_count)
```

**Interpretation:**
- Higher score = More unhealthy for the disease
- Lower score = More healthy for the disease

### Ingredient Effects
- **Very Negative:** Directly harmful (weight: 3)
- **Negative:** Contributes to disease risk (weight: 1)
- **Positive:** Protective/beneficial (weight: -1)

Example for Diabetes:
- Very Negative: Sugar, white flour, refined carbs
- Negative: Butter, processed oils
- Positive: Egg, fiber, lean protein

## Performance

- **Graph initialization:** ~2-5 seconds
- **Ranking 25 menus:** ~100ms
- **Getting menu details:** ~50ms
- **Comparing 3 menus:** ~50ms

## Troubleshooting

### Error: "Module not found: menu_ingredient_disease_graph"
Make sure you're running from `/Users/jacob/git/Hello-World` and have activated the py311 environment.

### Error: "Disease not found"
Check available diseases: `api.get_available_diseases()`

### Error: "Menu not found"
The system does fuzzy matching. Try a partial menu name.

### API Quota Exceeded
The evaluation framework automatically falls back to graph-based scoring if API quotas are exceeded.

## Files

- `backend_menu_processing/recommendation_api.py` - Main API (247 lines)
- `backend_menu_processing/evaluate_recommendations.py` - Evaluation framework (166 lines)
- `backend_menu_processing/menu_ingredient_disease_graph.py` - Underlying graph (523 lines)

## Questions?

All functions have docstrings. Check them with:
```python
from backend_menu_processing.recommendation_api import MenuRecommendationAPI
help(MenuRecommendationAPI.get_menus_for_disease)
```
