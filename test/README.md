# Test Suite for Preprocessing Pipeline

This folder contains comprehensive tests for the menu recommendation preprocessing pipeline.

## Test Files

### `test_full_pipeline.py`
Comprehensive test of all 6 preprocessing steps with simplified data:
1. Split Ingredients (OpenAI GPT-4o)
2. Extract Unique Ingredients (Python)
3. Deduplicate & Normalize (Gemini)
4. Annotate Disease Effects (Gemini)
5. Standardize Menu Ingredients (Gemini)
6. Graph Construction (NetworkX)

**Run:** `python test_full_pipeline.py`

### `test_gemini_steps.py`
Focused test of Gemini-dependent preprocessing steps:
- Deduplicate & normalize ingredients
- Annotate health impacts by disease
- Standardize menu ingredients

**Run:** `python test_gemini_steps.py`

### `test_core_pipeline.py`
Basic test of core pipeline functions:
- Ingredient splitting
- Unique ingredient extraction
- Deduplication
- Graph construction

**Run:** `python test_core_pipeline.py`

### `verify_paths.py`
Quick verification that import paths are correctly configured.

**Run:** `python verify_paths.py`

## Data

### `test_data/`
Contains test data used by the pipeline tests:
- Simplified recipe data for testing
- Minimal ingredient lists for each step

## Running Tests from Project Root

From `/Users/jameszhang/git/Hello-World`:
```bash
# Run full pipeline test
/opt/anaconda3/bin/conda run -n py311 python test/test_full_pipeline.py

# Run Gemini steps test
/opt/anaconda3/bin/conda run -n py311 python test/test_gemini_steps.py

# Run core pipeline test
/opt/anaconda3/bin/conda run -n py311 python test/test_core_pipeline.py

# Verify paths
/opt/anaconda3/bin/conda run -n py311 python test/verify_paths.py
```

## Expected Results

✅ **All tests should pass** when:
- `.env` file is properly configured with valid API keys
- `backend_menu_processing/llm.py` module is available
- Dependencies installed: `openai`, `google-generativeai`, `networkx`

⚠️ **Gemini quota limits** may cause steps 4-5 to be simulated if free-tier quota exceeded (20 requests/day).

## Path Structure

```
Hello-World/
├── backend_menu_processing/
│   ├── llm.py                 ← Centralized API module
│   ├── process_menu_ingredient.py
│   ├── menu_ingredient_disease_graph.py
│   └── ...
├── test/                      ← This folder
│   ├── test_full_pipeline.py
│   ├── test_gemini_steps.py
│   ├── test_core_pipeline.py
│   ├── verify_paths.py
│   └── test_data/             ← Test data
└── .env                        ← API keys (git-ignored)
```

All test files use relative paths to correctly import the `llm` module from `backend_menu_processing/`.
