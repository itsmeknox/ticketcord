from pymongo import MongoClient
import os

class MongoDBConnection:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.database = self.client[db_name]

    def get_database(self):
        return self.database

# Initialize the MongoDB connection when the module is imported
mongo_connection = MongoDBConnection(os.getenv("MONGO_URI"), os.getenv("DB_NAME"))

def get_database():
    return mongo_connection.get_database()