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
dotenv_path = Path("../API_Key.env")
print(f"Looking for API key file at: {dotenv_path.absolute()}")
print(f"File exists: {dotenv_path.exists()}")

load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    print("Environment variables:", list(os.environ.keys()))
    raise ValueError("OpenAI API key not found.")
else:
    print(f"API key loaded successfully. Length: {len(openai_api_key)} characters")

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

vectorstore = FAISS.load_local("../faiss_vectorstore_recipes", embeddings=embeddings,allow_dangerous_deserialization=True)

with open("../faiss_vectorstore_recipes/faiss_vectorstore_metadatas.pkl", "rb") as f:
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
        # Step 1: Use OpenAI Vision to extract a query from the image
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Analyze the uploaded image and extract the most relevant keywords, ingredients, or recipe names you can infer. Return a concise query string for searching a recipe database."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract a concise search query from this image for recipe search."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
        )
        extracted_query = response.choices[0].message.content.strip()
        # Step 2: Use extracted text as query to the recipes vector store
        # Load the vector store if not already loaded
        print(extracted_query)
        
        docs_and_scores = vectorstore.similarity_search_with_score(extracted_query, k=1)
        if docs_and_scores:
            doc, score = docs_and_scores[0]
            meta = doc.metadata if hasattr(doc, 'metadata') else {}
            print(meta)
            # Try to get recipe name from metadata, fallback to first line of page_content
            recipe_name = meta.get('name') or (doc.page_content.split('\n')[0] if doc.page_content else 'Unknown')
            # Format metadata as an HTML table (each key-value pair per row)
            if meta:
                table = '<table border="1" style="border-collapse:collapse;">'
                table += '<tr><th>Key</th><th>Value</th></tr>'
                for k, v in meta.items():
                    table += f'<tr><td>{k}</td><td>{v}</td></tr>'
                table += '</table>'
            else:
                table = 'No metadata available.'
            return (
                f"<b>What the model thinks is in the image:</b> {extracted_query}<br>"
                f"<b>Most matched recipe:</b> {recipe_name}<br>"
                f"<b>Metadata:</b><br>{table}"
            )
        else:
            return f"Image info extracted: {extracted_query}\nNo relevant recipe found."
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
