from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(
    MONGO_URI,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,
    tlsAllowInvalidHostnames=True
)

db = client["civic_copilot"]
complaints_collection = db["complaints"]