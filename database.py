import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("COSMOS_CONNECTION_STRING"))
db = client["note_app"]
collection = db["summaries"]

def save_summary(note: str, summary: str):
    document = {"note": note, "summary": summary}
    collection.insert_one(document)

def get_all_summaries():
    return list(collection.find({}, {"_id": 0}))
