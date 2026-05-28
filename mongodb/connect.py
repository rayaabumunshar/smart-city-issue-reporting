# mongodb/connect.py
from pymongo import MongoClient

print("=" * 40)
print("MongoDB Connection Test")
print("=" * 40)
try:
    client = MongoClient("mongodb://localhost:27017")
    db = client.smart_city
    server_info = client.server_info()
    
    print("SUCCESS! Connected to MongoDB")
    print(f" MongoDB Version: {server_info.get('version', 'unknown')}")
    print(f" Database name: smart_city")
    
except Exception as e:
    print("FAILED! Could not connect to MongoDB")
    print(f"Error: {e}")
    print("\n Make sure you started mongodb on docker!")
    print("\ndocker start neo4j")
