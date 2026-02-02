#!/usr/bin/env python3
"""
Load saved analysis_results.json and test fuzzy matching (difflib) against
menu titles in the knowledge graph. Prints top candidates with similarity
ratios and ingredient lists (no LLM calls).
"""
import json
from pathlib import Path
import sys
from difflib import get_close_matches, SequenceMatcher

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

ANALYSIS_FILE = Path(__file__).parent / 'templates' / 'uploads' / 'analysis_results.json'


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def main():
    if not ANALYSIS_FILE.exists():
        print(f"No analysis file found at {ANALYSIS_FILE}")
        return
    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    api = MenuRecommendationAPI()
    # menu keys are lower-cased keys used in menu_node_dict
    menu_keys = list(api.graph.menu_node_dict.keys())

    for fname, payload in data.items():
        print(f"\n=== File: {fname} ===")
        recipes = payload.get('recipes', [])
        print(f"Parsed recipes ({len(recipes)}): {recipes}")

        for r in recipes:
            key = str(r).lower().strip()
            print(f"\nRecipe: '{r}'")
            exact = api.graph.get_menu_node_from_string(key)
            print(f" exact lookup -> {exact}")

            # get close matches
            closes = get_close_matches(key, menu_keys, n=5, cutoff=0.4)
            if not closes:
                print(" No fuzzy matches found (cutoff=0.4)")
                continue
            print(" Fuzzy candidates:")
            for c in closes:
                ratio = similarity(key, c)
                node_name = api.graph.menu_node_dict.get(c)
                details = api.get_menu_details(node_name)
                ingredients = details.get('ingredients', []) if isinstance(details, dict) else []
                print(f"  - candidate_key='{c}' ratio={ratio:.3f} node_name='{node_name}' ingredients={ingredients[:8]}")

if __name__ == '__main__':
    main()
