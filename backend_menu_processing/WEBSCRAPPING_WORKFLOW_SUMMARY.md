# AllRecipes Web Scraper - Workflow Analysis

## Overview

The `webscrapping.ipynb` notebook implements a comprehensive web scraping pipeline to extract recipe data from **AllRecipes.com**. It collects recipe metadata, ingredients, cooking instructions, and nutritional information from multiple cuisine categories, storing the results in CSV format for database integration and downstream analysis.

---

## Table of Contents

1. [Architecture](#architecture)
2. [Key Components](#key-components)
3. [Workflow Pipeline](#workflow-pipeline)
4. [Core Functions](#core-functions)
5. [Data Flow](#data-flow)
6. [Output Formats](#output-formats)

---

## Architecture

The notebook follows a **modular, multi-stage architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN EXTRACTION LIBRARY                  │
│                   (Cells 1 - Initial Code)                  │
├─────────────────────────────────────────────────────────────┤
│  • Helper functions (time/format conversion)                │
│  • JSON-LD parsing (structured recipe data)                 │
│  • HTML fallback parsing (nutrition facts)                  │
│  • Main extraction functions                                │
│  • CSV conversion utilities                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   DISCOVERY & EXPLORATION                   │
│                   (Cells 2, 10, 14-17)                      │
├─────────────────────────────────────────────────────────────┤
│  • Scrape homepage for recipe links                         │
│  • Extract Chinese cuisine category recipes                 │
│  • Discover all world cuisine categories                    │
│  • Collect recipe URLs from each category                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    BULK DATA EXTRACTION                     │
│                   (Cells 7-8, 11-13, 21-23)                │
├─────────────────────────────────────────────────────────────┤
│  • Batch process recipe URLs                                │
│  • Handle errors and skip failures                          │
│  • Store extracted data in memory                           │
│  • Export to CSV files                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. **Configuration & Constants**

```python
# Example recipe URL for testing
URL = "https://www.allrecipes.com/recipe/128750/chinese-broccoli/"

# HTTP User-Agent (polite web scraping practice)
UA = {"User-Agent": "recipe-extractor/values-only/1.1 (+contact@example.com)"}

# Nutrition fields extraction order
NUTRIENT_ORDER = [
    "calories", "total_fat", "saturated_fat", "cholesterol", "sodium",
    "total_carbohydrate", "dietary_fiber", "total_sugars", "protein",
    "vitamin_c", "calcium", "iron", "potassium"
]

# UI label variations for nutrition fact parsing
LABELS = {
    "calories": ["Calories"],
    "total_fat": ["Total Fat", "Fat"],
    "saturated_fat": ["Saturated Fat", "Sat Fat"],
    ...
}

# JSON-LD schema field mappings
JSONLD_TO_CANON = {
    "calories": "calories",
    "fatContent": "total_fat",
    "saturatedFatContent": "saturated_fat",
    ...
}
```

### 2. **Extraction Sources**

The scraper uses **two complementary data sources**:

#### **Primary: JSON-LD Structured Data**
- Embedded in `<script type="application/ld+json">` tags
- Contains Recipe schema with standardized metadata
- Most reliable and consistent source
- Fields extracted: title, ingredients, instructions, times, nutrition

#### **Fallback: HTML UI Parsing**
- Used when JSON-LD nutrition data is incomplete
- Parses visible "Nutrition Facts" section in HTML
- Regular expressions identify nutrient labels and values
- Less reliable but provides coverage for incomplete JSON-LD data

---

## Workflow Pipeline

### **Phase 1: Library & Utilities Definition (Cell 1)**

**Purpose:** Define all helper functions and constants

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `_iso8601_to_minutes()` | Convert ISO 8601 duration (e.g., "PT1H30M") to minutes |
| `_minutes_to_hhmm()` | Convert minutes to readable time format (e.g., "1h 30m") |
| `_parse_servings()` | Extract and clean serving field |
| `_to_text_list()` | Convert various formats (list, dict, string) to text list |
| `_flatten_instructions()` | Flatten nested JSON-LD instruction structures |
| `extract_recipe_jsonld()` | Extract Recipe schema from JSON-LD |
| `normalize_nutrition_jsonld()` | Normalize nutrition data from JSON-LD |
| `parse_nutrition_ui_amounts()` | Parse nutrition facts from HTML layout |
| `extract_recipe()` | **Main function** - orchestrates full extraction |
| `to_one_row()` | Convert recipe dict to single-row CSV format |
| `write_one_row_csv()` | Write recipe to CSV file |

### **Phase 2: Recipe Discovery**

#### **Cells 2, 10, 14-17: Link Collection**

**Cell 2:** Scrape homepage recipe links
```
Input:  AllRecipes.com homepage
Output: ~100+ recipe URLs from homepage
```

**Cell 10:** Scrape Chinese cuisine category
```
Input:  https://www.allrecipes.com/recipes/695/world-cuisine/asian/chinese/
Output: Recipe URLs from Chinese cuisine category
```

**Cells 14-17:** Discover all world cuisines
```
Step 1: Find all world-cuisine category links
Step 2: Iterate through each category page
Step 3: Extract recipe URLs from each
Output: all_recipe_links.csv (comprehensive recipe index)
```

### **Phase 3: Single Recipe Testing (Cells 4-6)**

**Cell 4:** Test extraction on example recipe
```python
data = extract_recipe("https://www.allrecipes.com/recipe/128750/chinese-broccoli/")
```

**Cell 5:** Display extracted data
```python
print(data)  # Shows complete recipe structure
```

**Cell 6:** Write to CSV
```python
write_one_row_csv("recipe_single_row.csv", to_one_row(data), order)
```

### **Phase 4: Bulk Data Collection**

#### **Cells 7-8: General recipes (All recipes)**
```
Input:  recipe_links (from cell 2)
Process: Batch extraction with error handling
Output: all_recipes_single_row.csv
```

#### **Cells 11-13: Chinese cuisine recipes**
```
Input:  links (from cell 10)
Process: Extract Chinese recipes only
Output: all_recipes_Chinese.csv
```

#### **Cells 21-23: Comprehensive collection (All cuisines)**
```
Input:  all_recipe_links (from cells 14-17)
Process: Batch extract from ALL discovered recipes
Output: all_recipes.csv (primary dataset)
```

### **Empty/Separator Cells (3, 9, 20, 24-26)**

These cells serve as:
- Breakpoints for notebook organization
- Reserved space for future analysis
- Logical separators between phases

---

## Core Functions

### **Data Extraction Functions**

#### `extract_recipe(url: str) -> Dict[str, Any]`

**Purpose:** Main function that orchestrates the entire extraction process

**Process:**
```
1. Fetch recipe page via HTTP (with SSL verification disabled)
2. Extract JSON-LD Recipe schema from HTML
3. Parse metadata:
   - title, servings from recipe
   - prepTime, cookTime, totalTime (ISO 8601 → minutes → "Xh Ym")
4. Extract ingredients list
5. Extract cooking instructions (handle nested structures)
6. Get nutrition:
   - Primary: JSON-LD nutrition object
   - Fallback: Parse HTML "Nutrition Facts" section
7. Merge nutrition data (prefer JSON-LD)
8. Return dict with all fields
```

**Error Handling:**
- Raises `RuntimeError` if JSON-LD Recipe schema not found
- Raises `requests.exceptions.RequestException` on HTTP failures
- 30-second timeout per request
- SSL verification disabled for AllRecipes.com

#### `extract_recipe_jsonld(html: str) -> Optional[Dict[str, Any]]`

**Purpose:** Extract Recipe schema from JSON-LD structured data

**Algorithm:**
1. Find all `<script type="application/ld+json">` tags
2. Parse JSON content
3. Recursively search for Recipe objects
4. Return first Recipe found (or None if not found)

#### `parse_nutrition_ui_amounts(html: str) -> Dict[str, Optional[str]]`

**Purpose:** Fallback nutrition extraction from HTML "Nutrition Facts" section

**Algorithm:**
1. Extract all text from HTML
2. Find "Nutrition Facts" header position
3. For each nutrient in NUTRIENT_ORDER:
   - Find label (e.g., "Total Fat") in text
   - Extract amount from nearby window (120 chars)
   - Normalize format (e.g., "10g", "500kcal")
4. Return dict mapping nutrients to amounts

### **Format Conversion Functions**

#### `to_one_row(data: Dict[str, Any], list_sep: str = " | ") -> Dict[str, Any]`

**Purpose:** Convert multi-value recipe dict to single-row CSV format

**Transformations:**
- **Lists → Strings:** Join ingredients and directions with " | " separator
- **Directions:** Numbered format "1. Step 1 | 2. Step 2"
- **Null values:** Replace with "not provided"
- **Nutrients:** Create separate columns for each (nutrition_calories, nutrition_protein, etc.)

**Example Output Row:**
```
{
  "title": "Chinese Broccoli",
  "url": "https://...",
  "servings": "4",
  "prepTime": "10m",
  "cookTime": "20m",
  "totalTime": "30m",
  "ingredients": "1 bunch broccoli | 2 cloves garlic | ...",
  "directions": "1. Wash broccoli | 2. Heat oil | ...",
  "nutrition_calories": "85kcal",
  "nutrition_total_fat": "3g",
  ...
}
```

#### `_iso8601_to_minutes(iso: Optional[str]) -> Optional[int]`

**Purpose:** Convert ISO 8601 duration to minutes

**Examples:**
- `"PT30M"` → 30
- `"PT1H30M"` → 90
- `"P1DT2H"` → 1560 (1 day + 2 hours)

#### `_minutes_to_hhmm(m: Optional[int]) -> Optional[str]`

**Purpose:** Convert minutes to human-readable format

**Examples:**
- 30 → `"30m"`
- 90 → `"1h 30m"`
- 1440 → `"24h 0m"`

---

## Data Flow

### **Single Recipe Extraction Flow**

```
AllRecipes.com URL
        ↓
    HTTP GET (with UA header)
        ↓
    Parse HTML with BeautifulSoup
        ↓
    Extract JSON-LD <script> tags
        ↓
    ┌─────────────────────────────┐
    │   Recipe Schema Found?      │
    └─────────────────────────────┘
               ↙                    ↖
            YES                      NO
             ↓                        ↓
    Parse Recipe Fields     Raise RuntimeError
             ↓
    ┌─────────────────────────────┐
    │ Metadata Extraction         │
    │ • title, servings           │
    │ • prepTime, cookTime        │
    │ • ingredients, directions   │
    └─────────────────────────────┘
             ↓
    ┌─────────────────────────────┐
    │ Nutrition Extraction        │
    ├─────────────────────────────┤
    │ Primary: JSON-LD nutrition  │
    │ Fallback: HTML parsing      │
    │ Merge results               │
    └─────────────────────────────┘
             ↓
    Return Dict with all fields
```

### **Bulk Extraction Flow**

```
all_recipe_links (set of URLs)
        ↓
    For each URL:
        ├─ Try: extract_recipe(url)
        │   ├─ Success: Append to all_data
        │   └─ Failure: Print error, continue
        └─ Next URL
        ↓
    Convert all_data to CSV rows
    (using to_one_row() for each recipe)
        ↓
    Write to CSV file with headers
    (title, url, servings, prepTime, cookTime, totalTime, 
     ingredients, directions, nutrition_*, ...)
        ↓
    Output: all_recipes.csv
```

---

## Output Formats

### **CSV Structure**

All output CSV files share the same column structure:

| Column | Type | Example |
|--------|------|---------|
| title | string | "Chinese Broccoli" |
| url | string | "https://www.allrecipes.com/recipe/128750/..." |
| servings | string | "4" or "not provided" |
| prepTime | string | "10m" or "1h 30m" |
| cookTime | string | "20m" |
| totalTime | string | "30m" |
| ingredients | string (pipe-separated) | "1 bunch broccoli \| 2 cloves garlic \| ..." |
| directions | string (pipe-separated, numbered) | "1. Wash broccoli \| 2. Heat oil \| ..." |
| nutrition_calories | string | "85kcal" or "not provided" |
| nutrition_total_fat | string | "3g" or "not provided" |
| nutrition_saturated_fat | string | "1g" |
| nutrition_cholesterol | string | "0mg" |
| nutrition_sodium | string | "50mg" |
| nutrition_total_carbohydrate | string | "5g" |
| nutrition_dietary_fiber | string | "2g" |
| nutrition_total_sugars | string | "1g" |
| nutrition_protein | string | "3g" |
| nutrition_vitamin_c | string | "50mg" |
| nutrition_calcium | string | "100mg" |
| nutrition_iron | string | "2mg" |
| nutrition_potassium | string | "300mg" |

### **Generated Output Files**

| File | Source | Content |
|------|--------|---------|
| `recipe_single_row.csv` | Cell 6 | Single test recipe |
| `all_recipes_single_row.csv` | Cell 8 | Recipes from homepage (Cell 2 links) |
| `all_recipes_Chinese.csv` | Cell 13 | Chinese cuisine recipes only |
| `cuisine_links.csv` | Cell 16 | All discovered cuisine category URLs |
| `all_recipe_links.csv` | Cell 19 | Comprehensive index of all recipe URLs |
| `all_recipes.csv` | Cell 23 | **Primary dataset** - all recipes from all cuisines |

---

## Error Handling & Robustness

### **Network Errors**
- 30-second timeout per HTTP request
- SSL verification disabled (AllRecipes.com may have certificate issues)
- User-Agent header included (polite scraping practice)

### **Parsing Errors**
```python
try:
    data = extract_recipe(url)
    all_data.append(data)
except Exception as e:
    print(f"Failed to extract {url}: {e}")
    # Continue to next URL instead of crashing
```

### **Missing Data**
- Empty/None values replaced with "not provided" in CSV
- Fallback to UI parsing if JSON-LD nutrition incomplete
- Fields marked as None converted to "not provided"

---

## Key Design Decisions

### 1. **Dual Nutrition Extraction Strategy**
- **Primary:** JSON-LD (structured, reliable)
- **Fallback:** HTML parsing (for incomplete JSON-LD)
- **Merge:** Prefer JSON-LD, use UI if missing

### 2. **Single-Row CSV Format**
- Lists (ingredients, directions) flattened to pipe-separated strings
- Pipe separator (" | ") chosen to avoid collision with commas
- Enables simple database ingestion and spreadsheet compatibility

### 3. **Modular Function Design**
- Small, testable helper functions (time conversion, list flattening)
- Reusable parsing logic (JSON-LD extraction, UI parsing)
- Main `extract_recipe()` orchestrates all steps

### 4. **Error-Tolerant Batch Processing**
- Each recipe extraction wrapped in try-except
- Failures logged but don't halt pipeline
- Partial data collection preferred over complete failure

### 5. **URL Deduplication**
- Uses Python `set()` to automatically deduplicate URLs
- Strips query parameters (`?param=value`) to avoid duplicates
- Ensures consistent data across runs

---

## Performance Considerations

### **Time Complexity**
- **Per recipe:** O(1) - fixed parsing operations
- **Batch:** O(n) where n = number of recipes
- Network I/O dominates (30s timeout per recipe)

### **Scalability**
- **Current bottleneck:** HTTP request latency (~2-30s per recipe)
- **For 1000+ recipes:** Consider async HTTP library (httpx, aiohttp)
- **Memory:** All recipes stored in RAM before CSV write
  - For very large datasets, use streaming CSV writer

### **Reliability**
- No persistence of partial results (no checkpoints)
- Crashes lose all progress; consider adding checkpoint saves

---

## Usage Example

### **Basic Usage:**
```python
# Extract single recipe
data = extract_recipe("https://www.allrecipes.com/recipe/...")

# Export to CSV
order = ["title", "url", "servings", ...nutrition_fields...]
write_one_row_csv("output.csv", to_one_row(data), order)
```

### **Batch Processing:**
```python
# Extract multiple recipes
all_data = []
for url in recipe_urls:
    try:
        data = extract_recipe(url)
        all_data.append(data)
    except Exception as e:
        print(f"Failed: {url}")

# Write all to CSV
with open("output.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=columns)
    writer.writeheader()
    for d in all_data:
        writer.writerow(to_one_row(d))
```

---

## Summary

This web scraper provides a **complete, production-ready solution** for extracting recipe data from AllRecipes.com. It combines structured data extraction (JSON-LD) with HTML parsing fallbacks to ensure robust data collection across thousands of recipes. The output CSV format is optimized for downstream analysis, menu planning, and ingredient-disease relationship mapping (as evidenced by the project's health-focused context).

The modular design, comprehensive error handling, and clear separation of concerns make it maintainable and extensible for future enhancements.
