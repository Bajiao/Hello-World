import os
import sys
import ast
import csv
import json
import re
from pathlib import Path

# Import LLM functions from centralized module
from llm import (
    split_ingredient_openai,
    generate_response_gemini,
    annotate_ingredient_disease_gemini,
    get_data_dir
)
from menu_ingredient_disease_graph import MenuIngredientDiseaseGraph

class PreProcessing:
    '''
    This class provides a suite of static methods for processing menu ingredient data, including:
    - Processing all menu titles and writing split ingredient results to CSV.
    - Splitting ingredient strings into descriptors and core ingredient names using the OpenAI API.
    - Extracting unique core ingredients from processed data.
    - Removing duplicates and normalizing ingredient names using the Gemini API.
    - Annotating each ingredient with its health impact on specific diseases using the Gemini API.
    - Combining disease annotation results from multiple files.
    - Standardizing menu ingredient names by mapping them to a canonical list using the Gemini API.
    - Orchestrating the full preprocessing pipeline for menu-ingredient-disease relationship analysis.
    The class assumes the existence of certain helper functions (e.g., `init_api_keys`, `generate_response_gemini`) and requires access to the OpenAI and Gemini APIs for advanced NLP tasks.
    Methods:
        split_ingredient(ingredient): 
            Splits an ingredient string into (descriptor, core ingredient) using the OpenAI API.
        split_ingredient_for_all_titles(titles, df): 
            Processes all menu titles, splits their ingredients, and writes results to a CSV file.
        get_ingredient_set(filename='menu2ingredient.csv'): 
        remove_duplicates(all_ingredient_file='allIngredients.csv', unique_file='uniqueIngredients.csv'): 
            Removes duplicate and similar ingredients, normalizes them using the Gemini API, and writes unique results to a new CSV file.
        annotate_each_ingredient_causing_disease_using_gemini(input_file='uniqueIngredients.csv', disease="diabetes", output_file='ingredient_disease.csv'): 
            Annotates each ingredient with its health impact on a specified disease using the Gemini API.
        combine_ingredient_disease_annotations(diseases_and_files, output_file='combined_ingredient_disease_annotations.csv'): 
        standardize_menu_ingredients(input_file='menu2ingredient.csv', unique_ingredients_file='uniqueIngredients.csv', output_file='standardized_menu_ingredients.csv', batch_size=20): 
            Standardizes menu ingredient names by mapping them to a canonical list using the Gemini API.
        menu_ingredient_disease_relationship_preprcessing(): 
            Runs the full preprocessing pipeline for menu-ingredient-disease relationship analysis.
    '''
    def __init__(self):
        pass
    # split_ingredient function using OpenAI API
    @staticmethod
    def split_ingredient(ingredient):
        """Use centralized LLM module for ingredient splitting."""
        return split_ingredient_openai(ingredient)

    ####################################################
    #This function processes all titles and writes results to a CSV file
    ####################################################
    @staticmethod
    def split_ingredient_for_all_titles(titles, df):
        with open('menu2ingredients.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['title', 'ingredients'])
            for count, title in enumerate(titles):
                print(f"Processing {count + 1}/{len(titles)}: {title}")
                ingredients = df.loc[df['title'] == title, 'ingredients'].values
                if len(ingredients) > 0:
                    ingredient_list = str(ingredients[0]).split('|')
                    split_ingredients = [PreProcessing.split_ingredient(ingredient.strip()) for ingredient in ingredient_list]
                    print(f"\t split_ingredients: {split_ingredients}")
                else:
                    print(f"\t No ingredients found for title: {title}")
                    split_ingredients = []
                writer.writerow([title, str(split_ingredients)])
                f.flush()
                
    @staticmethod
    def get_ingredient_set(filename='menu2ingredient.csv'):
        """
        Extracts unique core ingredients from a CSV file and writes them to a new CSV file.
        This function reads the specified CSV file (default: 'menu2ingredient.csv'), where each row contains
        an 'ingredients' field. The 'ingredients' field is expected to be a string representation of a list
        of tuples (desc, core). For each tuple, if the 'core' value exists, it is stripped, converted to lowercase,
        and added to a set to ensure uniqueness.
        After processing all rows, the function writes the sorted set of unique core ingredients to 'allIngredients.csv',
        with one ingredient per row.
        Args:
            filename (str): The path to the input CSV file containing menu ingredients. Defaults to 'menu2ingredient.csv'.
        Side Effects:
            - Prints the total number of unique core ingredients found.
            - Writes the unique core ingredients to 'allIngredients.csv'.
            - Prints error messages if the input file does not exist or if a row cannot be parsed.
        Raises:
            None. All exceptions during row parsing are caught and printed.
        """
        ingredient_set = set()
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        split_ingredients = ast.literal_eval(row['ingredients'])
                        for desc, core in split_ingredients:
                            if core:
                                ingredient_set.add(core.strip().lower())
                    except Exception as e:
                        print(f"Error parsing row: {row['ingredients']}\nException: {e}")
        else:
            print(f"File {filename} does not exist. Please run split_ingredient_for_all_titles first.")

        print(f"Total unique core ingredients: {len(ingredient_set)}")
        with open('allIngredients.csv', 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(['ingredient'])
            for ingredient in sorted(ingredient_set):
                writer.writerow([ingredient])
    
    @staticmethod
    def remove_duplicates(all_ingredient_file='allIngredients.csv', unique_file='uniqueIngredients.csv'):
        """
        Removes duplicate and similar ingredients from a CSV file, normalizes them using the Gemini API, 
        and writes the unique, normalized ingredients to a new CSV file.
        Args:
            all_ingredient_file (str): Path to the input CSV file containing an 'ingredient' column. 
                                    Defaults to 'allIngredients.csv'.
            unique_file (str): Path to the output CSV file where unique, normalized ingredients will be written.
                            Defaults to 'uniqueIngredients.csv'.
        Process Overview:
            1. Initializes API keys (via init_api_keys).
            2. Reads the input CSV and collects all unique, lowercased, and stripped ingredient names.
            3. Writes the header to the output CSV.
            4. Sends the list of unique ingredients to the Gemini API for deduplication and normalization 
            (e.g., treating plural/singular forms as the same).
            5. Parses the API response, expecting a JSON array of normalized ingredient names.
            6. Writes the normalized ingredients to the output CSV.
            7. Handles errors gracefully, falling back to writing the original unique list if needed.
            8. Prints status messages and writes the raw API response to 'response.txt' for debugging.
        Notes:
            - Requires the functions `init_api_keys()` and `generate_response_gemini(prompt)` to be defined elsewhere.
            - Expects the input CSV to have an 'ingredient' column.
            - Uses the Gemini API for advanced deduplication and normalization.
            - Handles file existence and API errors with informative print statements.
        """
        init_api_keys()
        if os.path.exists(all_ingredient_file):
            with open(all_ingredient_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                ingredients = {row['ingredient'].strip().lower() for row in reader if row['ingredient'].strip()}
            
            with open(unique_file, 'w', encoding='utf-8', newline='') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(['ingredient'])
                
                if ingredients:
                    # Prepare the list of unique ingredients
                    ingredient_list = sorted(ingredients)

                    # Use the Gemini API via the generate_response_gemini function
                    try:
                        prompt = (
                            "Given this list of ingredients, deduplicate and normalize them. "
                            "Treat plural and singular forms as the same ingredient. "
                            "Return ONLY the final deduped list as a JSON array of strings, no explanation.\n"
                            f"Ingredients: {json.dumps(ingredient_list)}"
                        )
                        response_text = generate_response_gemini(prompt)
                        # If generate_response_gemini prints instead of returning, you may need to capture stdout or refactor it to return the text.
                        # Assuming it returns the text:
                        if response_text:
                            with open('response.txt', 'w', encoding='utf-8') as resp_file:
                                resp_file.write(response_text)
                            print ("Gemini response:", response_text)
                            try:
                                match = re.search(r'\[.*\]', response_text, re.DOTALL)
                                if match:
                                    normalized_ingredients = json.loads(match.group(0))
                                    for ingredient in normalized_ingredients:
                                        writer.writerow([ingredient])
                                else:
                                    print("No JSON array found in Gemini response, writing original list.")
                                    for ingredient in ingredient_list:
                                        writer.writerow([ingredient])
                            except Exception as e:
                                print(f"Error parsing Gemini response: {e}")
                                for ingredient in ingredient_list:
                                    writer.writerow([ingredient])
                        else:
                            for ingredient in ingredient_list:
                                writer.writerow([ingredient])
                    except Exception as e:
                        print(f"Error calling Gemini: {e}")
                        for ingredient in ingredient_list:
                            writer.writerow([ingredient])
            print(f"Removed duplicates. Unique ingredients written to {unique_file}.")
        else:
            print(f"File {all_ingredient_file} does not exist.")

    @staticmethod
    def annotate_each_ingredient_causing_disease_using_gemini(input_file='uniqueIngredients.csv', disease="diabetes", output_file='ingredient_disease.csv'):
        """
        Annotates each ingredient from a CSV file with its health impact regarding a specified disease using the Gemini API.
        This function reads a list of unique ingredients from the specified input CSV file, sends them to the Gemini API
        with a prompt to classify their effect ('positive', 'neutral', or 'negative') on the given disease, and writes
        the annotated results to an output CSV file. If the API response cannot be parsed, all ingredients are marked as 'neutral'.
        Args:
            input_file (str): Path to the input CSV file containing a column 'ingredient' with ingredient names.
            disease (str): The disease to assess the health impact of each ingredient against.
            output_file (str): Path to the output CSV file where annotated results will be saved.
        Returns:
            None
        Side Effects:
            - Reads from `input_file`.
            - Writes annotated results to `output_file`.
            - Prints status messages and errors to the console.
        """
        output_file = f"ingredient_{disease}_relation.csv"
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            ingredients = [row['ingredient'].strip() for row in reader if row['ingredient'].strip()]

            batch_size = 50

            with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
                writer = csv.DictWriter(out_f, fieldnames=['ingredient', 'effect', 'reason'])
                writer.writeheader()

                for i in range(0, len(ingredients), batch_size):
                    batch = ingredients[i:i+batch_size]
                    print(f"Processing batch {i//batch_size + 1}/{(len(ingredients)-1)//batch_size + 1} for {disease}...")
                    
                    # Use centralized Gemini function
                    annotations = annotate_ingredient_disease_gemini(batch, disease)
                    
                    if annotations:
                        for entry in annotations:
                            ingredient = entry.get("ingredient", "")
                            effect = entry.get("effect", "neutral").lower()
                            reason = entry.get("reason", "")
                            writer.writerow({"ingredient": ingredient, "effect": effect, "reason": reason})
                    else:
                        print(f"Failed to annotate batch {i//batch_size + 1}, marking all as neutral")
                        for ingredient in batch:
                            writer.writerow({"ingredient": ingredient, "effect": "neutral", "reason": ""})
                    out_f.flush()
                    
                print(f"✓ Annotated results written to {output_file}")
    
    @staticmethod
    def combine_ingredient_disease_annotations(diseases_and_files, output_file='combined_ingredient_disease_annotations.csv'):
        """
        Combines multiple ingredient-disease annotation CSV files into a single CSV file.
        Each input file should contain columns: 'ingredient', 'effect', and 'reason'.
        The combined output will have columns: 'ingredient', 'disease', 'effect', and 'reason'.
        
        Args:
            diseases_and_files (dict): A dictionary mapping disease names to their corresponding annotation CSV file paths.
            output_file (str): Path to the output CSV file where combined results will be saved.
        
        Returns:
            None
        Side Effects:
            - Reads from multiple input CSV files.
            - Writes combined results to `output_file`.
            - Prints status messages to the console.
        """
        combined_rows = []
        for disease, file_path in diseases_and_files.items():
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        ingredient = row.get('ingredient', '').strip()
                        effect = row.get('effect', '').strip()
                        reason = row.get('reason', '').strip()
                        if ingredient:
                            combined_rows.append({
                                'ingredient': ingredient,
                                'disease': disease,
                                'effect': effect,
                                'reason': reason
                            })
            else:
                print(f"File {file_path} does not exist. Skipping.")
        
        with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.DictWriter(out_f, fieldnames=['ingredient', 'disease', 'effect', 'reason'])
            writer.writeheader()
            for row in combined_rows:
                writer.writerow(row)
        
        print(f"Combined annotations written to {output_file}.")
    
    @staticmethod
    def standardize_menu_ingredients(
        input_file='menu2ingredient.csv',
        unique_ingredients_file='uniqueIngredients.csv',
        output_file='standardized_menu_ingredients.csv',
        batch_size=20
    ):
        """
        Reads allIngredients.csv containing menu, description, and non-standardized ingredient.
        Uses uniqueIngredients.csv for standardized ingredient list.
        Calls Gemini API in batches of 20 menu items to match non-standardized ingredients to standardized ones.
        Writes results to standardized_menu_ingredients.csv.
        """
        init_api_keys()
        # Load unique standardized ingredients
        standardized_ingredients = set()
        if os.path.exists(unique_ingredients_file):
            with open(unique_ingredients_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ingredient = row.get('ingredient', '').strip().lower()
                    if ingredient:
                        standardized_ingredients.add(ingredient)
        else:
            print(f"File {unique_ingredients_file} does not exist. Please run remove_duplicates first.")
            return

        standardized_ingredients_list = sorted(standardized_ingredients)
        # Load menu items (title and non-standardized ingredients)
        menu_items = []
        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    title = row.get('title', '').strip()
                    ingredients = row.get('ingredients', '').strip()
                    # The 'ingredients' column is a string representation of a list of tuples: (descriptor, core ingredient)
                    # We want to extract only the core ingredient names for matching
                    try:
                        split_ingredients = ast.literal_eval(ingredients)
                        core_ingredients = [core for desc, core in split_ingredients if core]
                        core_ingredients_str = ', '.join(core_ingredients)
                    except Exception as e:
                        print(f"Error parsing ingredients for title '{title}': {e}")
                        core_ingredients_str = ''
                    if title and core_ingredients_str:
                        menu_items.append((title, core_ingredients_str))
        else:
            print(f"File {input_file} does not exist.")
            return

        with open(output_file, 'w', encoding='utf-8', newline='') as out_f:
            writer = csv.writer(out_f)
            writer.writerow(['title', 'original_ingredients', 'standardized_ingredients'])
            print(f"Processing {len(menu_items)} menu items in batches of {batch_size}...")

            for i in range(0, len(menu_items), batch_size):
                batch = menu_items[i:i+batch_size]
                # For each batch, send only the core ingredient names to Gemini for mapping
                original_ingredients_batch = [ingredients for _, ingredients in batch]
                prompt = (
                    f"Given this list of standardized ingredients: {json.dumps(standardized_ingredients_list)}, "
                    f"for each comma-separated ingredient string below, match each ingredient to one or more standardized ingredients from the list. "
                    f"Ignore any descriptors, amounts, weights, or sizes. Focus only on the ingredient names. "
                    f"Return ONLY a JSON array of objects, each with keys 'original_ingredients' (the comma-separated string) and 'standardized_ingredients' (a JSON array of matched standardized ingredients). "
                    f"If no match is found for an item, use an empty array for 'standardized_ingredients'.\n"
                    f"Ingredient strings: {json.dumps(original_ingredients_batch)}"
                )
                response_text = generate_response_gemini(prompt)
                print(f"Gemini response for batch {i//batch_size + 1}:", response_text)
                with open(f'response_standardization_batch_{i//batch_size + 1}.txt', 'w', encoding='utf-8') as resp_file:
                    resp_file.write(response_text if response_text else "")
                try:
                    match = re.search(r'\[.*\]', response_text or "", re.DOTALL)
                    if match:
                        batch_results = json.loads(match.group(0))
                        for idx, entry in enumerate(batch_results):
                            original_ingredients = entry.get("original_ingredients", "")
                            standardized_ingredients = entry.get("standardized_ingredients", [])
                            matched_ingredients_str = ', '.join(standardized_ingredients) if standardized_ingredients else 'No match'
                            title = batch[idx][0] if idx < len(batch) else ""
                            writer.writerow([title, original_ingredients, matched_ingredients_str])
                    else:
                        print("No JSON array found in Gemini response, writing 'No match' for all in batch.")
                        for title, ingredients in batch:
                            writer.writerow([title, ingredients, 'No match'])
                except Exception as e:
                    print(f"Error parsing Gemini response: {e}")
                    for title, ingredients in batch:
                        writer.writerow([title, ingredients, 'No match'])
                out_f.flush()
            print(f"Standardized menu ingredients written to {output_file}.")
    
    @staticmethod
    def menu_ingredient_disease_relationship_preprcessing():
        # Step 1:
        PreProcessing.split_ingredient_for_all_titles()
        # Step 2:
        PreProcessing.get_ingredient_set()
        # Step 3:
        PreProcessing.remove_duplicates() 
        # #Step 4:  
        PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="diabetes")
        PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="cardiovascular disease")
        PreProcessing.annotate_each_ingredient_causing_disease_using_gemini(disease="kidney disease")
        #Step 5:
        PreProcessing.standardize_menu_ingredients()
        
        # disease_files = {
        #     "diabetes": "ingredient_diabetes_relation.csv",
        #     "cardiovascular disease": "ingredient_cardiovascular_disease_relation.csv",
        #     "kidney disease": "ingredient_kidney_disease_relation.csv"
        # }
        # PreProcessing.combine_ingredient_disease_annotations(diseases_and_files=disease_files)
        
        
    @staticmethod
    def analyze_menus_for_disease_effects(menu_ingredient_disease_graph, disease="diabetes"):
        """
        Analyzes all menus in the graph for their health effects on a specified disease.
        
        For each menu, this method:
        - Retrieves all ingredient nodes associated with the menu
        - Finds edges from those ingredients to the specified disease node
        - Counts the effects ('positive', 'negative', 'very negative', 'neutral')
        - Collects reasoning for non-neutral effects
        - Writes results to a CSV file with columns: menu_title, positive, negative, very_negative, neutral, reasoning
        
        Args:
            disease (str): The disease to analyze menu effects for. Defaults to "diabetes".
        
        Returns:
            None
        
        Side Effects:
            - Creates and writes results to '{disease}_menu_analysis.csv'
            - Prints status message upon completion
        """
        disease_node = menu_ingredient_disease_graph.get_disease_node_from_string(disease)

        # Get all menu nodes
        menu_nodes = [node for node, attr in menu_ingredient_disease_graph.G.nodes(data=True) if attr.get('type') == 'menu']

        results = []
        for menu_node in menu_nodes:
            menu_title = menu_node
            
            # Get ingredient neighbors of this menu
            ingredient_nodes = menu_ingredient_disease_graph.get_ingredient_neighbors_of_menu(menu_node)
            
            # Get edges from ingredients to disease
            edges = menu_ingredient_disease_graph.get_ingredient_disease_edges(ingredient_nodes, disease_node)
            
            # Count by effect type
            effect_counts = {'positive': 0, 'negative': 0, 'very negative': 0, 'neutral': 0}
            reasoning = []
            
            for src, dst, data in edges:
                effect = data.get('effect', 'neutral').lower()
                if effect in effect_counts:
                    effect_counts[effect] += 1
                    if effect != 'neutral':
                        ingredient_name = menu_ingredient_disease_graph.G.nodes[src].get('name', src)
                        reason = data.get('reason', '')
                        reasoning.append(f"{ingredient_name} ({effect}): {reason}")
            
            results.append({
                'menu_title': menu_title,
                'positive': effect_counts['positive'],
                'negative': effect_counts['negative'],
                'very_negative': effect_counts['very negative'],
                'neutral': effect_counts['neutral'],
                'reasoning': ' | '.join(reasoning) if reasoning else 'No significant effects'
            })

        # Write results to CSV
        with open(f'{disease}_menu_analysis.csv', 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['menu_title', 'positive', 'negative', 'very_negative', 'neutral', 'reasoning']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow(result)

        print(f"Analysis complete. Results written to {disease}_menu_analysis.csv")


def main():
    ########################################################
    # preprocessing steps is run only once to create the csv files 
    ########################################################
    ###PreProcessing.menu_ingredient_disease_relationship_preprcessing()
    #######################################################
    
    
    menu_ingredient_disease_graph = MenuIngredientDiseaseGraph()
    Test = False
    if Test:
        
        #exact match
        matched_menu = menu_ingredient_disease_graph.find_best_matched_menu_in_graph("Grilled Chicken Adobo")
        print(matched_menu)
        matched_menu_node = menu_ingredient_disease_graph.get_menu_node_from_string(matched_menu['matched_menu'])
        subgraph = menu_ingredient_disease_graph.get_menu_ingredient_disease_subgraph(matched_menu_node)
        #MenuIngredientDiseaseGraph.visualize_menu_ingredient_disease_graph(subgraph, top_n_menus=5)
        ingredient_nodes = menu_ingredient_disease_graph.get_ingredient_neighbors_of_menu(matched_menu_node)
        disease_node = menu_ingredient_disease_graph.get_disease_node_from_string("diabetes")
        edges = menu_ingredient_disease_graph.get_ingredient_disease_edges(ingredient_nodes, disease_node)
        #print the edges from ingredient to disease (no neutral edges)
        print(edges)
        
        
        #llm match
        matched_menu = menu_ingredient_disease_graph.find_best_matched_menu_in_graph("Chicken Salad")
        matched_menu_node = menu_ingredient_disease_graph.get_menu_node_from_string(matched_menu['matched_menu'])    
        subgraph = menu_ingredient_disease_graph.get_menu_ingredient_disease_subgraph(matched_menu_node)
        MenuIngredientDiseaseGraph.visualize_menu_ingredient_disease_graph(subgraph, top_n_menus=5)
        
        MenuIngredientDiseaseGraph.visualize_menu_ingredient_disease_graph(menu_ingredient_disease_graph.G, top_n_menus=5)
    else:
        # Run analysis for every disease node in the graph
        diseases = []
        for node, attr in menu_ingredient_disease_graph.G.nodes(data=True):
            if attr.get('type') == 'disease':
                # prefer a 'name' attribute if present, otherwise use the node identifier
                diseases.append(attr.get('name', node))

        for disease in sorted(set(diseases)):
            print(f"Analyzing menus for disease: {disease}")
            PreProcessing.analyze_menus_for_disease_effects(menu_ingredient_disease_graph, disease=disease)

        
if __name__ == "__main__":
    main()


