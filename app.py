import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask_pymongo import PyMongo  # Ensure you have imported PyMongo for MongoDB connection

# load .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure OpenAI settings
AZURE_ENDPOINT      = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_KEY           = os.getenv("AZURE_OPENAI_KEY")
AZURE_DEPLOYMENT_ID = os.getenv("AZURE_DEPLOYMENT_ID")
API_VERSION         = "2025-01-01-preview"
CHAT_URL = f"{AZURE_ENDPOINT}"

if not (AZURE_ENDPOINT and AZURE_KEY and AZURE_DEPLOYMENT_ID):
    raise RuntimeError("Missing Azure OpenAI config in .env")

# Initialize MongoDB connection (Ensure you are using the correct Mongo URI)
mongo_uri = os.getenv("COSMOS_MONGO_URI")  # Use your CosmosDB URI here
app.config["MONGO_URI"] = mongo_uri
mongo = PyMongo(app)
db = mongo.db

@app.route("/notes", methods=["POST"])
def create_note():
    data = request.get_json() or {}
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return jsonify({"error": "title & content required"}), 400
    doc = {"title": title, "content": content, "summary": None}
    result = db.notes.insert_one(doc)
    return jsonify({"id": str(result.inserted_id)}), 201

@app.route("/notes", methods=["GET"])
def list_notes():
    notes = []
    for n in db.notes.find():
        n['_id'] = str(n['_id'])
        notes.append(n)
    return jsonify(notes), 200

@app.route("/notes/<note_id>/summarize", methods=["POST"])
def summarize_note(note_id):
    note = db.notes.find_one({"_id": ObjectId(note_id)})
    if not note:
        return jsonify({"error": "not found"}), 404

    headers = {"Content-Type": "application/json", "api-key": AZURE_KEY}
    body = {
        "messages": [
            {"role": "system", "content": "You summarize meeting notes."},
            {"role": "user", "content": note['content']}
        ],
        "temperature": 0.3
    }

    resp = requests.post(CHAT_URL, headers=headers, json=body)
    resp.raise_for_status()
    result = resp.json()
    summary = result['choices'][0]['message']['content'].strip()

    db.notes.update_one({"_id": ObjectId(note_id)}, {"$set": {"summary": summary}})
    return jsonify({"summary": summary}), 200

if __name__ == '__main__':
    # Use Gunicorn to handle production deployment
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)  # Remove gunicorn config here, Azure handles it
