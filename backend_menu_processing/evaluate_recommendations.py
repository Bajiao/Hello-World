import os
import json
import random
import argparse
from pathlib import Path

from menu_ingredient_disease_graph import MenuIngredientDiseaseGraph

# Import centralized LLM functions
from llm import (
    load_env_variables,
    get_openai_client,
    get_gemini_client,
    generate_response_gemini,
    rank_menus_openai,
    judge_rankings_gemini
)

# Load environment and initialize APIs
load_env_variables()
client = get_openai_client()
get_gemini_client()

def sample_menus(graph: MenuIngredientDiseaseGraph, n=25, seed=42):
    menus = [n for n, attrs in graph.G.nodes(data=True) if attrs.get('type') == 'menu']
    random.seed(seed)
    if len(menus) <= n:
        return menus
    return random.sample(menus, n)

def get_menu_ingredients(graph: MenuIngredientDiseaseGraph, menu_node):
    """Return list of ingredient names for a menu node."""
    ingredients = graph.get_ingredient_neighbors_of_menu(menu_node)
    return sorted(list(ingredients))

def graph_rank_menus(graph: MenuIngredientDiseaseGraph, menus, disease, top_k=10):
    """Rank menus by unhealthy score derived from ingredient→disease edges.
       Format returned: list of dicts {menu, score, breakdown(list of ingredient effects/reasons)}"""
    disease_node = graph.get_disease_node_from_string(disease)
    results = []
    for menu in menus:
        ing_nodes = graph.get_ingredient_neighbors_of_menu(menu)
        very_neg = 0
        neg = 0
        pos = 0
        breakdown = []
        for ing in ing_nodes:
            if graph.G.has_edge(ing, disease_node):
                ed = graph.G.get_edge_data(ing, disease_node) or {}
                effect = ed.get('effect', 'neutral').lower()
                reason = ed.get('reason', '')
                if effect == 'very negative':
                    very_neg += 1
                    breakdown.append({"ingredient": ing, "effect": effect, "reason": reason})
                elif effect == 'negative':
                    neg += 1
                    breakdown.append({"ingredient": ing, "effect": effect, "reason": reason})
                elif effect == 'positive':
                    pos += 1
                    breakdown.append({"ingredient": ing, "effect": effect, "reason": reason})
        # simple scoring: very_negative weight 3, negative 1, positive -1
        score = 3 * very_neg + 1 * neg - 1 * pos
        results.append({"menu": menu, "score": score, "very_negative": very_neg, "negative": neg, "positive": pos, "breakdown": breakdown, "ingredients": get_menu_ingredients(graph, menu)})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]

def llm_rank_menus(client: OpenAI, graph: MenuIngredientDiseaseGraph, menus, disease, top_k=10):
    """Ask GPT-4o to rank menus by unhealthiness for disease.
       Provide for each menu the menu title and the ingredient list (ground truth) so LLM has full context.
       Expects model to return a JSON array of objects: {menu, score(0-100), reasoning}"""
    entries = []
    for m in menus:
        entries.append({"menu": m, "ingredients": get_menu_ingredients(graph, m)})
    
    try:
        # Use centralized function
        arr = rank_menus_openai(client, entries, disease, top_k)
        if not arr:
            print("  ⚠ LLM ranking failed. Using graph-based approximation instead.")
            return graph_rank_menus(graph, menus, disease, top_k=top_k)
    except Exception as e:
        print(f"  ⚠ LLM call failed ({str(e)[:60]}...). Using graph-based approximation instead.")
        return graph_rank_menus(graph, menus, disease, top_k=top_k)
    
    # Normalize results into expected shape and attach ingredients
    normalized = []
    for item in arr:
        menu = item.get("menu")
        score = float(item.get("score", 0))
        reasoning = item.get("reasoning", "")
        normalized.append({
            "menu": menu,
            "score": score,
            "reasoning": reasoning,
            "ingredients": get_menu_ingredients(graph, menu)
        })
    normalized.sort(key=lambda r: r["score"], reverse=True)
    return normalized[:top_k]

def gemini_judge(graph: MenuIngredientDiseaseGraph, disease, menus, graph_ranked, llm_ranked):
    """Ask Gemini to judge which ranking is better using ground-truth ingredient lists.
       Returns Gemini text response and writes to file."""
    # build context with ground-truth ingredients
    menu_gt = []
    for m in menus:
        menu_gt.append({"menu": m, "ingredients": get_menu_ingredients(graph, m)})
    
    # Create a simplified comparison focusing on top 5 instead of all
    top_graph = graph_ranked[:5]
    top_llm = llm_ranked[:5]
    
    payload = {
        "instruction": f"You are a neutral expert judge. The target disease is: '{disease}'. You are given:\n"
                       "1) Ground truth: for each menu the canonical ingredient list (do not invent ingredients).\n"
                       "2) Ranking A: results from METHOD A (graph-based). For each menu you have a score and reasoning.\n"
                       "3) Ranking B: results from METHOD B (LLM gpt-4o). For each menu you have a score and reasoning.\n\n"
                       "Task: Using ONLY the ground-truth ingredients as evidence, decide which ranking is better at identifying NOT RECOMMENDED menus for this disease. "
                       "Return a JSON object with keys: 'winner' (one of 'graph', 'gpt-4o', 'tie'), 'explanation' (short paragraph), 'differences' (list of up to 3 menu objects where methods disagree most). "
                       "Use clinical reasoning referencing specific ingredients. Do NOT include extra text.",
        "ground_truth": menu_gt[:10],  # Limit to top 10 menus to reduce token count
        "graph_ranking": top_graph,
        "llm_ranking": top_llm
    }
    # compose prompt text - simplified
    prompt_text = f"{payload['instruction']}\n\nGROUND_TRUTH (top 10 menus):\n{json.dumps(menu_gt[:10], ensure_ascii=False, indent=2)}\n\nGRAPH_RANKING (top 5):\n{json.dumps(top_graph, ensure_ascii=False, indent=2)}\n\nLLM_RANKING (top 5):\n{json.dumps(top_llm, ensure_ascii=False, indent=2)}"
    # call Gemini
    print("  Calling Gemini judge...")
    gemini_resp = generate_response_gemini(prompt_text)
    return gemini_resp

def main(args):
    graph = MenuIngredientDiseaseGraph()
    menus_sample = sample_menus(graph, n=args.sample, seed=args.seed)
    print(f"Sampled {len(menus_sample)} menus.")
    graph_results = graph_rank_menus(graph, menus_sample, args.disease, top_k=args.top)
    with open('graph_ranked.json', 'w', encoding='utf-8') as f:
        json.dump(graph_results, f, ensure_ascii=False, indent=2)
    print("✓ Graph ranking complete. Saved to graph_ranked.json")

    llm_results = llm_rank_menus(client, graph, menus_sample, args.disease, top_k=args.top)
    with open('llm_ranked.json', 'w', encoding='utf-8') as f:
        json.dump(llm_results, f, ensure_ascii=False, indent=2)
    print("✓ LLM ranking complete. Saved to llm_ranked.json")

    gemini_judgement = gemini_judge(graph, args.disease, menus_sample, graph_results, llm_results)
    with open('gemini_judgement.txt', 'w', encoding='utf-8') as f:
        f.write(gemini_judgement or "No response from Gemini")
    print("✓ Gemini judgement complete. Saved to gemini_judgement.txt")
    print("\nDone. Review outputs in current directory.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate graph-based vs LLM-based negative recommendation rankings")
    parser.add_argument("--disease", default="diabetes", help="Disease to evaluate")
    parser.add_argument("--sample", type=int, default=25, help="Number of menus to sample")
    parser.add_argument("--top", type=int, default=10, help="Top-K to produce")
    parser.add_argument("--seed", type=int, default=42, help="Sampling seed")
    args = parser.parse_args()
    main(args)
