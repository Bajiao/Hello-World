"""
Debug markdown generation and show line-by-line output for inspection.
"""
import json
import re
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ANALYSIS_PATH = Path(__file__).parent / 'templates' / 'uploads' / 'analysis_results.json'

if not ANALYSIS_PATH.exists():
    print('analysis_results.json not found at', ANALYSIS_PATH)
    sys.exit(1)

data = json.loads(ANALYSIS_PATH.read_text())
inner = next(iter(data.values())) if isinstance(data, dict) and len(data) == 1 and isinstance(next(iter(data.values())), dict) else data
recipes = inner.get('recipes', [])
matches = inner.get('matches', [])

# Build md similarly to the app
md = "# Recommendations for debug\n\n"
for idx, recipe in enumerate(recipes):
    md += f"## {recipe}\n\n"
    matched = matches[idx] if idx < len(matches) else {'matched_menu': None}
    if matched.get('matched_menu'):
        md += f"- Closest match in knowledge graph: **{matched.get('matched_menu')}**\n\n"
    else:
        md += f"- Not found in knowledge graph: Menu '{recipe}' not found\n\n"

# Show repr and numbered lines
print('---- RAW MARKDOWN (repr) ----')
print(repr(md[:1000]))
print('\n---- LINES WITH INDICES ----')
for i, line in enumerate(md.splitlines()):
    # show if blank line
    mark = '<BLANK>' if not line.strip() else line
    print(f"{i+1:03d}: {mark!s}")

# Show sequences of consecutive blank lines
lines = md.splitlines()
blank_runs = []
run = 0
for line in lines:
    if not line.strip():
        run += 1
    else:
        if run > 1:
            blank_runs.append(run)
        run = 0
if blank_runs:
    print('\nFound blank runs (consecutive blank lines lengths):', blank_runs)
else:
    print('\nNo multi-blank runs detected')
    # Run the same cleanup used by the app and show result
    import re
    clean = md.replace('\r\n', '\n')
    clean = re.sub(r'[ \t]+\n', '\n', clean)
    clean = re.sub(r'\n\s*\n+', '\n\n', clean)
    clean = re.sub(r'(#{1,6} .*?)\n\s*\n+', r'\1\n\n', clean)
    clean = re.sub(r'\n\s*\n(?=[*-]\s)', '\n', clean)
    clean = clean.strip() + '\n'
    print('\n---- CLEANED MARKDOWN LINES ----')
    for i, line in enumerate(clean.splitlines()):
        mark = '<BLANK>' if not line.strip() else line
        print(f"{i+1:03d}: {mark!s}")
