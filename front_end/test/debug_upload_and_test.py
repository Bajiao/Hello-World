#!/usr/bin/env python3
"""
Debug script: run the image extraction + matching flow programmatically for a single image
and persist results to templates/uploads/analysis_results.json for offline testing.
"""
import os
import sys
import json
import re
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from front_end.upload_chat_image import ask_openai_image, normalize_menu_name
from backend_menu_processing.recommendation_api import MenuRecommendationAPI

IMG_PATH = '/Users/jameszhang/git/Hello-World/front_end/templates/uploads/mexican.jpeg'
UPLOADS_DIR = Path(__file__).parent / 'templates' / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_FILE = UPLOADS_DIR / 'analysis_results.json'

def main():
    print(f"Processing image: {IMG_PATH}")
    html_out = ask_openai_image(IMG_PATH)
    # ask_openai_image returns final_html (string) or error string
    if not html_out or not isinstance(html_out, str):
        print("No HTML output from ask_openai_image")
        return
    print("Extraction HTML length:", len(html_out))

    bullets = re.findall(r'•\s*([^<\n]+)', html_out)
    parsed_recipes = [normalize_menu_name(b).lower() for b in bullets if b and b.strip()]
    print("Parsed recipes:", parsed_recipes)

    api = MenuRecommendationAPI()
    matches = []
    for recipe in parsed_recipes:
        node = api.graph.get_menu_node_from_string(recipe)
        if node:
            matches.append({'query': recipe, 'matched_menu': node, 'is_exact': True})
            print(f"Exact match for '{recipe}' -> {node}")
        else:
            try:
                best = api.graph.find_best_matched_menu_in_graph(recipe)
                matches.append({'query': recipe, 'matched_menu': best.get('matched_menu') if isinstance(best, dict) else None, 'is_exact': best.get('is_exact', False) if isinstance(best, dict) else False})
                print(f"Fallback for '{recipe}' -> {best}")
            except Exception as e:
                print(f"Fallback exception for '{recipe}': {e}")
                matches.append({'query': recipe, 'matched_menu': None, 'is_exact': False})

    results = {
        Path(IMG_PATH).name: {
            'answer': html_out,
            'recipes': parsed_recipes,
            'matches': matches
        }
    }

    with open(ANALYSIS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Wrote analysis results to {ANALYSIS_FILE}")

if __name__ == '__main__':
    main()
