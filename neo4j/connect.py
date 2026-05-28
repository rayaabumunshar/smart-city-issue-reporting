# neo4j/connect.py
from neo4j import GraphDatabase

print("=" * 40)
print("Neo4j Connection Test")
print("=" * 40)

# Neo4j connection details
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    driver.verify_connectivity()
    print(" SUCCESS! Connected to Neo4j")
    print(f" URI: {URI}")
    print(f" User: {USER}")
    driver.close()
    
except Exception as e:
    print(" FAILED! Could not connect to Neo4j")
    print(f"Error: {e}")
    print("\n Make sure you started neo4j on docker!")
    print("docker start neo4j")