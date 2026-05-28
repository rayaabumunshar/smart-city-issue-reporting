import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from backend import config  # noqa: E402
from backend.connections import get_influx_write_api, get_mongo_db, get_neo4j_driver, get_redis_client  # noqa: E402
from backend.db.influx_queries import write_report_event  # noqa: E402


DATA_DIR = REPO_ROOT / "data"


def read_csv(name):
    with open(DATA_DIR / name, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def seed_mongodb(users, departments, reports):
    db = get_mongo_db()
    db.reports.delete_many({})
    db.citizens.delete_many({})
    db.departments.delete_many({})

    db.departments.insert_many(
        [
            {
                "dep_id": row["dep_id"],
                "name": row["name"],
                "type": row["type"],
                "area": row["area"],
            }
            for row in departments
        ]
    )
    db.citizens.insert_many(
        [
            {
                "user_id": row["user_id"],
                "username": row["username"],
                "email": f"{row['username']}@city.com",
                "created_at": datetime.now(),
            }
            for row in users
        ]
    )
    db.reports.insert_many(
        [
            {
                "report_id": row["report_id"],
                "user_id": row["user_id"],
                "area": row["area"],
                "type": row["type"],
                "comment": row["comment"],
                "status": row["status"],
                "submitted_at": datetime.fromisoformat(row["report_time"]),
                "assigned_to": row["department_id"],
                "response_time": int(row["response_time"]) if row["response_time"] else None,
                "resolved_at": None,
            }
            for row in reports
        ]
    )

    db.departments.create_index("dep_id", unique=True)
    db.citizens.create_index("user_id", unique=True)
    db.reports.create_index("report_id", unique=True)


def seed_neo4j(users, departments, reports):
    driver = get_neo4j_driver()
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        for row in users:
            session.run(
                "CREATE (:User {user_id: $user_id, username: $username})",
                user_id=row["user_id"],
                username=row["username"],
            )
        for row in departments:
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
                area=row["area"],
            )
        for row in reports:
            response_time = int(row["response_time"]) if row["response_time"] else None
            session.run(
                """
                MATCH (u:User {user_id: $user_id})
                MATCH (d:Department {dep_id: $department_id})
                CREATE (r:Report {
                    report_id: $report_id,
                    type: $type,
                    area: $area,
                    status: $status,
                    response_time: $response_time
                })
                CREATE (u)-[:REPORTED]->(r)
                CREATE (d)-[:HANDLES]->(r)
                """,
                user_id=row["user_id"],
                department_id=row["department_id"],
                report_id=row["report_id"],
                type=row["type"],
                area=row["area"],
                status=row["status"],
                response_time=response_time,
            )


def seed_redis(reports):
    r = get_redis_client()
    for key in r.scan_iter("issue_counter:*"):
        r.delete(key)
    for key in r.scan_iter("area_counter:*"):
        r.delete(key)
    for key in r.scan_iter("avg_response_time:*"):
        r.delete(key)
    for key in r.scan_iter("response_time_count:*"):
        r.delete(key)

    issue_counts = Counter(row["type"] for row in reports)
    area_counts = Counter(row["area"] for row in reports)
    area_response_times = defaultdict(list)
    for row in reports:
        if row["response_time"]:
            area_response_times[row["area"]].append(int(row["response_time"]))

    for issue_type, count in issue_counts.items():
        r.set(f"issue_counter:{issue_type}", count)
    for area, count in area_counts.items():
        r.set(f"area_counter:{area.replace(' ', '_')}", count)
    for area, times in area_response_times.items():
        key = area.replace(" ", "_")
        r.set(f"avg_response_time:{key}", round(sum(times) / len(times), 2))
        r.set(f"response_time_count:{key}", len(times))


def seed_influx(reports):
    write_api = get_influx_write_api()
    for row in reports:
        write_report_event(
            write_api,
            config.INFLUX_BUCKET,
            config.INFLUX_ORG,
            row["report_id"],
            row["type"],
            row["area"],
            row["status"],
            int(row["response_time"]) if row["response_time"] else None,
        )


def main():
    users = read_csv("users.csv")
    departments = read_csv("departments.csv")
    reports = read_csv("reports.csv")
    seed_mongodb(users, departments, reports)
    seed_neo4j(users, departments, reports)
    seed_redis(reports)
    seed_influx(reports)
    print("Seed data loaded into MongoDB, Neo4j, Redis, and InfluxDB.")


if __name__ == "__main__":
    main()

