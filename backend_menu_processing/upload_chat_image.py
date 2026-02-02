"""
Menu Image Processing and Chat Application (Backend Version)

This Flask application processes menu images to:
1. Extract recipe names using OpenAI Vision API with structured JSON output
2. Match extracted recipes to a FAISS vector database for semantic similarity
3. Display matching recipes with comprehensive metadata in an HTML table
4. Answer follow-up questions about recipes and health implications

Key Features:
- Vision-based OCR using GPT-4V for accurate recipe extraction
- Semantic search using FAISS vector database for recipe matching
- Custom OpenAI embeddings for LangChain integration
- HTML table output with dynamic column generation based on metadata
- Follow-up question answering based on extracted information

Dependencies:
- Flask: Web framework
- OpenAI API: Vision API and embeddings
- FAISS: Vector similarity search
- LangChain: Embedding and vector store integration
- Pillow: Image processing
"""

import os
from flask import Flask, request, render_template, render_template_string, send_from_directory
from pathlib import Path
from dotenv import load_dotenv  
import httpx
from PIL import Image
import pytesseract
import base64
import pickle

# Use langchain v1 compatible community/core packages when available,
# fall back to older langchain imports for compatibility.
try:
    from langchain_community.vectorstores import FAISS
    from langchain_core.embeddings import Embeddings
except Exception:
    from langchain.vectorstores import FAISS
    from langchain.embeddings.base import Embeddings  # Base class for embedding models

import pandas as pd
from openai import OpenAI
from langchain.embeddings.base import Embeddings  # Base class for embedding models


# ============================================================================
# ENVIRONMENT AND CLIENT INITIALIZATION
# ============================================================================
# === Setup Environment Variables ===
dotenv_path = Path("OpenAI_API_Key.env")
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OpenAI API key not found.")
else:
    print("API key loaded.")

# === Initialize OpenAI Client ===
# Using httpx.Client with verify=False for SSL verification (be cautious in production)
client = OpenAI(api_key=openai_api_key, http_client=httpx.Client(verify=False))

# ============================================================================
# EMBEDDING AND VECTOR STORE SETUP
# ============================================================================

# === Custom Embeddings Class ===
class CustomOpenAIEmbeddings(Embeddings):
    """
    Custom embedding model wrapper for LangChain compatibility.
    
    Wraps OpenAI's text-embedding-3-large model to work with LangChain's
    FAISS vector store interface. Provides methods for embedding both
    single documents and batch documents.
    
    Attributes:
        client: OpenAI client instance used for API calls
    """

    def __init__(self, client):
        """
        Initialize embeddings wrapper with OpenAI client.
        
        Args:
            client: OpenAI client instance
        """
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
        
        Uses the text-embedding-3-large model for high-quality semantic embeddings.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector from OpenAI's text-embedding-3-large model
        """
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        # Correctly access the embedding data
        return response.data[0].embedding
    

# Initialize embeddings instance
embeddings = CustomOpenAIEmbeddings(client)

print(embeddings)

# === Load FAISS Vector Store ===
# Load pre-built FAISS vector store containing recipe embeddings
# Load the FAISS vectorstore (use folder_path kwarg for community package compatibility)
try:
    vectorstore = FAISS.load_local(
        folder_path="faiss_vectorstore_recipes",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )
except TypeError:
    # Older langchain FAISS.load_local accepted the folder path as first positional arg
    vectorstore = FAISS.load_local(
        "faiss_vectorstore_recipes",
        embeddings=embeddings,
        allow_dangerous_deserialization=True
    )

# === Load Metadata ===
# Load pickled metadata containing disease risk scores and health information
with open("./faiss_vectorstore_recipes/faiss_vectorstore_metadatas.pkl", "rb") as f:
    metadatas = pickle.load(f)


# ============================================================================
# FLASK APPLICATION CONFIGURATION
# ============================================================================

# Initialize Flask app
app = Flask(__name__)

# === File Upload Configuration ===
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# === Helper Functions ===

def ask_openai_image(image_path):
    """
    Extract recipe names from menu image and find matching recipes with metadata.
    
    Process flow:
    1. Load image and convert to base64 data URL
    2. Use OpenAI Vision API (GPT-4V) with strict JSON schema to extract recipe names
    3. For each extracted recipe, search FAISS vector store for semantic matches
    4. Generate HTML table with recipe matches and all available metadata
    
    Args:
        image_path: File path to the menu image to process
        
    Returns:
        HTML string containing:
        - List of extracted recipes from the menu image
        - Table with recipe matches, similarity scores, and all metadata fields
    """
    try:
        # Step 0: Load and encode image
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        ext = image_path.rsplit('.', 1)[1].lower()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/{ext};base64,{image_base64}"

        # Step 1: Use OpenAI Vision to extract recipe names as JSON
        # Using structured JSON schema for reliable recipe extraction
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "Extract ALL dish/recipe names uniquely from the image. Ignore prices, descriptions, categories. Return only JSON adhering to the schema."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Parse this menu and return all recipe names."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ],
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "menu_recipes",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "recipes": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Unique recipe or dish names found in the image"
                            }
                        },
                        "required": ["recipes"],
                        "additionalProperties": False
                    },
                    "strict": True
                },
            },
            temperature=0  # Deterministic output for consistent recipe extraction
        )

        # Parse JSON response to extract recipe names
        import json
        obj = json.loads(response.choices[0].message.content)
        recipes = obj.get("recipes", [])
        print("Extracted recipes:", recipes)

        # Show extracted recipes in HTML format
        extracted_html = f"<b>Extracted recipes from image:</b> {', '.join(recipes) if recipes else 'None found'}<br>"

        # Step 2: For each extracted recipe, run vector search and collect results
        # First, collect all metadata keys to determine table columns dynamically
        all_keys = set()
        recipe_results = []
        for recipe_query in recipes:
            # Search FAISS vector store for most similar recipe (k=1 means top 1 match)
            docs_and_scores = vectorstore.similarity_search_with_score(recipe_query, k=1)
            if docs_and_scores:
                doc, score = docs_and_scores[0]
                meta = doc.metadata if hasattr(doc, 'metadata') else {}
                # Get recipe name from metadata or document content
                recipe_name = meta.get('name') or (doc.page_content.split('\n')[0] if doc.page_content else 'Unknown')
                all_keys.update(meta.keys())
                recipe_results.append({
                    'query': recipe_query,
                    'matched': recipe_name,
                    'meta': meta
                })
            else:
                recipe_results.append({
                    'query': recipe_query,
                    'matched': 'No relevant recipe found.',
                    'meta': {}
                })

        all_keys = sorted(all_keys)
        # Build HTML table header
        # Improved table styling for better appearance and width
        results_table = '''
        <div style="overflow-x:auto; margin-top:12px; max-height:500px;">
        <table border="1" style="border-collapse:collapse; width:98%; min-width:800px; background:#fff; font-size:1rem;">
            <thead style="background:#f2f2f2; position:sticky; top:0; z-index:2;">
                <tr>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Recipe Query</th>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Most Matched Recipe</th>
'''
        # Add columns for each metadata key found
        for k in all_keys:
            results_table += f'<th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">{k}</th>'
        results_table += '''
                </tr>
            </thead>
            <tbody>
'''
        # Build table rows with data
        for result in recipe_results:
            results_table += f'<tr>'
            results_table += f'<td style="padding:8px;">{result["query"]}</td>'
            results_table += f'<td style="padding:8px;">{result["matched"]}</td>'
            for k in all_keys:
                v = result['meta'].get(k, '')
                results_table += f'<td style="padding:8px;">{v}</td>'
            results_table += '</tr>'
        results_table += '''
            </tbody>
        </table>
        </div>
'''

        return extracted_html + results_table
    except Exception as e:
        return f"Error: {str(e)}"


def ask_openai_over_image_output(answer, question):
    """
    Answer follow-up questions based on extracted recipe information.
    
    Takes the HTML table output from ask_openai_image and answers user questions
    about the recipes, their health implications, and other relevant information.
    
    Args:
        answer: HTML string containing extracted recipe information and metadata
        question: User's follow-up question about the recipes
        
    Returns:
        String containing the answer from OpenAI API
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer the user's question using the following extracted information from an image, a recipe, and its metadata."},
                {"role": "user", "content": f"Extracted info and recipe:\n{answer}\n\nQuestion: {question}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Main upload and chat interface endpoint.
    
    Handles file uploads and question submission:
    1. POST with image file: Extract recipes and display results
    2. POST with question: Answer question based on previous extraction or find recent image
    
    Returns:
        Rendered HTML template with filename, question, answer, and followup response
    """
    filename = None
    question = None
    answer = None
    followup = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        question = request.form.get('question')

        # Handle image file upload
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = uploaded_file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in {'png', 'jpg', 'jpeg'}:
                # Process image and extract recipes
                answer = ask_openai_image(file_path)
        elif question:
            # Handle follow-up question
            # If answer already exists (from image upload), use it for follow-up
            if answer:
                print(answer)
                print(question)
                followup = ask_openai_over_image_output(answer, question)
                print(followup)
            else:
                # Find the most recently uploaded image by modification time
                uploaded_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(f)]
                if uploaded_files:
                    uploaded_files.sort(key=lambda f: os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f)), reverse=True)
                    filename = uploaded_files[0]
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    answer = ask_openai_image(file_path)
                    print(answer)
                    print(question)
                    followup = ask_openai_over_image_output(answer, question)
                    print(followup)
                else:
                    answer = "No image uploaded."
    return render_template('menu_chat.html', filename=filename, question=question, answer=answer, followup=followup)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
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
    # Start Flask development server with debugging enabled
    app.run(debug=True)
