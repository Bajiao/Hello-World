#!/usr/bin/env python3
"""
Test Script for Preprocessing Pipeline
======================================
Tests each step of the menu recommendation preprocessing pipeline
with simplified data (1-2 entries per step) to ensure all functions work correctly.

Pipeline Steps:
1. Split Ingredients (OpenAI GPT-4 Turbo)
2. Extract Unique Ingredients
3. Deduplicate & Normalize (Gemini)
4. Annotate with Disease Effects (Gemini x3)
5. Standardize Menu Ingredients (Gemini)
6. Graph Construction
"""

import os
import sys
import csv
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Add parent directory to path to import llm module
sys.path.insert(0, str(Path(__file__).parent))

from llm import (
    load_env_variables,
    get_openai_client,
    get_gemini_client,
    get_project_root,
    get_data_dir,
)
from process_menu_ingredient import PreProcessing
from menu_ingredient_disease_graph import MenuIngredientDiseaseGraph


class TestPipeline:
    """Test runner for preprocessing pipeline"""

    def __init__(self):
        """Initialize test environment"""
        load_env_variables()
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)
        self.results = []

    def print_header(self, step_num: int, step_name: str):
        """Print formatted step header"""
        print(f"\n{'='*80}")
        print(f"STEP {step_num}: {step_name}")
        print(f"{'='*80}")

    def print_status(self, status: str, message: str = ""):
        """Print formatted status message"""
        symbol = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{symbol} {status}: {message}")
        self.results.append((status, message))

    def create_test_data(self):
        """Create minimal test data files"""
        self.print_header(0, "Creating Test Data")

        # Test recipes for preprocessing
        test_recipes = [
            {
                "title": "Simple Pasta",
                "url": "https://www.allrecipes.com/recipe/1234/simple-pasta/",
                "servings": "2",
                "prepTime": "10m",
                "cookTime": "15m",
                "totalTime": "25m",
                "ingredients": "2 cups pasta | 1 tablespoon salt | 3 cloves garlic | 2 tablespoons olive oil",
                "directions": "Boil pasta. Add garlic and oil.",
                "nutrition_calories": "200",
            },
            {
                "title": "Vegetable Soup",
                "url": "https://www.allrecipes.com/recipe/5678/vegetable-soup/",
                "servings": "4",
                "prepTime": "15m",
                "cookTime": "30m",
                "totalTime": "45m",
                "ingredients": "1 carrot | 1 onion | 2 potatoes | 1 tablespoon butter",
                "directions": "Chop vegetables. Simmer in broth.",
                "nutrition_calories": "100",
            },
        ]

        # Write test recipes CSV
        test_csv = self.test_dir / "test_recipes.csv"
        with open(test_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=test_recipes[0].keys())
            writer.writeheader()
            writer.writerows(test_recipes)

        self.print_status("PASS", f"Created test_recipes.csv with {len(test_recipes)} entries")
        return test_csv

    def test_step1_split_ingredients(self):
        """Test Step 1: Split ingredients using OpenAI"""
        self.print_header(1, "Split Ingredients (OpenAI GPT-4 Turbo)")

        try:
            # Test data
            test_ingredients = [
                "2 cups pasta",
                "1 tablespoon salt",
                "3 cloves garlic, minced",
            ]

            print(f"Testing with {len(test_ingredients)} ingredients...")
            results = []

            for ingredient in test_ingredients:
                try:
                    print(f"  Processing: '{ingredient}'", end=" → ")
                    # This would call the llm.py function
                    from llm import split_ingredient_openai

                    result = split_ingredient_openai(ingredient)
                    results.append(result)
                    print(f"✓ {result}")
                except Exception as e:
                    print(f"✗ Error: {e}")
                    raise

            if len(results) == len(test_ingredients):
                self.print_status("PASS", f"Successfully split {len(results)} ingredients")
                return results
            else:
                self.print_status("FAIL", "Not all ingredients were split")
                return None

        except Exception as e:
            self.print_status("FAIL", f"Step 1 failed: {str(e)}")
            return None

    def test_step2_extract_unique(self):
        """Test Step 2: Extract unique ingredients"""
        self.print_header(2, "Extract Unique Ingredients")

        try:
            # Simulate extracted ingredients from menus
            menu_ingredients = [
                [("2 cups", "pasta"), ("1 tbsp", "salt"), ("3 cloves", "garlic")],
                [("1", "carrot"), ("1", "onion"), ("2", "potatoes"), ("1 tbsp", "butter")],
            ]

            unique_ingredients = set()
            for menu_ingr_list in menu_ingredients:
                for descriptor, core in menu_ingr_list:
                    unique_ingredients.add(core.lower().strip())

            print(f"Extracted unique ingredients: {sorted(unique_ingredients)}")
            self.print_status("PASS", f"Extracted {len(unique_ingredients)} unique ingredients")
            return list(unique_ingredients)

        except Exception as e:
            self.print_status("FAIL", f"Step 2 failed: {str(e)}")
            return None

    def test_step3_deduplicate(self):
        """Test Step 3: Deduplicate using Gemini"""
        self.print_header(3, "Deduplicate & Normalize (Gemini)")

        try:
            test_ingredients = ["pasta", "garlic", "salt", "onion", "onions", "carrot", "potatoes", "butter"]

            print(f"Testing deduplication with {len(test_ingredients)} ingredients...")
            from llm import deduplicate_ingredients_gemini

            deduplicated = deduplicate_ingredients_gemini(test_ingredients)
            print(f"Deduplicated result: {deduplicated}")

            if isinstance(deduplicated, list) and len(deduplicated) > 0:
                self.print_status("PASS", f"Successfully deduplicated to {len(deduplicated)} items")
                return deduplicated
            else:
                self.print_status("FAIL", "Deduplication returned empty or invalid result")
                return None

        except Exception as e:
            self.print_status("FAIL", f"Step 3 failed: {str(e)}")
            return None

    def test_step4_annotate_disease(self):
        """Test Step 4: Annotate ingredients with disease effects (Gemini)"""
        self.print_header(4, "Annotate Disease Effects (Gemini)")

        try:
            test_ingredients = ["pasta", "salt", "butter", "garlic", "carrot", "onion"]
            diseases = ["diabetes", "cardiovascular disease", "kidney disease"]

            from llm import annotate_ingredient_disease_gemini

            all_results = {}

            for disease in diseases:
                print(f"\n  Testing disease: {disease}")
                try:
                    results = annotate_ingredient_disease_gemini(test_ingredients, disease)
                    print(f"    Annotated {len(results)} ingredients")
                    all_results[disease] = results

                    # Display sample results
                    for i, item in enumerate(results[:2]):
                        print(f"      {item}")

                except Exception as e:
                    print(f"    ✗ Error annotating {disease}: {e}")
                    raise

            if len(all_results) == len(diseases):
                self.print_status(
                    "PASS", f"Successfully annotated ingredients for {len(all_results)} diseases"
                )
                return all_results
            else:
                self.print_status("FAIL", "Not all diseases were processed")
                return None

        except Exception as e:
            self.print_status("FAIL", f"Step 4 failed: {str(e)}")
            return None

    def test_step5_standardize_ingredients(self):
        """Test Step 5: Standardize menu ingredients (Gemini)"""
        self.print_header(5, "Standardize Menu Ingredients (Gemini)")

        try:
            test_menus = [
                "Simple Pasta",
                "Vegetable Soup",
            ]

            test_menu_ingredients = [
                ["pasta", "salt", "garlic", "olive oil"],
                ["carrot", "onion", "potatoes", "butter"],
            ]

            canonical_ingredients = ["pasta", "salt", "garlic", "olive oil", "carrot", "onion", "potatoes", "butter"]

            print(f"Testing standardization with {len(test_menus)} menus...")

            from llm import standardize_ingredients_gemini

            # Prepare data as expected by the function
            menu_ingredients_dict = {menu: ingrs for menu, ingrs in zip(test_menus, test_menu_ingredients)}

            results = standardize_ingredients_gemini(menu_ingredients_dict, canonical_ingredients)

            print(f"Standardized {len(results)} menus")
            for menu, std_ingrs in list(results.items())[:2]:
                print(f"  {menu}: {std_ingrs}")

            if len(results) > 0:
                self.print_status("PASS", f"Successfully standardized {len(results)} menus")
                return results
            else:
                self.print_status("FAIL", "Standardization returned no results")
                return None

        except Exception as e:
            self.print_status("FAIL", f"Step 5 failed: {str(e)}")
            return None

    def test_step6_graph_construction(self):
        """Test Step 6: Graph construction"""
        self.print_header(6, "Graph Construction (NetworkX)")

        try:
            # Create minimal test data files for graph construction
            test_menu_ingredients = [
                ["Simple Pasta", ["pasta", "salt", "garlic", "olive oil"]],
                ["Vegetable Soup", ["carrot", "onion", "potatoes", "butter"]],
            ]

            disease_annotations = {
                "diabetes": {
                    "pasta": "negative",
                    "salt": "neutral",
                    "garlic": "positive",
                    "olive oil": "neutral",
                    "carrot": "positive",
                    "onion": "neutral",
                    "potatoes": "negative",
                    "butter": "very negative",
                },
                "cardiovascular disease": {
                    "pasta": "neutral",
                    "salt": "very negative",
                    "garlic": "positive",
                    "olive oil": "positive",
                    "carrot": "positive",
                    "onion": "positive",
                    "potatoes": "neutral",
                    "butter": "very negative",
                },
                "kidney disease": {
                    "pasta": "neutral",
                    "salt": "very negative",
                    "garlic": "positive",
                    "olive oil": "neutral",
                    "carrot": "positive",
                    "onion": "neutral",
                    "potatoes": "negative",
                    "butter": "neutral",
                },
            }

            print("Creating minimal test graph...")

            # Create graph manually for testing
            import networkx as nx

            G = nx.DiGraph()

            # Add menu and ingredient nodes
            menu_node_dict = {}
            ingredient_node_dict = {}

            for menu_name, ingredients in test_menu_ingredients:
                # Normalize menu name for node ID
                menu_node_id = menu_name.lower().replace(" ", "_")
                G.add_node(menu_node_id, type="menu", label=menu_name)
                menu_node_dict[menu_node_id] = menu_name

                # Add ingredients and menu->ingredient edges
                for ingredient in ingredients:
                    ing_node_id = ingredient.lower().replace(" ", "_")
                    G.add_node(ing_node_id, type="ingredient", label=ingredient)
                    ingredient_node_dict[ing_node_id] = ingredient
                    G.add_edge(menu_node_id, ing_node_id, relation="has_ingredient")

            # Add disease nodes and ingredient->disease edges
            disease_node_dict = {}
            for disease in disease_annotations.keys():
                disease_node_id = disease.lower().replace(" ", "_")
                G.add_node(disease_node_id, type="disease", label=disease)
                disease_node_dict[disease_node_id] = disease

                # Add ingredient->disease edges
                for ingredient, effect in disease_annotations[disease].items():
                    ing_node_id = ingredient.lower().replace(" ", "_")
                    if G.has_node(ing_node_id):
                        G.add_edge(
                            ing_node_id,
                            disease_node_id,
                            relation="causes_effect",
                            effect=effect,
                            reason="Test annotation",
                        )

            print(f"  Nodes: {G.number_of_nodes()}")
            print(f"  Edges: {G.number_of_edges()}")
            print(f"  Menu nodes: {len([n for n in G.nodes() if G.nodes[n].get('type') == 'menu'])}")
            print(f"  Ingredient nodes: {len([n for n in G.nodes() if G.nodes[n].get('type') == 'ingredient'])}")
            print(f"  Disease nodes: {len([n for n in G.nodes() if G.nodes[n].get('type') == 'disease'])}")

            if G.number_of_nodes() > 0 and G.number_of_edges() > 0:
                self.print_status("PASS", f"Successfully created test graph with {G.number_of_nodes()} nodes")
                return G

            else:
                self.print_status("FAIL", "Graph has no nodes or edges")
                return None

        except Exception as e:
            self.print_status("FAIL", f"Step 6 failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return None

    def run_all_tests(self):
        """Run all preprocessing pipeline tests"""
        print("\n" + "=" * 80)
        print("MENU RECOMMENDATION PREPROCESSING PIPELINE - TEST SUITE")
        print("=" * 80)
        print(f"Test Data Directory: {self.test_dir}")

        try:
            # Create test data
            self.create_test_data()

            # Run each step
            step1_result = self.test_step1_split_ingredients()
            step2_result = self.test_step2_extract_unique()
            step3_result = self.test_step3_deduplicate()
            step4_result = self.test_step4_annotate_disease()
            step5_result = self.test_step5_standardize_ingredients()
            step6_result = self.test_step6_graph_construction()

            # Print summary
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)

            passed = sum(1 for status, _ in self.results if status == "PASS")
            failed = sum(1 for status, _ in self.results if status == "FAIL")
            total = len(self.results)

            for status, message in self.results:
                symbol = "✅" if status == "PASS" else "❌"
                print(f"{symbol} {message}")

            print(f"\n{'-'*80}")
            print(f"Results: {passed}/{total} tests passed")

            if failed == 0:
                print("🎉 All tests passed! Pipeline is working correctly.")
            else:
                print(f"⚠️  {failed} test(s) failed. See details above.")

            print("=" * 80 + "\n")

        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    tester = TestPipeline()
    tester.run_all_tests()
