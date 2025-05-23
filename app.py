# Updated app.py to include GET endpoint for saved summaries

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv
from database import save_summary, get_all_summaries

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_version = "2023-05-15"
deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME")

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    note = data.get("note", "")

    if not note:
        return jsonify({"error": "Note content is required."}), 400

    try:
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes meeting notes."},
                {"role": "user", "content": note}
            ]
        )
        summary = response.choices[0].message['content']
        save_summary(note, summary)

        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summaries', methods=['GET'])
def summaries():
    try:
        summaries = get_all_summaries()
        return jsonify(summaries)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
