import csv
import random
from datetime import datetime, timedelta

areas = [
    "Downtown",
    "Old City",
    "University",
    "Industrial Zone",
    "North District",
    "South District",
    "East Side",
    "West Side"
]

issue_types = [
    "trash",
    "electricity",
    "traffic",
    "water",
    "road_damage"
]

comments = {
    "trash": [
        "Garbage container overflowing",
        "Trash not collected",
        "Bad smell from waste area"
    ],
    "electricity": [
        "Street light not working",
        "Power outage in neighborhood",
        "Electrical sparks near pole"
    ],
    "traffic": [
        "Heavy traffic near intersection",
        "Traffic light malfunction",
        "Road congestion during rush hour"
    ],
    "water": [
        "Water leakage from pipe",
        "No water supply",
        "Flooding near building"
    ],
    "road_damage": [
        "Large pothole on road",
        "Road cracks becoming dangerous",
        "Damaged sidewalk"
    ]
}

statuses = [
    "submitted",
    "in_progress",
    "resolved"
]

# ---------------- USERS ----------------

users = []

for i in range(1, 121):
    users.append([
        f"U{i:03}",
        f"user_{i}",
        "1234"
    ])

with open("users.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "user_id",
        "username",
        "password"
    ])
    writer.writerows(users)

# ---------------- DEPARTMENTS ----------------

# One department for each area + issue type combination
# 8 areas × 5 issue types = 40 departments

departments = []
dep_counter = 1

for area in areas:
    for issue_type in issue_types:
        departments.append([
            f"D{dep_counter:03}",
            f"{area} {issue_type} department",
            issue_type,
            area
        ])
        dep_counter += 1

with open("departments.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "dep_id",
        "name",
        "type",
        "area"
    ])
    writer.writerows(departments)

# ---------------- REPORTS ----------------

reports = []

start_time = datetime(2026, 5, 1, 8, 0, 0)

for i in range(1, 401):

    issue_type = random.choice(issue_types)
    user = random.choice(users)

    area = random.choice(areas)

    # Because every area has every department type,
    # this always finds exactly one matching department.
    matching_department = next(
        d for d in departments
        if d[2] == issue_type and d[3] == area
    )

    status_weights = [0.35, 0.40, 0.25]
    status = random.choices(statuses, weights=status_weights)[0]

    report_time = start_time + timedelta(
        minutes=random.randint(0, 10000)
    )

    response_time = None

    if status == "resolved":
        response_time = random.randint(10, 240)

    reports.append([
        f"R{i:03}",
        issue_type,
        random.choice(comments[issue_type]),
        area,
        user[0],
        status,
        report_time.isoformat(),
        response_time,
        matching_department[0]
    ])

with open("reports.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "report_id",
        "type",
        "comment",
        "area",
        "user_id",
        "status",
        "report_time",
        "response_time",
        "department_id"
    ])
    writer.writerows(reports)

print("Dataset generated successfully")
