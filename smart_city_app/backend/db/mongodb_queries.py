from datetime import datetime


def _without_id():
    return {"_id": 0}


def get_all_reports(db):
    return list(db.reports.find({}, _without_id()).sort("submitted_at", -1))


def get_reports_filtered(db, report_type=None, area=None, status=None, department_id=None, user_id=None):
    query = {}
    if report_type:
        query["type"] = report_type
    if area:
        query["area"] = area
    if status:
        query["status"] = status
    if department_id:
        query["assigned_to"] = department_id
    if user_id:
        query["user_id"] = user_id
    return list(db.reports.find(query, _without_id()).sort("submitted_at", -1))


def delete_report_by_id(db, report_id):
    result = db.reports.delete_one({"report_id": report_id})
    return result.deleted_count


def create_report_mongodb(db, report_id, user_id, area, report_type, comment, department_id):
    document = {
        "report_id": report_id,
        "user_id": user_id,
        "area": area,
        "type": report_type,
        "comment": comment,
        "status": "submitted",
        "submitted_at": datetime.now(),
        "assigned_to": department_id,
        "response_time": None,
        "resolved_at": None,
    }
    db.reports.insert_one(document)
    document.pop("_id", None)
    return document


def find_department_for_report(db, report_type, area):
    # Supports both the current seed shape (single-item lists) and normalized strings.
    return db.departments.find_one(
        {
            "$and": [
                {"$or": [{"type": report_type}, {"type": {"$in": [report_type]}}]},
                {"$or": [{"area": area}, {"area": {"$in": [area]}}]},
            ]
        },
        _without_id(),
    )


def get_reports_by_user(db, user_id):
    return list(db.reports.find({"user_id": user_id}, _without_id()).sort("submitted_at", -1))


def get_reports_by_department(db, department_id):
    return list(db.reports.find({"assigned_to": department_id}, _without_id()).sort("submitted_at", -1))


def get_department_reports_by_status(db, department_id, status):
    return list(
        db.reports.find({"assigned_to": department_id, "status": status}, _without_id()).sort("submitted_at", -1)
    )


def update_report_status(db, report_id, new_status):
    report = db.reports.find_one({"report_id": report_id})
    if not report:
        return None

    updates = {"status": new_status}
    if new_status == "resolved":
        resolved_at = datetime.now()
        submitted_at = report.get("submitted_at") or resolved_at
        response_time = int((resolved_at - submitted_at).total_seconds() / 60)
        updates["resolved_at"] = resolved_at
        updates["response_time"] = max(response_time, 0)

    db.reports.update_one({"report_id": report_id}, {"$set": updates})
    return get_report_by_id(db, report_id)


def get_report_by_id(db, report_id):
    return db.reports.find_one({"report_id": report_id}, _without_id())


def count_reports_by_area(db):
    pipeline = [
        {"$group": {"_id": "$area", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return {row["_id"]: row["count"] for row in db.reports.aggregate(pipeline)}


def count_reports_by_status(db):
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    return {row["_id"]: row["count"] for row in db.reports.aggregate(pipeline)}


def get_distinct_report_types(db):
    return sorted([value for value in db.reports.distinct("type") if value])


def get_distinct_areas(db):
    return sorted([value for value in db.reports.distinct("area") if value])


def get_distinct_statuses(db):
    return sorted([value for value in db.reports.distinct("status") if value])


def get_all_departments(db):
    return list(db.departments.find({}, _without_id()).sort("dep_id", 1))


def get_all_users(db):
    return list(db.citizens.find({}, _without_id()).sort("user_id", 1))

