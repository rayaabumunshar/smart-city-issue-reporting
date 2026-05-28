
import pandas as pd
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
username = "neo4j"
password = "12345678"


driver = GraphDatabase.driver(uri, auth=(username, password))

users = pd.read_csv("../data/users.csv")
departments = pd.read_csv("../data/departments.csv")
reports = pd.read_csv("../data/reports.csv")

with driver.session() as session:

    for _, row in users.iterrows():
        session.run(
            """
            CREATE (:User {
                user_id: $user_id,
                username: $username
            })
            """,
            user_id=row["user_id"],
            username=row["username"]
        )

    for _, row in departments.iterrows():
        session.run(
            """
            CREATE (:Department {
                dep_id: $dep_id,
                name: $name,
                type: $type,
                area: $area
            })
            """,
            dep_id=row["dep_id"],
            name=row["name"],
            type=row["type"],
            area=row["area"]
        )

    for _, row in reports.iterrows():
        session.run(
            """
            CREATE (r:Report {
                report_id: $report_id,
                type: $type,
                area: $area,
                status: $status,
                response_time: $response_time
            })
            """,
            report_id=row["report_id"],
            type=row["type"],
            area=row["area"],
            status=row["status"],
            response_time=row["response_time"]
        )

        session.run(
            """
            MATCH (u:User {user_id: $user_id})
            MATCH (r:Report {report_id: $report_id})
            CREATE (u)-[:REPORTED]->(r)
            """,
            user_id=row["user_id"],
            report_id=row["report_id"]
        )

        session.run(
            """
            MATCH (d:Department {dep_id: $dep_id})
            MATCH (r:Report {report_id: $report_id})
            CREATE (d)-[:HANDLES]->(r)
            """,
            dep_id=row["department_id"],
            report_id=row["report_id"]
        )

print("Neo4j data inserted")
