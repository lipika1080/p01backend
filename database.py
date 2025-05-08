import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)

mongo = PyMongo()

def init_db(app):
    uri    = os.getenv("COSMOS_MONGO_URI")
    dbname = os.getenv("COSMOS_DBNAME")
    if not uri or not dbname:
        raise RuntimeError("Set COSMOS_MONGO_URI and COSMOS_DBNAME in .env")
    # include DB name in URI path
    if not uri.endswith(f"/{dbname}"):
        uri = uri.rstrip("/") + f"/{dbname}"
    app.config["MONGO_URI"] = uri
    mongo.init_app(app)
    return mongo