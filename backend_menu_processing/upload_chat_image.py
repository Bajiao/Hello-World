import os
from flask import Flask, request, render_template, render_template_string, send_from_directory
from pathlib import Path
from dotenv import load_dotenv  
import httpx
from PIL import Image
import pytesseract
import base64
import pickle

from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

import pandas as pd
from openai import OpenAI
from langchain.embeddings.base import Embeddings  # Base class for embedding models


# === Setup ===
dotenv_path = Path("OpenAI_API_Key.env")
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OpenAI API key not found.")
else:
    print("API key loaded.")

# === Initialize client ===
client = OpenAI(api_key=openai_api_key, http_client=httpx.Client(verify=False))

# === Custom Embeddings Class ===
class CustomOpenAIEmbeddings(Embeddings):
    """Custom embedding model wrapper for LangChain compatibility."""

    def __init__(self, client):
        self.client = client

    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        response = self.client.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        # Correctly access the embedding data
        return response.data[0].embedding
    
embeddings = CustomOpenAIEmbeddings(client)

print(embeddings)

vectorstore = FAISS.load_local("faiss_vectorstore_recipes", embeddings=embeddings,allow_dangerous_deserialization=True)

with open("./faiss_vectorstore_recipes/faiss_vectorstore_metadatas.pkl", "rb") as f:
    metadatas = pickle.load(f)


# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# OpenAI API Key (secure in production via env variable)

# Helper to check allowed file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Chat function

def ask_openai_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
        ext = image_path.rsplit('.', 1)[1].lower()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:image/{ext};base64,{image_base64}"

        # Step 1: Use OpenAI Vision to extract recipe names as JSON
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
            temperature=0
        )

        import json
        obj = json.loads(response.choices[0].message.content)
        recipes = obj.get("recipes", [])
        print("Extracted recipes:", recipes)

        # Show extracted recipes first
        extracted_html = f"<b>Extracted recipes from image:</b> {', '.join(recipes) if recipes else 'None found'}<br>"

        # Step 2: For each extracted recipe, run vector search and collect results
        # First, collect all metadata keys
        all_keys = set()
        recipe_results = []
        for recipe_query in recipes:
            docs_and_scores = vectorstore.similarity_search_with_score(recipe_query, k=1)
            if docs_and_scores:
                doc, score = docs_and_scores[0]
                meta = doc.metadata if hasattr(doc, 'metadata') else {}
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
        # Build table header
        # Improved table styling for better appearance and width
        results_table = '''
        <div style="overflow-x:auto; margin-top:12px; max-height:500px;">
        <table border="1" style="border-collapse:collapse; width:98%; min-width:800px; background:#fff; font-size:1rem;">
            <thead style="background:#f2f2f2; position:sticky; top:0; z-index:2;">
                <tr>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Recipe Query</th>
                    <th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">Most Matched Recipe</th>
'''  # Start header
        for k in all_keys:
            results_table += f'<th style="padding:8px; position:sticky; top:0; background:#f2f2f2;">{k}</th>'
        results_table += '''
                </tr>
            </thead>
            <tbody>
'''
        # Build table rows
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


# Function to chat over the output of ask_openai_image
def ask_openai_over_image_output(answer, question):
    """
    Given the output from ask_openai_image (containing extracted info, recipe, and metadata),
    and a user question, use OpenAI to answer the question based on that output.
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




# Route for upload and chat
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    filename = None
    question = None
    answer = None
    followup = None
    doc_text = None

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        question = request.form.get('question')

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = uploaded_file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(file_path)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in {'png', 'jpg', 'jpeg'}:
                answer = ask_openai_image(file_path)
        elif question:
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

# Serve uploaded PDFs
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
