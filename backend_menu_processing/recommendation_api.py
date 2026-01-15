"""
Simple API for Menu-Ingredient-Disease Recommendations.

Provides a clean interface to:
1. Rank menus by healthiness/unhealthiness for a disease
2. Get ingredient details for a menu
3. Get disease-specific recommendations
"""

import json
from typing import List, Dict, Any
from menu_ingredient_disease_graph import MenuIngredientDiseaseGraph


class MenuRecommendationAPI:
    """API for menu health recommendations based on disease."""
    
    def __init__(self):
        """Initialize the graph and knowledge base."""
        self.graph = MenuIngredientDiseaseGraph()
    
    def get_menus_for_disease(self, disease: str, top_n: int = 10, 
                             ranking: str = "unhealthy") -> List[Dict[str, Any]]:
        """
        Get ranked menus for a specific disease.
        
        Args:
            disease: Disease name (e.g., "diabetes", "cardiovascular disease", "kidney disease")
            top_n: Number of top results to return
            ranking: "unhealthy" for not-recommended, "healthy" for recommended
            
        Returns:
            List of dicts with menu, score, ingredients, and breakdown
        """
        disease_node = self.graph.get_disease_node_from_string(disease)
        if not disease_node:
            return []
        
        # Score all menus
        all_menus = [n for n, attrs in self.graph.G.nodes(data=True) 
                     if attrs.get('type') == 'menu']
        
        results = []
        for menu in all_menus:
            ing_nodes = self.graph.get_ingredient_neighbors_of_menu(menu)
            very_neg = 0
            neg = 0
            pos = 0
            breakdown = []
            
            for ing in ing_nodes:
                if self.graph.G.has_edge(ing, disease_node):
                    ed = self.graph.G.get_edge_data(ing, disease_node) or {}
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
            
            # Weighted scoring
            score = 3 * very_neg + 1 * neg - 1 * pos
            results.append({
                "menu": menu,
                "score": score,
                "very_negative_count": very_neg,
                "negative_count": neg,
                "positive_count": pos,
                "ingredients": sorted(list(ing_nodes)),
                "breakdown": breakdown
            })
        
        # Sort based on ranking type
        if ranking == "unhealthy":
            results.sort(key=lambda r: r["score"], reverse=True)
        else:  # healthy
            results.sort(key=lambda r: r["score"])
        
        return results[:top_n]
    
    def get_menu_details(self, menu_name: str, disease: str = None) -> Dict[str, Any]:
        """
        Get detailed information about a specific menu.
        
        Args:
            menu_name: Name of the menu
            disease: (Optional) Filter ingredient analysis by disease
            
        Returns:
            Dict with menu details, ingredients, and optional disease analysis
        """
        menu_node = self.graph.get_menu_node_from_string(menu_name)
        if not menu_node:
            return {"error": f"Menu '{menu_name}' not found"}
        
        ingredients = self.graph.get_ingredient_neighbors_of_menu(menu_node)
        
        result = {
            "menu": menu_node,
            "ingredients": sorted(list(ingredients)),
            "ingredient_count": len(ingredients)
        }
        
        # Optional disease analysis
        if disease:
            disease_node = self.graph.get_disease_node_from_string(disease)
            if disease_node:
                breakdown = []
                for ing in ingredients:
                    if self.graph.G.has_edge(ing, disease_node):
                        ed = self.graph.G.get_edge_data(ing, disease_node) or {}
                        breakdown.append({
                            "ingredient": ing,
                            "effect": ed.get('effect', 'neutral'),
                            "reason": ed.get('reason', '')
                        })
                result[f"disease_analysis_{disease}"] = breakdown
        
        return result
    
    def compare_menus(self, menu_names: List[str], disease: str) -> List[Dict[str, Any]]:
        """
        Compare multiple menus for a specific disease.
        
        Args:
            menu_names: List of menu names to compare
            disease: Disease to evaluate against
            
        Returns:
            List of dicts with menus ranked by healthiness
        """
        results = []
        disease_node = self.graph.get_disease_node_from_string(disease)
        
        if not disease_node:
            return []
        
        for menu_name in menu_names:
            menu_node = self.graph.get_menu_node_from_string(menu_name)
            if not menu_node:
                continue
            
            ing_nodes = self.graph.get_ingredient_neighbors_of_menu(menu_node)
            very_neg = 0
            neg = 0
            pos = 0
            
            for ing in ing_nodes:
                if self.graph.G.has_edge(ing, disease_node):
                    ed = self.graph.G.get_edge_data(ing, disease_node) or {}
                    effect = ed.get('effect', 'neutral').lower()
                    if effect == 'very negative':
                        very_neg += 1
                    elif effect == 'negative':
                        neg += 1
                    elif effect == 'positive':
                        pos += 1
            
            score = 3 * very_neg + 1 * neg - 1 * pos
            results.append({
                "menu": menu_node,
                "score": score,
                "very_negative": very_neg,
                "negative": neg,
                "positive": pos,
                "ingredients": sorted(list(ing_nodes))
            })
        
        # Sort by score (highest = most unhealthy)
        results.sort(key=lambda r: r["score"], reverse=True)
        return results
    
    def get_available_diseases(self) -> List[str]:
        """Get list of diseases in the knowledge graph."""
        diseases = [n for n, attrs in self.graph.G.nodes(data=True) 
                   if attrs.get('type') == 'disease']
        return sorted(diseases)
    
    def get_available_menus(self) -> List[str]:
        """Get list of all menus in the knowledge graph."""
        menus = [n for n, attrs in self.graph.G.nodes(data=True) 
                if attrs.get('type') == 'menu']
        return sorted(menus)


# Quick utility functions for easy access
def rank_menus_for_disease(disease: str, top_n: int = 10, 
                          unhealthy: bool = True) -> List[Dict[str, Any]]:
    """
    Quick function to rank menus for a disease.
    
    Example:
        results = rank_menus_for_disease("diabetes", top_n=10)
        for menu_rec in results:
            print(f"{menu_rec['menu']}: {menu_rec['score']}")
    """
    api = MenuRecommendationAPI()
    ranking = "unhealthy" if unhealthy else "healthy"
    return api.get_menus_for_disease(disease, top_n=top_n, ranking=ranking)


def get_menu_info(menu_name: str, disease: str = None) -> Dict[str, Any]:
    """Quick function to get menu details."""
    api = MenuRecommendationAPI()
    return api.get_menu_details(menu_name, disease)


def compare_menus(menu_names: List[str], disease: str) -> List[Dict[str, Any]]:
    """Quick function to compare menus."""
    api = MenuRecommendationAPI()
    return api.compare_menus(menu_names, disease)


if __name__ == "__main__":
    # Example usage
    api = MenuRecommendationAPI()
    
    print("Available diseases:", api.get_available_diseases())
    print()
    
    print("Top 10 UNHEALTHY menus for DIABETES:")
    print("=" * 60)
    results = api.get_menus_for_disease("diabetes", top_n=10, ranking="unhealthy")
    for i, rec in enumerate(results, 1):
        print(f"{i}. {rec['menu']} (score: {rec['score']})")
        print(f"   Very Negative: {rec['very_negative_count']}, "
              f"Negative: {rec['negative_count']}, "
              f"Positive: {rec['positive_count']}")
        print()
    
    print("\nCompare 3 menus for DIABETES:")
    print("=" * 60)
    comparison = api.compare_menus(
        ["Finnish Runeberg Tortes", "Swedish Spareribs", "Korean Street Toast"],
        disease="diabetes"
    )
    for rec in comparison:
        print(f"{rec['menu']}: Score {rec['score']} "
              f"(v_neg: {rec['very_negative']}, "
              f"neg: {rec['negative']}, "
              f"pos: {rec['positive']})")
