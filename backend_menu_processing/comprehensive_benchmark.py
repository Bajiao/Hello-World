"""
Comprehensive Benchmark: Graph-based vs LLM-based Menu Recommendations
Runs 5 iterations with different random samples, calculates statistics,
and creates visualizations comparing both methods.
"""

import os
import json
import random
import argparse
import time
from typing import List, Dict, Any
import numpy as np
from datetime import datetime

from menu_ingredient_disease_graph import MenuIngredientDiseaseGraph

# Import centralized LLM functions
from llm import (
    load_env_variables,
    get_openai_client,
    get_gemini_client,
    generate_response_gemini,
    rank_menus_openai,
    judge_rankings_gemini,
    get_project_root
)

# Load environment and initialize APIs
load_env_variables()
client = get_openai_client()
get_gemini_client()


class BenchmarkResults:
    """Store benchmark results across multiple iterations."""
    
    def __init__(self):
        self.iterations = []
        self.graph_times = []
        self.llm_times = []
        self.judge_times_ab = []
        self.judge_times_ba = []
        self.total_times = []
        
    def add_iteration(self, iteration_data: Dict[str, Any]):
        """Add results from one iteration."""
        self.iterations.append(iteration_data)
        self.graph_times.append(iteration_data['graph_time'])
        self.llm_times.append(iteration_data['llm_time'])
        self.judge_times_ab.append(iteration_data['judge_time_ab'])
        self.judge_times_ba.append(iteration_data['judge_time_ba'])
        self.total_times.append(iteration_data['total_time'])
    
    def get_statistics(self) -> Dict[str, Dict[str, float]]:
        """Calculate statistics across all iterations."""
        stats = {}
        
        for name, data in [
            ('graph_time', self.graph_times),
            ('llm_time', self.llm_times),
            ('judge_time_ab', self.judge_times_ab),
            ('judge_time_ba', self.judge_times_ba),
            ('total_time', self.total_times)
        ]:
            if data:
                stats[name] = {
                    'mean': np.mean(data),
                    'median': np.median(data),
                    'std': np.std(data),
                    'min': np.min(data),
                    'max': np.max(data),
                    'q25': np.percentile(data, 25),
                    'q75': np.percentile(data, 75),
                    'data': data
                }
        
        return stats
    
    def save_verdicts(self, filename='benchmark_verdicts_cache.json'):
        """Save verdict data for chart regeneration without rerunning LLM calls."""
        verdict_data = []
        for iteration in self.iterations:
            verdict_data.append({
                'iteration': iteration.get('iteration'),
                'verdict_ab': iteration.get('verdict_ab'),
                'verdict_ba': iteration.get('verdict_ba')
            })
        
        with open(filename, 'w') as f:
            json.dump(verdict_data, f, indent=2)
        print(f"✓ Verdict cache saved to {filename}")
    
    @staticmethod
    def load_verdicts(filename='benchmark_verdicts_cache.json'):
        """Load verdict data for chart regeneration."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None



def sample_menus(graph: MenuIngredientDiseaseGraph, n=25, seed=None):
    """Sample random menus from the graph. Only returns menus that have ingredients."""
    menus = [node for node, attrs in graph.G.nodes(data=True) 
             if attrs.get('type') == 'menu']
    
    # Filter to only menus that have ingredients in the graph
    valid_menus = []
    for menu in menus:
        try:
            ingredients = graph.get_ingredient_neighbors_of_menu(menu)
            if ingredients:  # Only include menus with ingredients
                valid_menus.append(menu)
        except Exception:
            pass  # Skip menus that cause errors
    
    if seed is not None:
        random.seed(seed)
    if len(valid_menus) <= n:
        return valid_menus
    return random.sample(valid_menus, n)


def get_menu_ingredients(graph: MenuIngredientDiseaseGraph, menu_node):
    """Get ingredients for a menu. Returns empty list if menu not in graph."""
    try:
        ingredients = graph.get_ingredient_neighbors_of_menu(menu_node)
        return sorted(list(ingredients))
    except Exception:
        # Menu not in graph, return empty list
        return []


def print_judge_verdict_summary(results_obj):
    """Print detailed summary of judge verdicts across ALL iterations."""
    if results_obj is None or not results_obj.iterations:
        return
    
    # Analyze verdict consistency across all iterations (sample sets)
    graph_consistent_wins = 0  # Both A→B and B→A agree Graph wins
    llm_consistent_wins = 0    # Both A→B and B→A agree LLM wins
    uncertain = 0              # A→B and B→A disagree
    
    graph_scores_ab = []
    graph_scores_ba = []
    llm_scores_ab = []
    llm_scores_ba = []
    
    import re
    for i, iteration in enumerate(results_obj.iterations, 1):
        verdict_ab = iteration.get('verdict_ab', '')
        verdict_ba = iteration.get('verdict_ba', '')
        
        # Extract scores
        score_ab_match = re.search(r'SCORE:\s*(\d+)', verdict_ab)
        score_ba_match = re.search(r'SCORE:\s*(\d+)', verdict_ba)
        score_ab = int(score_ab_match.group(1)) if score_ab_match else 5
        score_ba = int(score_ba_match.group(1)) if score_ba_match else 5
        
        # Determine winners from verdicts
        ab_winner = None
        ba_winner = None
        
        if 'WINNER: A' in verdict_ab:
            ab_winner = 'Graph'
            graph_scores_ab.append(score_ab)
        elif 'WINNER: B' in verdict_ab:
            ab_winner = 'LLM'
            llm_scores_ab.append(score_ab)
        
        if 'WINNER: A' in verdict_ba:
            ba_winner = 'LLM'  # Note: A is LLM in B→A test
            llm_scores_ba.append(score_ba)
        elif 'WINNER: B' in verdict_ba:
            ba_winner = 'Graph'  # Note: B is Graph in B→A test
            graph_scores_ba.append(score_ba)
        
        # Check consistency
        if ab_winner == ba_winner:
            if ab_winner == 'Graph':
                graph_consistent_wins += 1
            elif ab_winner == 'LLM':
                llm_consistent_wins += 1
        else:
            uncertain += 1
    
    total_iterations = len(results_obj.iterations)
    
    print(f"\n{'='*80}")
    print(f"JUDGE VERDICT SUMMARY - ACROSS ALL {total_iterations} SAMPLE SETS")
    print(f"{'='*80}\n")
    
    print(f"Verdict Consistency (A→B vs B→A agreement):")
    print(f"  Graph Consistent Wins: {graph_consistent_wins}/{total_iterations} ({graph_consistent_wins/total_iterations*100:.1f}%)")
    print(f"  LLM Consistent Wins:   {llm_consistent_wins}/{total_iterations} ({llm_consistent_wins/total_iterations*100:.1f}%)")
    print(f"  Uncertain/Disagree:    {uncertain}/{total_iterations} ({uncertain/total_iterations*100:.1f}%)")
    
    # Calculate average scores
    avg_graph_score = (sum(graph_scores_ab) + sum(graph_scores_ba)) / (len(graph_scores_ab) + len(graph_scores_ba)) if (graph_scores_ab or graph_scores_ba) else 5
    avg_llm_score = (sum(llm_scores_ab) + sum(llm_scores_ba)) / (len(llm_scores_ab) + len(llm_scores_ba)) if (llm_scores_ab or llm_scores_ba) else 5
    
    print(f"\nAverage Judge Confidence Scores (0-10 scale):")
    print(f"  Graph Method: {avg_graph_score:.2f} ({len(graph_scores_ab) + len(graph_scores_ba)} verdicts)")
    print(f"  LLM Method:   {avg_llm_score:.2f} ({len(llm_scores_ab) + len(llm_scores_ba)} verdicts)")
    
    # Overall verdict
    if graph_consistent_wins > llm_consistent_wins:
        print(f"\n🏆 OVERALL: GRAPH METHOD WINS ({graph_consistent_wins} consistent wins vs {llm_consistent_wins})")
    elif llm_consistent_wins > graph_consistent_wins:
        print(f"\n🏆 OVERALL: LLM METHOD WINS ({llm_consistent_wins} consistent wins vs {graph_consistent_wins})")
    else:
        print(f"\n🤝 OVERALL: TIED ({graph_consistent_wins} consistent wins each)")
    


    




def graph_rank_menus(graph: MenuIngredientDiseaseGraph, menus, disease, top_k=10) -> tuple:
    """Rank menus using graph method. Returns (results, time_taken)."""
    start_time = time.time()
    
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
        
        score = 3 * very_neg + 1 * neg - 1 * pos
        results.append({
            "menu": menu,
            "score": score,
            "very_negative": very_neg,
            "negative": neg,
            "positive": pos,
            "breakdown": breakdown,
            "ingredients": get_menu_ingredients(graph, menu)
        })
    
    results.sort(key=lambda r: r["score"], reverse=True)
    elapsed = time.time() - start_time
    
    return results[:top_k], elapsed


def llm_rank_menus(client, graph: MenuIngredientDiseaseGraph, 
                   menus, disease, top_k=10) -> tuple:
    """Rank menus using LLM. Returns (results, time_taken).
    
    NOTE: LLM is NOT provided with ingredients. It only ranks the menus by disease,
    then returns reasoning that explains ingredients to help patients understand.
    Uses centralized rank_menus_openai function from llm.py
    """
    start_time = time.time()
    
    # Prepare menus with generic ingredient handling
    menus_with_ingredients = [
        {"menu": m, "ingredients": get_menu_ingredients(graph, m)}
        for m in menus
    ]
    
    try:
        # Use centralized function
        arr = rank_menus_openai(client, menus_with_ingredients, disease, top_k)
        if not arr:
            elapsed = time.time() - start_time
            return graph_rank_menus(graph, menus, disease, top_k=top_k)[0], elapsed
    except Exception as e:
        print(f"  ⚠️  LLM call failed: {str(e)}")
        elapsed = time.time() - start_time
        return graph_rank_menus(graph, menus, disease, top_k=top_k)[0], elapsed
    
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
    elapsed = time.time() - start_time
    
    return normalized[:top_k], elapsed



def gemini_judge_ab(graph: MenuIngredientDiseaseGraph, disease, menus, 
                   graph_ranked, llm_ranked) -> tuple:
    """Judge comparing Graph (A) vs LLM (B). Returns (verdict, time_taken).
    
    The judge is provided with:
    - 25 menu items
    - ingredients for each item
    - disease
    
    This ensures the judge has full context for fair comparison.
    """
    start_time = time.time()
    
    # Prepare full menu data with ingredients for the judge
    menu_data = []
    for m in menus:
        ingredients = get_menu_ingredients(graph, m)
        menu_data.append({"menu": m, "ingredients": ingredients})
    
    top_graph = graph_ranked[:5]
    top_llm = llm_ranked[:5]
    
    prompt_text = f"""You are a neutral expert judge in nutrition and clinical medicine. 
The target disease is: '{disease}'.

FULL MENU DATA (all ingredients for reference):
{json.dumps(menu_data, ensure_ascii=False, indent=2)}

RANKING A (GRAPH-BASED) - Top 5 not recommended:
{json.dumps(top_graph, ensure_ascii=False, indent=2)}

RANKING B (LLM-BASED) - Top 5 not recommended:
{json.dumps(top_llm, ensure_ascii=False, indent=2)}

TASK: Evaluate which ranking is better at identifying NOT RECOMMENDED menus for {disease} patients.
Consider the ingredients, clinical knowledge, and ranking quality.

Respond ONLY with:
- WINNER: A or B
- SCORE: 1-10 (how much better is the winner, where 5 = equal)
- REASON: One sentence why"""
    
    try:
        verdict = generate_response_gemini(prompt_text)
    except Exception as e:
        print(f"  ⚠️  Judge A→B failed: {str(e)}")
        verdict = "Could not judge due to API error"
    
    elapsed = time.time() - start_time
    return verdict, elapsed


def gemini_judge_ba(graph: MenuIngredientDiseaseGraph, disease, menus, 
                   llm_ranked, graph_ranked) -> tuple:
    """Judge comparing LLM (A) vs Graph (B) [reversed order]. Returns (verdict, time_taken).
    
    Called TWICE to check consistency and remove bias from sequence.
    Same data but reversed order to ensure conclusion is consistent.
    """
    start_time = time.time()
    
    # Prepare full menu data with ingredients for the judge
    menu_data = []
    for m in menus:
        ingredients = get_menu_ingredients(graph, m)
        menu_data.append({"menu": m, "ingredients": ingredients})
    
    top_llm = llm_ranked[:5]
    top_graph = graph_ranked[:5]
    
    prompt_text = f"""You are a neutral expert judge in nutrition and clinical medicine. 
The target disease is: '{disease}'.

FULL MENU DATA (all ingredients for reference):
{json.dumps(menu_data, ensure_ascii=False, indent=2)}

RANKING A (LLM-BASED) - Top 5 not recommended:
{json.dumps(top_llm, ensure_ascii=False, indent=2)}

RANKING B (GRAPH-BASED) - Top 5 not recommended:
{json.dumps(top_graph, ensure_ascii=False, indent=2)}

TASK: Evaluate which ranking is better at identifying NOT RECOMMENDED menus for {disease} patients.
Consider the ingredients, clinical knowledge, and ranking quality.

Respond ONLY with:
- WINNER: A or B
- SCORE: 1-10 (how much better is the winner, where 5 = equal)
- REASON: One sentence why"""
    
    try:
        verdict = generate_response_gemini(prompt_text)
    except Exception as e:
        print(f"  ⚠️  Judge B→A failed: {str(e)}")
        verdict = "Could not judge due to API error"
    
    elapsed = time.time() - start_time
    return verdict, elapsed


def run_iteration(graph: MenuIngredientDiseaseGraph, disease: str, 
                 iteration_num: int, sample_size: int = 25, 
                 top_k: int = 10, seed: int = None) -> Dict[str, Any]:
    """Run one complete iteration of benchmarking."""
    
    print(f"\n{'='*80}")
    print(f"Iteration {iteration_num}: Sampling {sample_size} menus")
    print(f"{'='*80}")
    
    iteration_start = time.time()
    
    # Sample menus
    if seed is not None:
        seed = seed + iteration_num  # Make each iteration different
    menus_sample = sample_menus(graph, n=sample_size, seed=seed)
    print(f"  ✓ Sampled {len(menus_sample)} menus")
    
    # Graph ranking
    print(f"  ► Running graph-based ranking...")
    graph_results, graph_time = graph_rank_menus(graph, menus_sample, disease, top_k=top_k)
    print(f"    ✓ Graph ranking complete in {graph_time:.3f}s")
    
    # LLM ranking
    print(f"  ► Running LLM-based ranking...")
    llm_results, llm_time = llm_rank_menus(client, graph, menus_sample, disease, top_k=top_k)
    print(f"    ✓ LLM ranking complete in {llm_time:.3f}s")
    
    # Judge A→B (Graph vs LLM)
    print(f"  ► Gemini Judge (Graph vs LLM)...")
    verdict_ab, judge_time_ab = gemini_judge_ab(graph, disease, menus_sample, graph_results, llm_results)
    print(f"    ✓ Judge A→B complete in {judge_time_ab:.3f}s")
    
    # Judge B→A (LLM vs Graph) - reversed
    print(f"  ► Gemini Judge (LLM vs Graph) [reversed]...")
    verdict_ba, judge_time_ba = gemini_judge_ba(graph, disease, menus_sample, llm_results, graph_results)
    print(f"    ✓ Judge B→A complete in {judge_time_ba:.3f}s")
    
    total_time = time.time() - iteration_start
    
    return {
        'iteration': iteration_num,
        'sample_size': sample_size,
        'graph_time': graph_time,
        'llm_time': llm_time,
        'judge_time_ab': judge_time_ab,
        'judge_time_ba': judge_time_ba,
        'total_time': total_time,
        'graph_results': graph_results,
        'llm_results': llm_results,
        'verdict_ab': verdict_ab,
        'verdict_ba': verdict_ba
    }


def main(args):
    """Run comprehensive benchmark."""
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE BENCHMARK: Graph vs LLM Menu Recommendations")
    print(f"{'='*80}")
    print(f"Disease: {args.disease}")
    print(f"Iterations: {args.iterations}")
    print(f"Sample Size: {args.sample}")
    print(f"Top-K: {args.top}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize graph
    graph = MenuIngredientDiseaseGraph()
    print(f"✓ Graph loaded")
    
    # Run iterations
    results = BenchmarkResults()
    for i in range(1, args.iterations + 1):
        iteration_data = run_iteration(graph, args.disease, i, 
                                      sample_size=args.sample, 
                                      top_k=args.top,
                                      seed=args.seed)
        results.add_iteration(iteration_data)
    
    # Save raw results
    with open('benchmark_results_detailed.json', 'w') as f:
        json.dump(results.iterations, f, indent=2, default=str)
    print(f"\n✓ Detailed results saved to benchmark_results_detailed.json")
    
    # Save verdicts separately for chart regeneration
    results.save_verdicts()
    
    # Calculate statistics
    stats = results.get_statistics()
    
    # Save statistics
    stats_summary = {k: {kk: float(vv) if isinstance(vv, (int, float, np.number)) else vv 
                         for kk, vv in v.items() if kk != 'data'}
                    for k, v in stats.items()}
    
    with open('benchmark_statistics.json', 'w') as f:
        json.dump(stats_summary, f, indent=2)
    print(f"✓ Statistics saved to benchmark_statistics.json")
    
    # Print statistics
    print(f"\n{'='*80}")
    print(f"STATISTICS ACROSS {args.iterations} ITERATIONS")
    print(f"{'='*80}\n")
    
    print("TIME STATISTICS (seconds):\n")
    print(f"{'Metric':<25} {'Mean':<10} {'Median':<10} {'Std':<10} {'Min':<10} {'Max':<10}")
    print("-" * 65)
    
    for metric_name in ['graph_time', 'llm_time', 'judge_time_ab', 'judge_time_ba', 'total_time']:
        if metric_name in stats:
            s = stats[metric_name]
            display_name = {
                'graph_time': 'Graph Ranking',
                'llm_time': 'LLM Ranking',
                'judge_time_ab': 'Judge (A→B)',
                'judge_time_ba': 'Judge (B→A)',
                'total_time': 'Total Time'
            }[metric_name]
            print(f"{display_name:<25} {s['mean']:<10.4f} {s['median']:<10.4f} {s['std']:<10.4f} {s['min']:<10.4f} {s['max']:<10.4f}")
    
    # Calculate speedup
    if stats['graph_time']['mean'] > 0 and stats['llm_time']['mean'] > 0:
        speedup = stats['llm_time']['mean'] / stats['graph_time']['mean']
        print(f"\n{'Graph Speedup vs LLM':<25} {speedup:.2f}x faster")
    
    # Create visualizations
    print(f"\n{'='*80}")
    print(f"GENERATING VISUALIZATIONS...")
    print(f"{'='*80}\n")
    
    create_visualizations(stats, args.iterations, results)
    
    print(f"✓ Boxplot saved to benchmark_boxplot.png")
    print(f"✓ Time comparison saved to benchmark_timeplot.png")
    print(f"✓ Scatter plot saved to benchmark_scatter.png")
    print(f"✓ Distribution saved to benchmark_distribution.png")
    
    # Print judge verdict summary
    print(f"\n{'='*80}")
    print(f"JUDGE VERDICT SUMMARY")
    print(f"{'='*80}\n")
    print_judge_verdict_summary(results)
    
    print(f"\n{'='*80}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*80}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def create_visualizations(stats: Dict, iterations: int, results_obj=None):
    """Create visualizations of benchmark results."""
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError:
        print("  ⚠️  matplotlib/seaborn not installed. Skipping visualizations.")
        return
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (14, 10)
    
    # Extract judge verdict data
    graph_wins_ab = 0  # A→B: Graph is A
    llm_wins_ab = 0
    llm_wins_ba = 0    # B→A: LLM is A
    graph_wins_ba = 0
    ties = 0
    
    if results_obj is not None:
        for iteration in results_obj.iterations:
            verdict_ab = iteration.get('verdict_ab', '')
            verdict_ba = iteration.get('verdict_ba', '')
            
            # Parse A→B (Graph vs LLM)
            if 'WINNER: A' in verdict_ab:
                graph_wins_ab += 1
            elif 'WINNER: B' in verdict_ab:
                llm_wins_ab += 1
            
            # Parse B→A (LLM vs Graph)
            if 'WINNER: A' in verdict_ba:
                llm_wins_ba += 1
            elif 'WINNER: B' in verdict_ba:
                graph_wins_ba += 1
    
    total_graph_wins = graph_wins_ab + graph_wins_ba
    total_llm_wins = llm_wins_ab + llm_wins_ba
    consistent_agreements = 0
    
    if results_obj is not None:
        for iteration in results_obj.iterations:
            verdict_ab = iteration.get('verdict_ab', '')
            verdict_ba = iteration.get('verdict_ba', '')
            # Check if both tests agree Graph is better (A wins in both)
            if 'WINNER: A' in verdict_ab and 'WINNER: B' in verdict_ba:
                consistent_agreements += 1
    
    # 1. Boxplot - Time Comparison
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Benchmark Results: Graph vs LLM Menu Recommendations', fontsize=16, fontweight='bold')
    
    # Boxplot
    ax = axes[0, 0]
    data_for_box = [
        stats['graph_time']['data'],
        stats['llm_time']['data']
    ]
    bp = ax.boxplot(data_for_box, labels=['Graph\nRanking', 'LLM\nRanking'],
                    patch_artist=True, showmeans=True)
    for patch, color in zip(bp['boxes'], ['lightblue', 'lightcoral']):
        patch.set_facecolor(color)
    ax.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Execution Time Distribution (Log Scale)', fontsize=12, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3)
    
    # Time series
    ax = axes[0, 1]
    iterations_range = range(1, iterations + 1)
    ax.plot(iterations_range, stats['graph_time']['data'], 'o-', label='Graph', linewidth=2, markersize=6)
    ax.plot(iterations_range, stats['llm_time']['data'], 's-', label='LLM', linewidth=2, markersize=6)
    ax.set_xlabel('Iteration', fontsize=11, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_title('Execution Time Across Iterations (Log Scale)', fontsize=12, fontweight='bold')
    ax.set_yscale('log')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Judge verdict panel - WINNER COMPARISON
    ax = axes[1, 0]
    
    # Create comparison data
    methods = ['Graph Wins', 'LLM Wins', 'Consistent\nAgreement']
    wins = [total_graph_wins, total_llm_wins, consistent_agreements]
    colors_verdict = ['#2E7D32', '#C62828', '#F57C00']  # Dark green, dark red, orange
    
    bars = ax.bar(methods, wins, color=colors_verdict, edgecolor='black', linewidth=2)
    ax.set_ylabel('Number of Wins', fontsize=12, fontweight='bold')
    ax.set_title(f'Judge Verdict Results: Who Wins?\n(Out of {iterations} iterations)', 
                 fontsize=13, fontweight='bold')
    ax.set_ylim(0, max(iterations, 1) + 0.5)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels and percentages on bars
    for bar, value in zip(bars, wins):
        height = bar.get_height()
        pct = (value / iterations * 100) if iterations > 0 else 0
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}\n({pct:.0f}%)', ha='center', va='bottom', 
                fontsize=11, fontweight='bold')
    
    # Add a text summary below
    if total_graph_wins > total_llm_wins:
        summary = f"✓ GRAPH METHOD WINS ({total_graph_wins} vs {total_llm_wins} wins)"
        color = '#2E7D32'
    elif total_llm_wins > total_graph_wins:
        summary = f"✓ LLM METHOD WINS ({total_llm_wins} vs {total_graph_wins} wins)"
        color = '#C62828'
    else:
        summary = f"= TIED ({total_graph_wins} wins each)"
        color = '#666666'
    
    ax.text(0.5, -0.25, summary, transform=ax.transAxes,
            ha='center', fontsize=12, fontweight='bold', 
            bbox=dict(boxstyle='round', facecolor=color, alpha=0.3, edgecolor='black', linewidth=2))
    
    # Total time distribution
    ax = axes[1, 1]
    ax.hist(stats['total_time']['data'], bins=8, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(stats['total_time']['mean'], color='red', linestyle='--', linewidth=2, label=f"Mean: {stats['total_time']['mean']:.3f}s")
    ax.axvline(stats['total_time']['median'], color='green', linestyle='--', linewidth=2, label=f"Median: {stats['total_time']['median']:.3f}s")
    ax.set_xlabel('Total Time (seconds)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax.set_title('Total Execution Time Distribution', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('benchmark_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Judge Verdicts Consistency Analysis - Bar Chart + Score Comparison
    if results_obj is not None and len(results_obj.iterations) > 0:
        # Analyze verdict consistency across all iterations (sample sets)
        graph_consistent_wins = 0  # Both A→B and B→A agree Graph wins
        llm_consistent_wins = 0    # Both A→B and B→A agree LLM wins
        uncertain = 0              # A→B and B→A disagree
        
        graph_scores = []  # Collect all Graph-favorable scores
        llm_scores = []    # Collect all LLM-favorable scores
        
        for iteration in results_obj.iterations:
            verdict_ab = iteration.get('verdict_ab', '')
            verdict_ba = iteration.get('verdict_ba', '')
            
            # Extract scores
            import re
            score_ab_match = re.search(r'SCORE:\s*(\d+)', verdict_ab)
            score_ba_match = re.search(r'SCORE:\s*(\d+)', verdict_ba)
            score_ab = int(score_ab_match.group(1)) if score_ab_match else 5
            score_ba = int(score_ba_match.group(1)) if score_ba_match else 5
            
            # Determine winners from verdicts
            ab_winner = None
            ba_winner = None
            
            if 'WINNER: A' in verdict_ab:
                ab_winner = 'Graph'
                graph_scores.append(score_ab)
            elif 'WINNER: B' in verdict_ab:
                ab_winner = 'LLM'
                llm_scores.append(score_ab)
            
            if 'WINNER: A' in verdict_ba:
                ba_winner = 'LLM'  # Note: A is LLM in B→A test
                llm_scores.append(score_ba)
            elif 'WINNER: B' in verdict_ba:
                ba_winner = 'Graph'  # Note: B is Graph in B→A test
                graph_scores.append(score_ba)
            
            # Check consistency
            if ab_winner == ba_winner:
                if ab_winner == 'Graph':
                    graph_consistent_wins += 1
                elif ab_winner == 'LLM':
                    llm_consistent_wins += 1
            else:
                uncertain += 1
        
        # Create figure with 2 subplots side by side
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Subplot 1: Consistency Category Bar Chart
        total_sets = len(results_obj.iterations)
        categories = ['Graph Wins\n(Consistent)', 'LLM Wins\n(Consistent)', 'Uncertain\n(Disagree)']
        values = [graph_consistent_wins, llm_consistent_wins, uncertain]
        colors = ['#2E7D32', '#C62828', '#FFA500']  # Green (Graph), Red (LLM), Orange (Uncertain)
        
        bars1 = ax1.bar(categories, values, color=colors, edgecolor='black', linewidth=2, width=0.6)
        ax1.set_ylabel('Number of Sample Sets', fontsize=12, fontweight='bold')
        ax1.set_title(f'Judge Verdict Consistency\n({total_sets} sets × 25 menus each)', 
                      fontsize=13, fontweight='bold', pad=15)
        ax1.set_ylim(0, max(total_sets, 1) + 1)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add percentage and count labels on bars
        for bar, value in zip(bars1, values):
            height = bar.get_height()
            pct = (value / total_sets * 100) if total_sets > 0 else 0
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(value)}\n({pct:.0f}%)', ha='center', va='bottom', 
                    fontsize=11, fontweight='bold')
        
        # Subplot 2: Average Judge Scores Comparison
        avg_graph_score = sum(graph_scores) / len(graph_scores) if graph_scores else 5
        avg_llm_score = sum(llm_scores) / len(llm_scores) if llm_scores else 5
        
        score_categories = ['Graph\nMethod', 'LLM\nMethod']
        score_values = [avg_graph_score, avg_llm_score]
        score_colors = ['#2E7D32', '#C62828']
        
        bars2 = ax2.bar(score_categories, score_values, color=score_colors, edgecolor='black', linewidth=2, width=0.5)
        ax2.set_ylabel('Average Judge Score', fontsize=12, fontweight='bold')
        ax2.set_title(f'Average Judge Confidence Score\n(0-10 scale)', 
                      fontsize=13, fontweight='bold', pad=15)
        ax2.set_ylim(0, 10)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add score labels on bars
        for bar, score in zip(bars2, score_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{score:.2f}', ha='center', va='bottom', 
                    fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('benchmark_judge_verdicts.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Judge verdicts comparison bar charts saved to benchmark_judge_verdicts.png")
    
    # 2. Bar chart - Mean times (only Graph and LLM, no judges)
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics = ['Graph\nRanking', 'LLM\nRanking']
    means = [
        stats['graph_time']['mean'],
        stats['llm_time']['mean']
    ]
    stds = [
        stats['graph_time']['std'],
        stats['llm_time']['std']
    ]
    colors = ['lightblue', 'lightcoral']
    bars = ax.bar(metrics, means, yerr=stds, capsize=10, color=colors, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Average Execution Time with Std Dev (Log Scale)', fontsize=13, fontweight='bold')
    ax.set_yscale('log')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{mean:.4f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('benchmark_timeplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Scatter - Graph vs LLM time
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.scatter(stats['graph_time']['data'], stats['llm_time']['data'], s=100, alpha=0.6, color='purple')
    ax.set_xlabel('Graph Ranking Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_ylabel('LLM Ranking Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Graph vs LLM Execution Time', fontsize=13, fontweight='bold')
    
    # Add diagonal line (equal performance)
    max_val = max(max(stats['graph_time']['data']), max(stats['llm_time']['data']))
    ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Equal Performance')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Distribution comparison (only Graph and LLM, no judges)
    fig, axes = plt.subplots(1, 1, figsize=(10, 5))
    
    axes.hist(stats['graph_time']['data'], bins=8, alpha=0.6, label='Graph', color='blue', edgecolor='black')
    axes.hist(stats['llm_time']['data'], bins=8, alpha=0.6, label='LLM', color='red', edgecolor='black')
    axes.set_xlabel('Time (seconds)', fontsize=11, fontweight='bold')
    axes.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    axes.set_title('Ranking Time Distribution (Log Scale)', fontsize=12, fontweight='bold')
    axes.set_xscale('log')
    axes.legend(fontsize=10)
    axes.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('benchmark_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comprehensive benchmark: Graph vs LLM recommendations")
    parser.add_argument("--disease", default="diabetes", help="Disease to benchmark")
    parser.add_argument("--iterations", type=int, default=20, help="Number of sample sets to evaluate")
    parser.add_argument("--sample", type=int, default=25, help="Sample size per iteration")
    parser.add_argument("--top", type=int, default=10, help="Top-K results")
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    args = parser.parse_args()
    main(args)
