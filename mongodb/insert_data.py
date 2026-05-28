from pymongo import MongoClient 
from datetime import datetime
import csv

client = MongoClient("mongodb://localhost:27017")
db = client.smart_city

# deleted the documents from each collection to avoid duplicates if we run it multiple times 
db.reports.delete_many({})
db.citizens.delete_many({})
db.departments.delete_many({})

# import the departments from the csv file 
with open('data/departments.csv','r') as department:
    read =csv.DictReader(department)
    departments =[]
    for row in read:
        departments.append({"dep_id":row["dep_id"],"name":row["name"],"type":[row["type"]],"area":[row["area"]]})
    if departments:
        db.departments.insert_many(departments)
        print(f"Inserted {len(departments)} departments")

# import the citizens from the csv file 
with open('data/users.csv','r') as citizen:
    read =csv.DictReader(citizen)
    citizens =[]
    for row in read:
        citizens.append({"user_id": row["user_id"],"username": row["username"],"email": f"{row['username']}@city.com","created_at": datetime.now()})
    if citizens:
        db.citizens.insert_many(citizens)
        print(f"Inserted {len(citizens)} citizens")


# import the reports from the csv file 
with open('data/reports.csv','r') as report:
    read = csv.DictReader(report)
    reports =[]
    for row in read:
        submitted_time = datetime.fromisoformat(row["report_time"])
        report_dict = {
            "report_id": row["report_id"],
            "user_id": row["user_id"],
            "area": row["area"],
            "type": row["type"],
            "comment": row["comment"],
            "status": row["status"],
            "submitted_at": submitted_time,
            "assigned_to": row["department_id"]
        }
        if row["response_time"] and row["response_time"] != '':
            report_dict["response_time"] = int(row["response_time"])
            report_dict["resolved_at"] = None
        else:
            report_dict["response_time"] = None
            report_dict["resolved_at"] = None
        reports.append(report_dict)
    if reports:
        db.reports.insert_many(reports)
        print(f"Inserted {len(reports)} reports")

db.departments.create_index("dep_id", unique=True)
db.citizens.create_index("user_id", unique=True)
db.reports.create_index("report_id", unique=True)
print("Indexes created successfully")

