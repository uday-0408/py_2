# App/DB/db.py

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
mongo_db = client["codingPlatform"]
submissions_collection = mongo_db["submissions"]
