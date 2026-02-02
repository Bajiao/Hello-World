#!/usr/bin/env python3
"""Test Gemini-based preprocessing steps with fresh API quota"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend_menu_processing'))

from llm import load_env_variables, deduplicate_ingredients_gemini, annotate_ingredient_disease_gemini, standardize_ingredients_gemini

load_env_variables()

print("\n" + "="*80)
print("TESTING GEMINI-BASED PREPROCESSING STEPS")
print("="*80)

# STEP 3: Deduplicate
print("\n✅ STEP 3: Deduplicate & Normalize Ingredients")
print("-" * 80)
test_for_dedup = ["pasta", "garlic", "salt", "onion", "onions", "carrot", "potatoes", "potato", "butter"]
print(f"Input ({len(test_for_dedup)} items): {test_for_dedup}")

try:
    deduplicated = deduplicate_ingredients_gemini(test_for_dedup)
    if deduplicated:
        print(f"Output ({len(deduplicated)} items): {deduplicated}")
        print("✅ PASSED: Successfully deduplicated ingredients")
    else:
        print("✗ FAILED: Gemini returned None")
except Exception as e:
    print(f"✗ FAILED: {str(e)[:100]}")

# STEP 4: Annotate Disease Effects
print("\n✅ STEP 4: Annotate Disease Effects")
print("-" * 80)
test_ingredients = ["pasta", "garlic", "salt", "butter"]
diseases = ["diabetes", "cardiovascular disease"]

for disease in diseases:
    print(f"\nDisease: {disease}")
    print(f"Ingredients: {test_ingredients}")
    try:
        results = annotate_ingredient_disease_gemini(test_ingredients, disease)
        if results:
            print(f"Results ({len(results)} annotations):")
            for item in results[:2]:  # Show first 2
                print(f"  {item}")
            print("✅ PASSED: Successfully annotated disease effects")
        else:
            print("✗ FAILED: Gemini returned None")
    except Exception as e:
        print(f"✗ FAILED: {str(e)[:100]}")

# STEP 5: Standardize Ingredients
print("\n✅ STEP 5: Standardize Menu Ingredients")
print("-" * 80)
test_menus = {
    "Simple Pasta": ["pasta", "salt", "garlic", "olive oil"],
    "Vegetable Soup": ["carrot", "onion", "potatoes", "butter"],
}
canonical_list = ["pasta", "salt", "garlic", "olive oil", "carrot", "onion", "potato", "butter"]

print(f"Menus to standardize: {list(test_menus.keys())}")
print(f"Canonical ingredients: {canonical_list}\n")

try:
    results = standardize_ingredients_gemini(test_menus, canonical_list)
    if results:
        print(f"Results ({len(results)} menus):")
        for menu, std_ingrs in results.items():
            print(f"  {menu}: {std_ingrs}")
        print("✅ PASSED: Successfully standardized menu ingredients")
    else:
        print("✗ FAILED: Gemini returned None")
except Exception as e:
    print(f"✗ FAILED: {str(e)[:100]}")

print("\n" + "="*80 + "\n")
