"""
Full integration test: load saved analysis_results.json, apply first-candidate overrides, run customized condition analysis, and write resulting HTML to uploads folder.
"""
import json
import re
from pathlib import Path
import html as html_mod
import markdown
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend_menu_processing.recommendation_api import MenuRecommendationAPI

DEFAULT_ANALYSIS = Path(__file__).parent / 'templates' / 'uploads' / 'analysis_results.json'

def main(condition='diabetes', customQuestion=None, apply_overrides=True, analysis_path=None, out_path=None):
    analysis_path = Path(analysis_path) if analysis_path else DEFAULT_ANALYSIS
    out_path = Path(out_path) if out_path else (Path(__file__).parent / 'templates' / 'uploads' / 'full_test_recommendation.html')

    if not analysis_path.exists():
        print(f'No saved analysis_results.json found at {analysis_path}. Run upload first.')
        return
    data = json.loads(analysis_path.read_text())
    # If saved as {filename: {...}}
    if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), dict):
        inner = next(iter(data.values()))
    else:
        inner = data

    recipes = inner.get('recipes', [])
    matches = inner.get('matches', [])
    if not recipes:
        print('No recipes to analyze.')
        return

    # Apply overrides: select first candidate if available for each match (only if apply_overrides True)
    api = MenuRecommendationAPI()
    if apply_overrides:
        for m in matches:
            if m.get('candidates'):
                first = m['candidates'][0]
                # Use candidate_key and map to node
                ck = first.get('candidate_key')
                node = api.graph.menu_node_dict.get(ck)
                if node:
                    m['matched_menu'] = node
                    m['matched_key'] = ck
                    m['is_exact'] = False
                    m['user_override'] = True

    md = f"# Recommendations for {condition}\n\n"

    top_menus = api.get_menus_for_disease(condition, top_n=200, ranking='unhealthy')

    recipe_infos = []
    for idx, recipe in enumerate(recipes):
        info = {"recipe": recipe, "details": None, "breakdown": [], "vneg": 0, "neg": 0}
        matched = matches[idx] if idx < len(matches) else {'matched_menu': None, 'is_exact': False}
        matched_menu = matched.get('matched_menu')
        if matched_menu:
            details = api.get_menu_details(matched_menu, disease=condition)
            info['matched_closest'] = matched_menu
            info['is_exact'] = matched.get('is_exact', False)
        else:
            details = api.get_menu_details(recipe, disease=condition)
        info['details'] = details
        breakdown = details.get(f'disease_analysis_{condition}', []) if isinstance(details, dict) else []
        info['breakdown'] = breakdown
        info['vneg'] = sum(1 for b in breakdown if b.get('effect','').lower() == 'very negative')
        info['neg'] = sum(1 for b in breakdown if b.get('effect','').lower() == 'negative')
        recipe_infos.append(info)

    recipe_infos.sort(key=lambda r: (r['vneg'], r['neg']), reverse=True)

    for info in recipe_infos:
        recipe = info['recipe']
        details = info.get('details') or {}
        md += f"## {recipe}\n\n"
        if info.get('matched_closest'):
            md += f"- Closest match in knowledge graph: **{info['matched_closest']}** (exact={info.get('is_exact', False)})\n\n"
        if isinstance(details, dict) and details.get('error'):
            md += f"- Not found in knowledge graph: {details.get('error')}\n\n"
            match = next((m for m in top_menus if m['menu'].lower() == recipe.lower()), None)
            if match:
                md += f"- Matched in ranking: score {match['score']}\n\n"
            continue
        ingredients = details.get('ingredients', [])
        md += f"**Ingredients:** {', '.join(ingredients) if ingredients else 'N/A'}\n\n"
        breakdown = details.get(f'disease_analysis_{condition}', [])
        if breakdown:
            md += "**Knowledge Graph Reasoning:**\n"
            for b in breakdown:
                ingr = b.get('ingredient','')
                eff = b.get('effect','')
                reason = b.get('reason','')
                md += f"- **{ingr}** — {eff}. {reason}\n"
            md += "\n"
        else:
            md += "- No direct ingredient->disease links found in knowledge graph for this menu.\n\n"
        found = next((r for r in top_menus if r['menu'].lower() == details.get('menu','').lower()), None)
        if found:
            rank = next((i for i, r in enumerate(top_menus, 1) if r['menu'] == found['menu']), None)
            md += f"- Knowledge graph score: {found['score']}"
            if rank:
                md += f" (rank {rank} of {len(top_menus)})"
            md += "\n\n"
        vneg = info.get('vneg', 0)
        neg = info.get('neg', 0)
        if vneg > 0 or neg > 0:
            md += f"**ALERT:** This menu contains {vneg} very negative and {neg} negative ingredients for {condition}. Consider requesting modifications.\n\n"
        else:
            md += f"**Note:** No strongly negative ingredients detected for {condition}.\n\n"

    # Normalize markdown spacing similar to upload flow
    import re as _re
    md = md.replace('\r\n', '\n')
    md = _re.sub(r'[ \t]+\n', '\n', md)
    md = _re.sub(r'\n\s*\n+', '\n\n', md)
    md = _re.sub(r'(#{1,6} .*?)\n\s*\n+', r'\1\n\n', md)
    md = _re.sub(r'\n\s*\n(?=[*-]\s)', '\n', md)

    if customQuestion:
        try:
            from backend_menu_processing.llm import get_openai_client
            client = get_openai_client()
            prompt = f"You are a medical nutritionist. Context:\n{md}\nUser question: {customQuestion}\nProvide a concise answer focusing on actionable recommendations and concise alerts. Return plain text."
            resp = client.chat.completions.create(model='gpt5-nano', messages=[{'role':'user','content':prompt}], temperature=0.7)
            post = resp.choices[0].message.content
            md += "\n---\n### Additional Analysis\n\n" + post
        except Exception as e:
            print('gpt5-nano post-processing failed:', e)

        # Build compact HTML directly similar to runtime
        import html as _html
        html_parts = [f"<div class=\"rec-root\"><h1>Recommendations for { _html.escape(condition) }</h1>"]
        for info in recipe_infos:
            recipe = _html.escape(info['recipe'])
            details = info.get('details') or {}
            html_parts.append(f"<div class=\"rec-recipe\"><div class=\"rec-title\">{recipe}</div>")
            if info.get('matched_closest'):
                mc = _html.escape(info['matched_closest'])
                html_parts.append(f"<div class=\"rec-match\">Closest match: <strong>{mc}</strong> (exact={info.get('is_exact', False)})</div>")
            if isinstance(details, dict) and details.get('error'):
                html_parts.append(f"<div class=\"rec-error\">Not found in knowledge graph: { _html.escape(details.get('error')) }</div>")
            else:
                ingredients = details.get('ingredients', [])
                html_parts.append(f"<div class=\"rec-ingredients\"><strong>Ingredients:</strong> { _html.escape(', '.join(ingredients) if ingredients else 'N/A') }</div>")
                breakdown = details.get(f'disease_analysis_{condition}', [])
                if breakdown:
                    html_parts.append('<div class=\"rec-breakdown\">')
                    for b in breakdown:
                        ingr = _html.escape(b.get('ingredient',''))
                        eff = _html.escape(b.get('effect',''))
                        reason = _html.escape(b.get('reason',''))
                        html_parts.append(f"<div class=\"rec-item\"><strong>{ingr}</strong> — {eff}. {reason}</div>")
                    html_parts.append('</div>')
                else:
                    html_parts.append('<div class=\"rec-breakdown\">No direct ingredient->disease links found.</div>')
                vneg = info.get('vneg', 0)
                neg = info.get('neg', 0)
                if vneg > 0 or neg > 0:
                    html_parts.append(f"<div class=\"rec-alert\"><strong>ALERT:</strong> This menu contains {vneg} very negative and {neg} negative ingredients for { _html.escape(condition) }.</div>")
                else:
                    html_parts.append(f"<div class=\"rec-note\">No strongly negative ingredients detected for { _html.escape(condition) }.</div>")
            html_parts.append('</div>')
        html_parts.append('</div>')
        out_path.write_text('\n'.join(html_parts), encoding='utf-8')
        print('Wrote recommendation HTML to', out_path)
        return

    # Convert markdown to HTML for the normal (no customQuestion) path
    try:
        body_html = markdown.markdown(md, extensions=['extra'])
    except Exception:
        body_html = markdown.markdown(md)

    html_out = f"<html><head><meta charset='utf-8'><title>Recommendations</title></head><body>{body_html}</body></html>"
    out_path.write_text(html_out, encoding='utf-8')
    print('Wrote recommendation HTML to', out_path)

if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(description='Run full integration recommendation test')
    p.add_argument('--condition', '-c', default='diabetes', help='Target disease/condition (default: diabetes)')
    p.add_argument('--no-override', action='store_true', help='Do not apply candidate overrides')
    p.add_argument('--analysis-file', '-a', help='Path to analysis_results.json to load (default: templates/uploads/analysis_results.json)')
    p.add_argument('--output', '-o', help='Output HTML path (default: templates/uploads/full_test_recommendation.html)')
    p.add_argument('--customQuestion', help='Optional custom question to append to analysis')

    args = p.parse_args()

    print(f"Running full_integration_test: condition={args.condition}, apply_overrides={not args.no_override}, analysis_file={args.analysis_file or DEFAULT_ANALYSIS}, output={args.output or 'templates/uploads/full_test_recommendation.html'}")
    main(condition=args.condition, customQuestion=args.customQuestion, apply_overrides=not args.no_override, analysis_path=args.analysis_file, out_path=args.output)
