# The Menu-Disease Recommendation Repository

This repository contains the Menu → Ingredient → Disease knowledge-graph system, supporting:
- web scraping recipes (AllRecipes),
- preprocessing and canonicalization of ingredients,
- construction of a Menu→Ingredient→Disease NetworkX graph,
- a backend Recommendation API, and
- a lightweight Flask frontend that accepts menu images and returns health recommendations.

This README provides an index of the key documents, the minimal steps to run the frontend, and pointers to the preprocessing pipeline and analysis results.
**Note:** This file replaces an older quick-run note and consolidates current run instructions and references.

**Quick Links & Summaries**
- **Preprocessing pipeline:** [PREPROCESSING_PIPELINE_SUMMARY.md](PREPROCESSING_PIPELINE_SUMMARY.md) — Full design and step-by-step description of how AllRecipes data is scraped, ingredients are split/deduplicated/standardized, and ingredients are annotated per disease. Use this for reproducing or extending the canonicalization and annotation steps.
- **Graph summary:** [backend_menu_processing/MENU_INGREDIENT_DISEASE_GRAPH_SUMMARY.md](backend_menu_processing/MENU_INGREDIENT_DISEASE_GRAPH_SUMMARY.md) — How the NetworkX knowledge graph is built, queried, and visualized. Contains examples of `MenuIngredientDiseaseGraph` usage.
- **Web scraping:** [backend_menu_processing/WEBSCRAPPING_WORKFLOW_SUMMARY.md](backend_menu_processing/WEBSCRAPPING_WORKFLOW_SUMMARY.md) — Notebook-driven extractor design (`webscrapping.ipynb`), JSON-LD parsing, fallback HTML parsing, and CSV output formats.
- **Benchmarks & evaluation:** [BENCHMARK_RESULTS_SUMMARY.md](BENCHMARK_RESULTS_SUMMARY.md) — Results comparing graph vs LLM ranking approaches, visualizations, and recommendations.
- **Judge & verdict write-up:** [JUDGE_VERDICT.md](JUDGE_VERDICT.md) — Detailed evaluation verdicts and recommended hybrid approach.
- **Quick start (backend examples):** [QUICK_START.md](QUICK_START.md) — Example code snippets showing how to call the `MenuRecommendationAPI` from Python and command-line examples for `evaluate_recommendations.py`.

**Key modules (code) and what they do**
- `backend_menu_processing/process_menu_ingredient.py` — Preprocessing utilities (split ingredients, dedupe, annotate, standardize).
- `backend_menu_processing/menu_ingredient_disease_graph.py` — Builds `MenuIngredientDiseaseGraph` (NetworkX) from CSV inputs and provides graph query/matching/visualization methods.
- `backend_menu_processing/llm.py` — Centralized LLM interfaces (OpenAI + Gemini wrapper functions) used by preprocessing, evaluation, and frontend image parsing.
- `backend_menu_processing/recommendation_api.py` — `MenuRecommendationAPI` wrapper with convenient methods: `get_menus_for_disease()`, `get_menu_details()`, `compare_menus()`.
- `front_end/upload_chat_image.py` — Flask app that accepts image uploads, calls `extract_recipes_from_image()`, searches a FAISS vectorstore for best matches, and displays knowledge-graph recommendations.

**Files required to build/serve the system**
- `backend_menu_processing/data/standardized_menu_ingredients.csv` — menu → standardized ingredients (required by the graph builder).
- `backend_menu_processing/data/ingredient_*_relation.csv` — per-disease ingredient effect annotations (e.g., `ingredient_diabetes_relation.csv`).
- `front_end/faiss_vectorstore_recipes/` — FAISS index and metadata used by the frontend similarity search.
If any of the above are missing the graph or frontend will not run; see [PREPROCESSING_PIPELINE_SUMMARY.md](PREPROCESSING_PIPELINE_SUMMARY.md) for instructions to reproduce them.

**Frontend (Flask) - quick run**
1. Prepare Python environment (Python 3.10+ recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
# Install core dependencies; the project also uses OpenAI / Google Gemini clients.
pip install flask openai google-generativeai httpx networkx pandas python-dotenv markdown
2. Ensure environment variables are set (create a `.env` in repository root or set in environment):

- `OPENAI_API_KEY` (OpenAI API key) — required by vision/extraction and optional LLM steps
- `GOOGLE_API_KEY` (Gemini / Google generative API key) — required by preprocessing steps that call Gemini
See `backend_menu_processing/llm.py` for the `.env` search locations and examples.

3. Start the frontend server:
```bash
cd front_end
python upload_chat_image.py
# Open http://127.0.0.1:5001 in your browser
```
Notes:
- The Flask app expects a FAISS vectorstore under `front_end/faiss_vectorstore_recipes` and a pickled `faiss_vectorstore_metadatas.pkl` with the metadata (disease scores/reasoning) to display results. If the vectorstore is missing the frontend will raise an error on start.
- For development you may run with `debug=True` by editing the `__main__` block in `front_end/upload_chat_image.py`.

**Backend / Preprocessing - short guide**
- Preprocessing is documented in [PREPROCESSING_PIPELINE_SUMMARY.md](PREPROCESSING_PIPELINE_SUMMARY.md). In brief:
	1. Scrape recipes → `all_recipes.csv` (see `webscrapping.ipynb`).
	2. Use `process_menu_ingredient.py` to split ingredient strings (OpenAI), extract unique ingredients, deduplicate/normalize (Gemini), and annotate per disease (Gemini).
	3. Standardize menu ingredients and write `standardized_menu_ingredients.csv`.
	4. Build the graph: instantiate `MenuIngredientDiseaseGraph()` which reads the CSVs under `backend_menu_processing/data`.

Run examples:
```bash
# From repository root, basic backend example (interactive):
python3 -c "from backend_menu_processing.recommendation_api import MenuRecommendationAPI; api=MenuRecommendationAPI(); print(api.get_available_diseases()); print(len(api.get_available_menus()))"
```
## Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request with your improvements.

## License

This repository is for educational purposes. Please respect copyright and attribution requirements when using or sharing these materials.