"""
Run gpt5-nano matching test against saved analysis_results.json
"""
import json
import sys
from pathlib import Path

# Ensure project root is on sys.path so backend_menu_processing can be imported
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
from backend_menu_processing.menu_ingredient_disease_graph import MenuIngredientDiseaseGraph

ANALYSIS_PATH = Path(__file__).parent / 'templates' / 'uploads' / 'analysis_results.json'

def main():
    if not ANALYSIS_PATH.exists():
        print(f"Saved analysis not found at {ANALYSIS_PATH}")
        return
    data = json.loads(ANALYSIS_PATH.read_text())
    # Support two shapes: direct dict with keys, or file-keyed object (e.g. {"mexican.jpeg": {...}})
    if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), dict):
        inner = next(iter(data.values()))
    else:
        inner = data

    parsed = inner.get('recipes') or inner.get('parsed_recipes') or inner.get('parsed_recipes_clean') or []
    if not parsed:
        print('No parsed recipes found in saved analysis JSON.')

    print('Loading graph...')
    g = MenuIngredientDiseaseGraph()
    for r in parsed:
        print('\nRecipe:', r)
        res = g.find_best_matched_menu_in_graph(r)
        print('-> matched:', res.get('matched_menu'), 'exact:', res.get('is_exact'))

if __name__ == '__main__':
    main()
