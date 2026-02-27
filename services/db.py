from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["xtrack"]
expenses = db["expenses"]

expenses.create_index([("channel_id", 1), ("user_id", 1), ("message_id", 1)])