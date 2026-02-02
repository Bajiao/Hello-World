"""
Menu Chat Image Upload Application

This Flask application provides a web interface for:
1. Uploading menu images and extracting recipe names using OpenAI Vision API
2. Searching for matching recipes in a FAISS vector database
3. Providing health-related information (disease risk scores and reasoning)
4. Answering follow-up questions about recipes based on extracted information

The application uses:
- OpenAI Vision API for menu image analysis
- FAISS vector database for semantic recipe similarity search
- LangChain for embedding generation and vector operations
- Flask for the web interface
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, render_template, send_from_directory
import pickle
import json
import html
import re

# Add parent directory to path to import llm module
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
import pandas as pd
import markdown

# Import centralized LLM functions
from backend_menu_processing.llm import (
    load_env_variables,
    get_openai_client,
    extract_recipes_from_image,
    ask_openai_follow_up,
    get_project_root
)


# ============================================================================
# SETUP AND INITIALIZATION
# ============================================================================
# Load environment variables and initialize clients needed for the application

# Load environment variables
load_env_variables()

# Get OpenAI client
client = get_openai_client()

# Define base directories using functions (no hardcoded paths)
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = get_project_root()

print(f"Base directory: {BASE_DIR}")
print(f"Project root: {PROJECT_ROOT}")


# === Custom Embeddings Class ===
class CustomOpenAIEmbeddings(Embeddings):
    """
    Custom embedding model wrapper for LangChain compatibility.
    
    Wraps OpenAI's text-embedding-3-large model to work with LangChain's
    FAISS vector store interface. Handles both single queries and document
    batches.
    
    Attributes:
        client: OpenAI client instance used for API calls
    """

    def __init__(self, client):
        """Initialize embeddings with an OpenAI client."""
        self.client = client

    def embed_documents(self, texts):
        """
        Generate embeddings for multiple documents/texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (lists of floats)
        """
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        """
        Generate embedding for a single query text.
        
        Args:
            text: Single text string to embed
            
        Returns:
            Embedding vector (list of floats)
        """
        return self._embed(text)

    def _embed(self, text):
        """
        Internal method to call OpenAI embedding API.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector from OpenAI's text-embedding-3-large model
        """
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding


# === Initialize embeddings ===
embeddings = CustomOpenAIEmbeddings(client)
print(f"✓ Embeddings initialized: {embeddings}")

# === Load FAISS vectorstore with resilient path resolution ===
# Try multiple possible locations to find the FAISS vectorstore
vectorstore_paths = [
    BASE_DIR / "faiss_vectorstore_recipes",
    BASE_DIR / "." / "faiss_vectorstore_recipes",
    PROJECT_ROOT / "front_end" / "faiss_vectorstore_recipes",
]

vectorstore = None
vectorstore_path = None
for path in vectorstore_paths:
    try:
        if path.exists():
            vectorstore = FAISS.load_local(
                folder_path=str(path),
                embeddings=embeddings,
                allow_dangerous_deserialization=True
            )
            vectorstore_path = path
            print(f"✓ Successfully loaded FAISS vectorstore from: {path}")
            break
    except Exception as e:
        print(f"Debug: Failed to load from {path}: {e}")
        continue

if vectorstore is None:
    raise ValueError(
        f"Could not load FAISS vectorstore from any of: {vectorstore_paths}"
    )

# === Load metadata with resilient path resolution ===
# Metadata contains disease scoring information for recipes
metadata_paths = [
    vectorstore_path / "faiss_vectorstore_metadatas.pkl",
    BASE_DIR / "faiss_vectorstore_recipes" / "faiss_vectorstore_metadatas.pkl",
    PROJECT_ROOT / "front_end" / "faiss_vectorstore_recipes" / "faiss_vectorstore_metadatas.pkl",
]

metadatas = None
for path in metadata_paths:
    if path.exists():
        try:
            with open(path, "rb") as f:
                metadatas = pickle.load(f)
            print(f"✓ Loaded metadata from: {path}")
            break
        except Exception as e:
            print(f"  ⚠️  Failed to load metadata from {path}: {e}")
            continue

if metadatas is None:
    raise ValueError(
        f"Could not find faiss_vectorstore_metadatas.pkl in any of: {metadata_paths}"
    )

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================
# Configure Flask app with template and static file directories

# Initialize Flask app with explicit paths
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
UPLOAD_FOLDER = TEMPLATE_DIR / "uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR)
)

# Configure upload folder
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"✓ Upload folder configured: {UPLOAD_FOLDER}")

# Helper to check allowed file type
def allowed_file(filename):
    """
    Check if uploaded file has an allowed extension.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        True if file has an allowed extension (png, jpg, jpeg), False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# CHAT AND PROCESSING FUNCTIONS
# ============================================================================

def ask_openai_image(image_path):
    """
    Extract recipe names from an image and find matching recipes with health data.
    
    Process flow:
    1. Use OpenAI Vision API to extract all dish/recipe names from the menu image
    2. For each extracted recipe, search the FAISS vector store for the best match
    3. Retrieve disease risk scores and reasoning from recipe metadata
    4. Generate an HTML table displaying results
    
    Args:
        image_path: File path to the image to process
        
    Returns:
        Tuple of (html_output, empty_string, empty_string):
        - html_output: HTML string with extracted recipes list and results table
        - Unused strings maintained for interface compatibility
    """
    try:
        # Use centralized function from llm.py to extract recipes
        recipes = extract_recipes_from_image(image_path)
        
        if not recipes:
            print("No recipes extracted from image")
            return "", "<p>No recipes found in image</p>", ""

        print(f"Raw recipes received from extract_recipes_from_image:")
        for i, r in enumerate(recipes):
            print(f"  Recipe {i}: {repr(r)}", flush=True)
            has_literal_n = '\\n' in r
            has_newline = '\n' in r
            print(f"    Has literal backslash-n: {has_literal_n}, Has newline: {has_newline}", flush=True)

        # Show extracted recipes first - handle recipes as a list and clean whitespace aggressively
        # Strip each recipe and remove any internal newlines/special characters
        if isinstance(recipes, str):
            # If it's a string, split by newlines and clean each part
            recipes_str = recipes.replace('\\n', '\n')  # Ensure we have real newlines
            cleaned_recipes = []
            for line in recipes_str.split('\n'):
                cleaned = line.strip()
                # Remove any remaining escape sequences or special chars
                cleaned = re.sub(r'[\r\n\t\\]+', ' ', cleaned)
                if cleaned:
                    cleaned_recipes.append(cleaned)
        else:
            # If it's already a list, clean each item thoroughly
            cleaned_recipes = []
            for r in recipes:
                if isinstance(r, str):
                    # Strip and remove all newlines and special whitespace
                    cleaned_r = r.strip()
                    # Remove literal backslash-n sequences (two character sequence)
                    cleaned_r = cleaned_r.replace('\\n', ' ')
                    # Remove actual newlines
                    cleaned_r = re.sub(r'[\n\r\t]+', ' ', cleaned_r)
                    # Remove multiple consecutive spaces
                    cleaned_r = re.sub(r'\s+', ' ', cleaned_r).strip()
                    if cleaned_r:
                        cleaned_recipes.append(cleaned_r)
        
        print(f"Cleaned recipes: {cleaned_recipes}", flush=True)
        print(f"Cleaned recipes repr: {repr(cleaned_recipes)}", flush=True)
        
        # Format recipes list as HTML bullet points with proper line breaks
        # Use html.escape() to safely handle any special characters and prevent XSS
        recipes_html = '<br>'.join([f"• {html.escape(r)}" for r in cleaned_recipes])
        extracted_html = f"<b>Extracted recipes from image:</b><br>{recipes_html}<br><br>"
        print(f"Extracted HTML (first 500 chars): {repr(extracted_html[:500])}", flush=True)

        # Step 2: For each extracted recipe, run vector search and collect results
        # Use cleaned_recipes instead of original recipes to avoid newline characters
        all_keys = set()
        recipe_results = []
        for recipe_query in cleaned_recipes:
            # Search FAISS vector store for most similar recipe (k=1 means top 1 match)
            docs_and_scores = vectorstore.similarity_search_with_score(recipe_query, k=1)
            if docs_and_scores:
                # Keys to display: disease scores and health reasoning
                selected_keys = [
                    'score_cardiovascular', 'reasoning-cardiovascular',
                    'score_diabetes', 'reasoning-diabetes',
                    'score_kidney', 'reasoning-kidney'
                ]
                for doc, score in docs_and_scores:
                    meta = doc.metadata if hasattr(doc, 'metadata') else {}
                    recipe_name = meta.get('name') or (doc.page_content.split('\n')[0] if doc.page_content else 'Unknown')
                    # Filter metadata to only selected keys and add similarity score
                    meta_filtered = {k: meta.get(k, '') for k in selected_keys}
                    meta_filtered['similarity_score'] = float(score) if score is not None else ''
                    all_keys.update(meta_filtered.keys())
                    recipe_results.append({
                        'query': recipe_query,
                        'matched': recipe_name,
                        'meta': meta_filtered
                    })
            else:
                recipe_results.append({
                    'query': recipe_query,
                    'matched': 'No relevant recipe found.',
                    'meta': {}
                })

        all_keys = sorted(all_keys)
        display_keys = ['matched', 'similarity_score']
        
        # Build table HTML with styling for better readability
        results_table = '''
        <div style="overflow-x:auto; margin-top:12px; max-height:500px;">
        <table border="1" style="border-collapse:collapse; width:98%; min-width:800px; background:#fff; font-size:1rem;">
            <thead style="background:#f2f2f2; position:sticky; top:0; z-index:2;">
                <tr>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Recipe Query</th>
'''
        # Add column headers
        for k in display_keys:
            header_label = 'Most Matched Recipe' if k == 'matched' else k
            results_table += f'<th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">{header_label}</th>'
        results_table += '''
                </tr>
            </thead>
            <tbody>
'''
        # Add data rows
        for result in recipe_results:
            results_table += f'<tr>'
            # Clean the query: strip all whitespace including newlines and escape for HTML
            clean_query = result["query"].strip()
            clean_query = clean_query.replace('\\n', ' ')  # Remove literal backslash-n
            clean_query = re.sub(r'[\n\r\t]+', ' ', clean_query)  # Remove actual whitespace
            clean_query = re.sub(r'\s+', ' ', clean_query).strip()
            results_table += f'<td style="padding:8px;">{html.escape(clean_query)}</td>'
            for k in display_keys:
                val = result["meta"].get(k, '')
                if isinstance(val, float):
                    val = f"{val:.3f}"
                results_table += f'<td style="padding:8px;">{val}</td>'
            results_table += '</tr>'
        
        results_table += '''
            </tbody>
        </table>
        </div>
'''
        final_html = extracted_html + results_table
        # CRITICAL: Aggressive final cleanup for escape sequences
        # Remove ALL variants of escaped newlines - this is the key issue!
        final_html = final_html.replace('\\n', '')  # backslash-n (two chars)
        final_html = final_html.replace('\\\\n', '')  # double-escaped backslash-n
        final_html = final_html.replace('&#92;n', '')  # HTML entity for backslash-n
        final_html = final_html.replace('&bsol;n', '')  # HTML entity variant
        final_html = re.sub(r'\\[rnt]', '', final_html)  # Any escaped whitespace chars
        final_html = re.sub(r'\n\n\n+', '\n', final_html)  # Collapse multiple newlines
        
        # One more pass - remove spaces that are just \n patterns that we missed
        # This catches if they somehow slipped through with spaces around them
        pattern = r'\s*\\\s*n\s*'
        final_html = re.sub(pattern, '', final_html, flags=re.IGNORECASE)
        
        final_html = final_html.strip()
        
        # Verification: Check what's actually in the final HTML
        print(f"DEBUG: Final HTML length: {len(final_html)}", flush=True)
        print(f"DEBUG: Final HTML repr (last 500 chars): {repr(final_html[-500:])}", flush=True)
        has_backslash_n = '\\n' in final_html
        print(f"DEBUG: Has literal backslash-n? {has_backslash_n}", flush=True)
        has_pattern = bool(re.search(pattern, final_html))
        print(f"DEBUG: Has backslash-n pattern? {has_pattern}", flush=True)
        
        return final_html
    except Exception as e:
        print(f"Error in ask_openai_image: {e}")
        return f"Error: {str(e)}", "<p>Error processing image</p>", ""


def ask_openai_over_image_output(answer: str, question: str) -> str:
    """
    Answer a follow-up question based on extracted recipe information.
    
    Uses OpenAI to generate contextual responses about the recipes and their
    health implications based on the extracted and analyzed recipe data.
    
    Args:
        answer: HTML string containing extracted recipe information from ask_openai_image
        question: User's follow-up question about the recipes
        
    Returns:
        HTML string containing the response (converted from markdown for proper rendering)
    """
    try:
        response = ask_openai_follow_up(
            question=question,
            context=f"Extracted recipe information:\n{answer}"
        )
        if response:
            # First pass: Fix numbered list formatting where content appears on next line
            # Pattern: "1.\n" should become "1. " (number, dot, space on same line as content)
            response = re.sub(r'(\d+\.)\s*\n\s+', r'\1 ', response)
            
            # Second pass: Fix bulleted list formatting
            response = re.sub(r'([-•*])\s*\n\s+', r'\1 ', response)
            
            # Clean up the markdown: remove excessive blank lines but keep formatting
            lines = response.split('\n')
            cleaned_lines = []
            blank_count = 0
            for line in lines:
                if line.strip():
                    cleaned_lines.append(line)
                    blank_count = 0
                else:
                    blank_count += 1
                    if blank_count < 2:  # Allow max 1 blank line between content
                        cleaned_lines.append(line)
            
            cleaned_response = '\n'.join(cleaned_lines).strip()
            # Convert markdown to HTML for proper rendering without adding extra line breaks
            html_response = markdown.markdown(cleaned_response)
            # Post-process to clean up list formatting
            # Remove <p> tags from inside <li> items to keep number and content on same line
            html_response = re.sub(r'<li>\s*<p>(.+?)</p>\s*</li>', r'<li>\1</li>', html_response, flags=re.DOTALL)
            # Remove unwanted <br> tags that markdown adds after list items
            html_response = re.sub(r'(</li>)\s*<br>\s*', r'\1', html_response)
            return html_response
        return "<p>Could not generate a response</p>"
    except Exception as e:
        print(f"Error in ask_openai_over_image_output: {e}")
        return f"<p>Error: {str(e)}</p>"


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Main upload and chat interface endpoint.
    
    Handles three types of requests:
    1. Image upload: Extract recipes and disease risk information
    2. Follow-up question with existing answer: Answer based on previous extraction
    3. Follow-up question without answer: Find most recent upload and process it
    
    Returns:
        Rendered HTML template with filename, question, answer, and followup results
    """
    filename = None
    question = None
    answer = None
    followup = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        question = request.form.get('question')

        if uploaded_file and allowed_file(uploaded_file.filename):
            # Handle image upload
            filename = uploaded_file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                answer = ask_openai_image(file_path)
        
        elif question and answer:
            # Handle follow-up question with existing answer
            followup = ask_openai_over_image_output(answer, question)
        
        elif question:
            # If no answer yet, try to find the most recently uploaded image
            try:
                upload_dir = Path(app.config['UPLOAD_FOLDER'])
                uploaded_files = [f for f in upload_dir.iterdir() if f.is_file() and allowed_file(f.name)]
                if uploaded_files:
                    latest_file = max(uploaded_files, key=lambda p: p.stat().st_mtime)
                    filename = latest_file.name
                    answer = ask_openai_image(str(latest_file))
                    if answer:
                        followup = ask_openai_over_image_output(answer, question)
            except Exception as e:
                print(f"Error finding previous upload: {e}")

    return render_template('menu_chat.html',
                         filename=filename,
                         question=question,
                         answer=answer,
                         followup=followup)


@app.route('/uploads/<filename>')
def uploaded_file(filename: str):
    """
    Serve uploaded files from the uploads directory.
    
    Args:
        filename: Name of the file to serve
        
    Returns:
        File from uploads folder or 404 if not found
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    # Start Flask development server on localhost:5001
    # debug=False to avoid issues with auto-reloading
    app.run(debug=False, host='127.0.0.1', port=5001)
