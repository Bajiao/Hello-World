import os, sys
import matplotlib.pyplot as plt
import networkx as nx
import csv
import re
import html
import json
import openai
from dotenv import load_dotenv
import google.generativeai as genai

# Set your OpenAI API key here
openai.api_key = ""
def init_api_keys():
    try:
        load_dotenv()
        api_key = "<your gemini key>" 
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
    except Exception as exception:
        print("Error in initializing API keys:", exception)

def generate_response_gemini(prompt: str):
    # Ensure API key is set before making a call
    if not os.environ.get("GOOGLE_API_KEY"):
        init_api_keys()
    generation_config = {
                            "temperature": 0.01,
                            "top_p": 1,
                            "top_k": 1,
                            "max_output_tokens": 32000,
                        }
    model_name = 'gemini-2.5-flash-lite'
    model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
    prompt_parts = [prompt]
    try:
        response = model.generate_content(prompt_parts)
        if hasattr(response, "text") and response.text:
            return response.text
        else:
            print("No valid response text returned from Gemini.")
            return None
    except Exception as exception:
        print("Error generating response:", exception)
        return None


class MenuIngredientDiseaseGraph:
    def __init__(self):
        self.G = nx.Graph()
        self.menu_node_dict = {}
        self.ingredient_node_dict = {}
        self.disease_node_dict = {}
        self.connect_graph_from_menu_title_to_ingredient_to_disease()
        # Use menu_node_dict for efficient menu matching
        self.menu_nodes = list(self.menu_node_dict.keys())
    
    def get_menu_ingredient_disease_subgraph(self, menu_node):
        """
        Given a menu node (case-insensitive), returns a subgraph of self.G that includes:
        - The menu node
        - All directly connected ingredient nodes
        - All disease nodes connected to those ingredients via effect edges
        Only includes ingredient→disease edges (with effect attribute).
        Returns:
            nx.Graph: The induced subgraph.
        """
        nodes = set([menu_node])
        edges = []

        # Get ingredient neighbors
        ingredient_nodes = [
            n for n in self.G.neighbors(menu_node)
            if self.G.nodes[n].get('type') == 'ingredient'
        ]
        nodes.update(ingredient_nodes)
        for ing in ingredient_nodes:
            edges.append((menu_node, ing, self.G.get_edge_data(menu_node, ing)))

            # Get disease neighbors for each ingredient
            for neighbor in self.G.neighbors(ing):
                if self.G.nodes[neighbor].get('type') == 'disease':
                    edge_data = self.G.get_edge_data(ing, neighbor)
                    nodes.add(neighbor)
                    edges.append((ing, neighbor, edge_data))

        # Build subgraph
        subG = nx.Graph()
        for n in nodes:
            subG.add_node(n, **self.G.nodes[n])
        for u, v, d in edges:
            if d:
                subG.add_edge(u, v, **d)
        return subG

    def get_ingredient_disease_edges(self, ingredient_nodes, disease_node):
        """
        Given a set of ingredient nodes and a disease node, return all edges from ingredient node to the disease node
        where the effect is in {'positive', 'negative', 'very negative'}.

        Args:
            ingredient_nodes (set): Set of ingredient node names.
            disease_node (str): Disease node name.

        Returns:
            list: List of tuples (ingredient_node, disease_node, edge_data) for matching edges.
        """
        valid_effects = {'positive', 'negative', 'very negative'}
        edges = []
        for ing in ingredient_nodes:
            if self.G.has_edge(ing, disease_node):
                edge_data = self.G.get_edge_data(ing, disease_node)
                effect = edge_data.get('effect', '').lower() if edge_data else ''
                if effect in valid_effects:
                    edges.append((ing, disease_node, edge_data))
        return edges
    def get_ingredient_neighbors_of_menu(self, menu_node):
        """
        Given a menu node, returns a set of ingredient nodes that are direct neighbors of the menu node.
        Args:
            menu_node: The menu node in the graph.
        Returns:
            set: Set of ingredient nodes connected to the menu node.
        """
        return {
            n for n in self.G.neighbors(menu_node)
            if self.G.nodes[n].get('type') == 'ingredient'
        }
    def connect_graph_from_menu_title_to_ingredient_to_disease(self, 
            menu_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/standardized_menu_ingredients.csv'),
            disease_files = {
            "diabetes": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ingredient_diabetes_relation.csv"),
            "cardiovascular disease": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ingredient_cardiovascular_disease_relation.csv"), 
            "kidney disease": os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/ingredient_kidney_disease_relation.csv")
            }                                                                
        ):
        """
        connect_graph_from_menu_title_to_ingredient_to_disease reads standardized_menu_ingredients.csv to build graph for menu title to ingredient;
        reads ingredient_diabetes_relation.csv, ingredient_cardiovascular_disease_relation.csv, ingredient_kidney_disease_relation.csv to build graph for ingredient to disease;
        then connects menu title to ingredient to disease in a single graph and visualizes it.
        
        The function constructs and visualizes a graph connecting menu titles to their ingredients and further to diseases,
        based on relationships defined in CSV files.
        The function performs the following steps:
        1. Reads 'standardized_menu_ingredients.csv' to build edges from menu titles to their standardized ingredients.
        2. Reads disease relation files ('ingredient_diabetes_relation.csv', 'ingredient_cardiovascular_disease_relation.csv',
        'ingredient_kidney_disease_relation.csv') to build edges from ingredients to diseases, annotated with effect and reason.
        3. Combines these relationships into a single graph, connecting menu titles → ingredients → diseases.
        4. Visualizes a subgraph containing the top N menu titles (default: 5), their ingredients, and related diseases
        (excluding 'neutral' effects).
        Visualization details:
        - Menu, ingredient, and disease nodes are color-coded and sized distinctly.
        - Edges from menu to ingredient are gray; ingredient to disease edges are colored by effect (positive, negative, very negative).
        - Node positions are arranged for clarity: menus, ingredients, and diseases are placed in separate columns.
        - A legend is included to explain node and edge types.
        Parameters
        ----------
        top_n_menus : int, optional
            Number of menu titles to display in the visualization (default is 5).
        Requirements
        ------------
        - The following CSV files must exist in the working directory:
            * standardized_menu_ingredients.csv
            * ingredient_diabetes_relation.csv
            * ingredient_cardiovascular_disease_relation.csv
            * ingredient_kidney_disease_relation.csv
        - Each CSV must have appropriate columns:
            * standardized_menu_ingredients.csv: 'title', 'standardized_ingredients'
            * disease relation files: 'ingredient', 'effect', optionally 'reason'
        Returns
        -------
        None
            Displays a matplotlib plot of the constructed graph.
        Notes
        -----
        - Only non-neutral ingredient-disease relationships are visualized.
        - If required files are missing, the function prints a warning and skips those relationships.
        - Uses NetworkX for graph construction and Matplotlib for visualization.

        """
        # Step 1: Build graph from menu title to ingredient
        if not os.path.exists(menu_file):
            print(f"{menu_file} not found.")
            sys.exit(1)

        # Read menu file with utf-8-sig to handle BOM and ensure correct decoding
        with open(menu_file, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ensure all fields are decoded and stripped properly
                title = row['title'].strip()
                # Defensive: decode and strip each ingredient
                ingredients_field = row['standardized_ingredients']
                if isinstance(ingredients_field, bytes):
                    ingredients_field = ingredients_field.decode('utf-8', errors='replace')
                # HtmlDecode for both title and ingredients
                title = html.unescape(title)
                ingredients_field = html.unescape(ingredients_field)
                ingredients = [html.unescape(ing.strip()) for ing in ingredients_field.split(',') if ing.strip() and ing.strip().lower() != 'no match']
                for ingredient in ingredients:
                    # Defensive: ensure ingredient is str and strip
                    if isinstance(ingredient, bytes):
                        ingredient = ingredient.decode('utf-8', errors='replace')
                    ingredient = ingredient.strip()
                    ingredient = html.unescape(ingredient)
                    # Only add nodes if they don't exist
                    if not self.G.has_node(title):
                        self.G.add_node(title, type='menu')
                    if not self.G.has_node(ingredient):
                        self.G.add_node(ingredient, type='ingredient')
                    self.G.add_edge(title, ingredient, relation='has_ingredient')

        # Step 2: Build graph from ingredient to disease

        for disease, file_path in disease_files.items():
            if not os.path.exists(file_path):
                print(f"{file_path} not found. ERROR LOADING FILE FOR {disease}!!!")
                sys.exit(1)
            with open(file_path, 'r', encoding='utf-8-sig', errors='replace') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Defensive: decode and strip all fields
                    ingredient = row['ingredient']
                    if isinstance(ingredient, bytes):
                        ingredient = ingredient.decode('utf-8', errors='replace')
                    ingredient = ingredient.strip()
                    effect = row['effect']
                    if isinstance(effect, bytes):
                        effect = effect.decode('utf-8', errors='replace')
                    effect = effect.strip().lower()
                    reason = row.get('reason', '')
                    if isinstance(reason, bytes):
                        reason = reason.decode('utf-8', errors='replace')
                    reason = reason.strip()
                    disease_node = disease
                    if not self.G.has_node(disease_node):
                        self.G.add_node(disease_node, type='disease')
                    if not self.G.has_node(ingredient):
                        self.G.add_node(ingredient, type='ingredient')
                    # Add edge with effect and reason as attributes
                    self.G.add_edge(ingredient, disease_node, relation='ingredient_disease', effect=effect, reason=reason)

            # Build a dictionary mapping normalized (strip+lower) menu title strings to their corresponding node in the graph
            self.menu_node_dict = {str(n).strip().lower(): n for n, attrs in self.G.nodes(data=True) if attrs.get('type') == 'menu'}
            # Build a dictionary mapping normalized (strip+lower) ingredient strings to their corresponding node in the graph
            self.ingredient_node_dict = {str(n).strip().lower(): n for n, attrs in self.G.nodes(data=True) if attrs.get('type') == 'ingredient'}
            # Build a dictionary mapping normalized (strip+lower) disease strings to their corresponding node in the graph
            self.disease_node_dict = {str(n).strip().lower(): n for n, attrs in self.G.nodes(data=True) if attrs.get('type') == 'disease'}


    @staticmethod
    def visualize_menu_ingredient_disease_graph(graph, top_n_menus=5):
                # Node color mapping
                node_type_color_map = {
                    'menu': '#1f77b4',        # blue
                    'ingredient': "#C7E6EE",  # green
                    'disease': "#d62796"      # red
                }
                # Edge color mapping for ingredient-disease links
                effect_color_map = {
                    'positive': "#19f336",       # cyan
                    'negative': '#ff7f0e',       # orange
                    'very negative': "#ff0101"   # purple
                }
                # Edge color for menu-ingredient links
                menu_ingredient_edge_color = '#7f7f7f'  # gray
                # Filter menu nodes to top_n_menus
                all_menu_nodes = [n for n, attrs in graph.nodes(data=True) if attrs.get('type') == 'menu']
                top_menu_nodes = all_menu_nodes[:top_n_menus]

                # Find ingredient nodes connected to these menu nodes
                ingredient_nodes = set()
                for menu in top_menu_nodes:
                    for neighbor in graph.neighbors(menu):
                        if graph.nodes[neighbor].get('type') == 'ingredient':
                            ingredient_nodes.add(neighbor)
                ingredient_nodes = list(ingredient_nodes)

                # Find disease nodes connected to these ingredient nodes
                disease_nodes = set()
                for ingredient in ingredient_nodes:
                    for neighbor in graph.neighbors(ingredient):
                        if graph.nodes[neighbor].get('type') == 'disease':
                            # Only add if there is a non-neutral effect edge
                            edge_data = graph.get_edge_data(ingredient, neighbor)
                            effect = edge_data.get('effect', '').lower() if edge_data else ''
                            if effect in {'positive', 'negative', 'very negative'}:
                                disease_nodes.add(neighbor)
                disease_nodes = list(disease_nodes)

                # Build filtered subgraph
                filtered_nodes = set(top_menu_nodes) | set(ingredient_nodes) | set(disease_nodes)
                filtered_edges = []
                for u, v, d in graph.edges(data=True):
                    if u in filtered_nodes and v in filtered_nodes:
                        u_type = graph.nodes[u].get('type')
                        v_type = graph.nodes[v].get('type')
                        if (
                            (u_type == 'ingredient' and v_type == 'disease') or
                            (u_type == 'disease' and v_type == 'ingredient')
                        ):
                            effect = d.get('effect', '').lower()
                            if effect not in {'positive', 'negative', 'very negative'}:
                                continue  # skip this edge
                        filtered_edges.append((u, v, d))
                filteredG = nx.Graph()
                for node in filtered_nodes:
                    filteredG.add_node(node, **graph.nodes[node])
                for u, v, d in filtered_edges:
                    filteredG.add_edge(u, v, **d)

                # Assign node colors and positions
                node_positions = {}
                menu_y = []
                ingredient_y = []
                disease_y = []

                def get_y_positions(num, min_y=-5, max_y=5):
                    if num == 1:
                        return [0]
                    step = (max_y - min_y) / (num - 1)
                    return [min_y + i * step for i in range(num)]

                menu_y = get_y_positions(len(top_menu_nodes), min_y=-5, max_y=5)
                ingredient_y = get_y_positions(len(ingredient_nodes), min_y=-5, max_y=5)
                disease_y = get_y_positions(len(disease_nodes), min_y=-5, max_y=5)

                for idx, node in enumerate(top_menu_nodes):
                    node_positions[node] = (0, menu_y[idx])
                for idx, node in enumerate(ingredient_nodes):
                    node_positions[node] = (1, ingredient_y[idx])
                for idx, node in enumerate(disease_nodes):
                    node_positions[node] = (2, disease_y[idx])

                # Fallback for any other node types (should not be present)
                other_nodes = set(filteredG.nodes()) - set(top_menu_nodes) - set(ingredient_nodes) - set(disease_nodes)
                for node in other_nodes:
                    node_positions[node] = (1, 0)

                # Assign node colors in the order of filteredG.nodes()
                node_colors = []
                for node in filteredG.nodes():
                    node_type = filteredG.nodes[node].get('type')
                    node_colors.append(node_type_color_map.get(node_type, '#cccccc'))

                # Assign node sizes and font sizes
                node_sizes = []
                font_sizes = []
                for node in filteredG.nodes():
                    node_type = filteredG.nodes[node].get('type')
                    if node_type == 'disease':
                        node_sizes.append(2400)
                        font_sizes.append(16)
                    elif node_type == 'ingredient':
                        node_sizes.append(175)
                        font_sizes.append(8)
                    elif node_type == 'menu':
                        node_sizes.append(300)
                        font_sizes.append(11)
                    else:
                        node_sizes.append(400)
                        font_sizes.append(10)

                # Assign edge colors in the order of filteredG.edges()
                edge_colors = []
                for u, v, d in filteredG.edges(data=True):
                    if (filteredG.nodes[u].get('type') == 'menu' and filteredG.nodes[v].get('type') == 'ingredient') or \
                        (filteredG.nodes[v].get('type') == 'menu' and filteredG.nodes[u].get('type') == 'ingredient'):
                        edge_colors.append(menu_ingredient_edge_color)
                    elif (filteredG.nodes[u].get('type') == 'ingredient' and filteredG.nodes[v].get('type') == 'disease') or \
                            (filteredG.nodes[v].get('type') == 'ingredient' and filteredG.nodes[u].get('type') == 'disease'):
                        effect = d.get('effect', '').lower()
                        edge_colors.append(effect_color_map.get(effect, '#cccccc'))
                    else:
                        edge_colors.append('#cccccc')

                # Draw the graph
                plt.figure(figsize=(18, 10))
                nx.draw(
                    filteredG, node_positions,
                    with_labels=True,
                    node_color=node_colors,
                    node_size=node_sizes,
                    font_size=9,
                    edge_color=edge_colors,
                    width=2
                )
                plt.title('Menu → Ingredient → Disease (Non-Neutral Effects)')
                plt.axis('off')

                # Legend
                import matplotlib.patches as mpatches
                import matplotlib.lines as mlines

                node_legend = [
                    mpatches.Patch(color=node_type_color_map['menu'], label='Menu Title Node'),
                    mpatches.Patch(color=node_type_color_map['ingredient'], label='Ingredient Node'),
                    mpatches.Patch(color=node_type_color_map['disease'], label='Disease Node')
                ]
                edge_legend = [
                    mlines.Line2D([], [], color=menu_ingredient_edge_color, linewidth=3, label='Menu → Ingredient'),
                    mlines.Line2D([], [], color=effect_color_map['positive'], linewidth=3, label='Ingredient → Disease (Positive)'),
                    mlines.Line2D([], [], color=effect_color_map['negative'], linewidth=3, label='Ingredient → Disease (Negative)'),
                    mlines.Line2D([], [], color=effect_color_map['very negative'], linewidth=3, label='Ingredient → Disease (Very Negative)')
                ]
                plt.legend(
                    handles=node_legend + edge_legend,
                    loc='upper right',
                    bbox_to_anchor=(1, 0.75),
                    fontsize=11,
                    frameon=True
                )
                plt.show()

    def find_best_matched_menu_in_graph(self, menu_title):
        '''Performs matching in the following order:
        1. Case-insensitive exact match
        2. AI-powered semantic matching using Gemini model
            menu_title (str): The input menu title to find a match for in the graph
            dict: A dictionary containing:
                - matched_menu (str or None): The best matched menu title found, or None if no match
                - is_exact (bool): True if an exact match was found, False otherwise
        Notes:
            - Uses Google's Gemini AI model as fallback when exact match fails
            - The Gemini model compares ingredient lists to find semantically similar menus
            - Returns None if no suitable match is found through any method'''
                
        # First, try exact match (case-insensitive)
        matched_menu = None
        menu_title = menu_title.strip().lower()
        is_exact = False
        if menu_title in self.menu_nodes:
            matched_menu = menu_title
            is_exact = True
        # If not in graph, cannot compare, so return None
        if not matched_menu:
            # Build a list of menu titles and their ingredient lists for Gemini
            prompt = (
                f"You are given an input menu title and its ingredient list, and a list of menu titles with their ingredient lists. "
                f"Find the menu title from the list whose ingredients are most similar to the input. "
                f"Return ONLY the best matched menu title as a string. If no menu is sufficiently similar in terms of ingredients, return an empty string.\n"
                f"Input menu: '{menu_title}'\n"
                f"Menu list: {json.dumps(self.menu_nodes)}"
            )
            response = generate_response_gemini(prompt)
            matched_menu = None
            is_exact = False
            if response:
                # Try to extract the matched menu title from the response
                match = re.search(r"'([^']+)'|\"([^\"]+)\"", response)
                if match:
                    matched_menu = match.group(1) or match.group(2)
                    if matched_menu and matched_menu in self.menu_node_dict:
                        is_exact = False
                    else:
                        matched_menu = None
                elif response.strip() in self.menu_node_dict:
                    matched_menu = response.strip()
                    is_exact = False
                else:
                    matched_menu = None
            else:
                matched_menu = None
                is_exact = False

        if not matched_menu:
            return {
                'matched_menu': None,
                'is_exact': False,
                'ingredients': [],
                'ingredient_disease_edges': []
            }

        print_ingredient = False
        if print_ingredient:
            # Get ingredients connected to the matched menu
            ingredients = [
                n for n in self.G.neighbors(self.menu_node_dict[matched_menu])
                if self.G.nodes[n].get('type') == 'ingredient'
            ]

            # For each ingredient, get edges to disease nodes with effect/reason
            ingredient_disease_edges = []
            for ing in ingredients:
                for neighbor in self.G.neighbors(ing):
                    if self.G.nodes[neighbor].get('type') == 'disease':
                        edge_data = self.G.get_edge_data(ing, neighbor)
                        ingredient_disease_edges.append({
                            'ingredient': ing,
                            'disease': neighbor,
                            'effect': edge_data.get('effect', ''),
                            'reason': edge_data.get('reason', '')
                        })

        return {
            'matched_menu': matched_menu,
            'is_exact': is_exact
        }

    def get_menu_node_from_string(self, menu_string):
        """
        Given a menu string (case-insensitive), returns the corresponding node in the graph.
        If not found, returns null.
        """
        menu_key = str(menu_string).strip().lower()
        return self.menu_node_dict.get(menu_key, None) if menu_key in self.menu_node_dict else None

    def get_disease_node_from_string(self, disease_string):
        """
        Given a disease string (case-insensitive), returns the corresponding node in the graph.
        If not found, returns null.
        """
        disease_key = str(disease_string).strip().lower()
        return self.disease_node_dict.get(disease_key, None) if disease_key in self.disease_node_dict else None

    def get_ingredient_node_from_string(self, ingredient_string):
        """
        Given an ingredient string (case-insensitive), returns the corresponding node in the graph.
        If not found, returns null.
        """
        ingredient_key = str(ingredient_string).strip().lower()
        return self.ingredient_node_dict.get(ingredient_key, None) if ingredient_key in self.ingredient_node_dict else None

