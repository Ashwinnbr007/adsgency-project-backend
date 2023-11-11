from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI")
# MongoDB connection details
client = MongoClient(mongo_uri)
# Databases
books_db = client.books
users_db = client.users
comments_db = client.comments
# Collections
books_collection = books_db["books_data"]
users_collection = users_db["user_data"]
comments_collection = comments_db["comments_data"]
