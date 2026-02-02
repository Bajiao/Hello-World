#!/usr/bin/env python3
"""
Simple script to load saved upload analysis results and run matching tests
against the knowledge graph (MenuRecommendationAPI). Helpful for debugging
without using the UI.

Usage:
  cd front_end
  python run_saved_analysis.py

This will read `templates/uploads/analysis_results.json` (created by the Flask
app) and for each saved upload it will print parsed recipes, existing matches,
and the fallback matching results from the graph API.
"""
import json
from pathlib import Path
import os
import sys

# allow importing backend package
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend_menu_processing.recommendation_api import MenuRecommendationAPI

UPLOADS = Path(__file__).parent / 'templates' / 'uploads'
ANALYSIS_FILE = UPLOADS / 'analysis_results.json'


def load_analysis():
    if not ANALYSIS_FILE.exists():
        print(f"No analysis file found at {ANALYSIS_FILE}")
        return {}
    with open(ANALYSIS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_tests():
    data = load_analysis()
    if not data:
        return
    api = MenuRecommendationAPI()
    for filename, payload in data.items():
        print(f"\n=== File: {filename} ===")
        recipes = payload.get('recipes', [])
        saved_matches = payload.get('matches', [])
        print(f"Parsed recipes ({len(recipes)}): {recipes}")
        print(f"Saved matches: {saved_matches}")
        for i, recipe in enumerate(recipes):
            print(f"\n-- Recipe[{i}]: '{recipe}'")
            node = api.graph.get_menu_node_from_string(recipe)
            print(f" exact node lookup -> {node}")
            if node:
                print("  -> exact match found in graph")
                continue
            print("  -> no exact node, trying LLM/graph fallback...")
            try:
                best = api.graph.find_best_matched_menu_in_graph(recipe)
                print(f"  fallback result: {best}")
            except Exception as e:
                print(f"  fallback raised exception: {e}")


if __name__ == '__main__':
    run_tests()
