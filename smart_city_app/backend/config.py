import os


try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # The app still works from real environment variables if python-dotenv
    # has not been installed yet.
    pass

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "smart_city")

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "12345678")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "smart_city")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "Smart_City_Bucket")
