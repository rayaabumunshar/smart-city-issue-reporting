from uuid import uuid4

from backend import config
from backend.connections import (
    get_influx_query_api,
    get_influx_write_api,
    get_mongo_db,
    get_neo4j_driver,
    get_redis_client,
)
from backend.db import influx_queries, mongodb_queries, neo4j_queries, redis_queries


def _ok(message, **data):
    return {"success": True, "message": message, **data}


def _error(message, **data):
    return {"success": False, "message": message, **data}


def _try_redis():
    try:
        return get_redis_client()
    except Exception:
        return None


def _try_influx_write():
    try:
        return get_influx_write_api()
    except Exception:
        return None


def _try_influx_query():
    try:
        return get_influx_query_api()
    except Exception:
        return None


def get_reference_data_service():
    try:
        db = get_mongo_db()
        return _ok(
            "Reference data loaded.",
            report_types=mongodb_queries.get_distinct_report_types(db),
            areas=mongodb_queries.get_distinct_areas(db),
            statuses=mongodb_queries.get_distinct_statuses(db),
            departments=mongodb_queries.get_all_departments(db),
            users=mongodb_queries.get_all_users(db),
        )
    except Exception as exc:
        return _error(f"Could not load reference data: {exc}")


def submit_report_service(user_id, report_type, area, comment):
    try:
        db = get_mongo_db()
        department = mongodb_queries.find_department_for_report(db, report_type, area)
        if not department:
            return _error(f"No department handles {report_type} in {area}.")

        department_id = department["dep_id"]
        report_id = f"R-{uuid4().hex[:8].upper()}"
        report = mongodb_queries.create_report_mongodb(
            db, report_id, user_id, area, report_type, comment, department_id
        )

        try:
            with get_neo4j_driver().session() as session:
                created = neo4j_queries.create_report_in_neo4j(
                    session, report_id, user_id, department_id, report_type, area
                )
            if not created:
                report["neo4j_warning"] = "Neo4j did not create relationships. Check seeded users/departments."
        except Exception as exc:
            report["neo4j_warning"] = f"Neo4j update failed: {exc}"

        redis_client = _try_redis()
        if redis_client:
            redis_queries.increment_issue_counter(redis_client, report_type)
            redis_queries.increment_area_counter(redis_client, area)

        write_api = _try_influx_write()
        if write_api:
            try:
                influx_queries.write_report_event(
                    write_api, config.INFLUX_BUCKET, config.INFLUX_ORG, report_id, report_type, area, "submitted"
                )
            except Exception as exc:
                report["influx_warning"] = f"InfluxDB write failed: {exc}"

        return _ok("Report submitted successfully.", report=report)
    except Exception as exc:
        return _error(f"Could not submit report: {exc}")


def delete_report_service(report_id):
    try:
        db = get_mongo_db()
        deleted = mongodb_queries.delete_report_by_id(db, report_id)
        try:
            with get_neo4j_driver().session() as session:
                neo4j_queries.delete_report_in_neo4j(session, report_id)
        except Exception as exc:
            return _ok(f"Deleted from MongoDB, but Neo4j delete failed: {exc}", deleted_count=deleted)
        if deleted:
            return _ok("Report deleted from MongoDB and Neo4j.", deleted_count=deleted)
        return _error("No report was found with that report_id.", deleted_count=0)
    except Exception as exc:
        return _error(f"Could not delete report: {exc}")


def update_report_status_service(report_id, new_status):
    try:
        db = get_mongo_db()
        report = mongodb_queries.update_report_status(db, report_id, new_status)
        if not report:
            return _error("No report was found with that report_id.")

        try:
            with get_neo4j_driver().session() as session:
                neo4j_queries.update_report_status_neo4j(session, report_id, new_status)
        except Exception as exc:
            report["neo4j_warning"] = f"Neo4j status update failed: {exc}"

        response_time = report.get("response_time")
        if new_status == "resolved" and response_time is not None:
            redis_client = _try_redis()
            if redis_client:
                redis_queries.update_avg_response_time(redis_client, report["area"], response_time)
            write_api = _try_influx_write()
            if write_api:
                try:
                    influx_queries.write_report_event(
                        write_api,
                        config.INFLUX_BUCKET,
                        config.INFLUX_ORG,
                        report_id,
                        report["type"],
                        report["area"],
                        new_status,
                        response_time,
                    )
                except Exception as exc:
                    report["influx_warning"] = f"InfluxDB write failed: {exc}"

        return _ok("Report status updated.", report=report)
    except Exception as exc:
        return _error(f"Could not update report status: {exc}")


def get_admin_reports_service(filters):
    try:
        db = get_mongo_db()
        reports = mongodb_queries.get_reports_filtered(db, **filters)
        return _ok("Reports loaded.", reports=reports)
    except Exception as exc:
        return _error(f"Could not load reports: {exc}", reports=[])


def get_user_reports_service(user_id):
    try:
        return _ok("User reports loaded.", reports=mongodb_queries.get_reports_by_user(get_mongo_db(), user_id))
    except Exception as exc:
        return _error(f"Could not load user reports: {exc}", reports=[])


def get_department_reports_service(department_id, status=None):
    try:
        db = get_mongo_db()
        if status:
            reports = mongodb_queries.get_department_reports_by_status(db, department_id, status)
        else:
            reports = mongodb_queries.get_reports_by_department(db, department_id)
        return _ok("Department reports loaded.", reports=reports)
    except Exception as exc:
        return _error(f"Could not load department reports: {exc}", reports=[])


def get_admin_dashboard_service(hours):
    dashboard = {
        "redis": redis_queries.query_redis_dashboard(_try_redis()),
        "department_workload": [],
        "users_with_most_reports": [],
        "reports_last_x_hours": None,
        "mongo_area_counts": {},
        "mongo_status_counts": {},
    }
    try:
        db = get_mongo_db()
        dashboard["mongo_area_counts"] = mongodb_queries.count_reports_by_area(db)
        dashboard["mongo_status_counts"] = mongodb_queries.count_reports_by_status(db)
    except Exception as exc:
        dashboard["mongo_warning"] = str(exc)

    try:
        with get_neo4j_driver().session() as session:
            dashboard["department_workload"] = neo4j_queries.get_department_workload(session)
            dashboard["users_with_most_reports"] = neo4j_queries.get_users_with_most_reports(session)
    except Exception as exc:
        dashboard["neo4j_warning"] = str(exc)

    query_api = _try_influx_query()
    if query_api:
        try:
            dashboard["reports_last_x_hours"] = influx_queries.get_reports_count_last_x_hours(
                query_api, config.INFLUX_BUCKET, hours
            )
            dashboard["influx_response_by_area"] = influx_queries.get_response_time_by_area(
                query_api, config.INFLUX_BUCKET
            )
        except Exception as exc:
            dashboard["influx_warning"] = str(exc)
    return _ok("Dashboard loaded.", dashboard=dashboard)


def get_department_dashboard_service(department_id):
    result = {"department_status": None, "reports": [], "redis_area_stats": {}}
    try:
        result["reports"] = mongodb_queries.get_reports_by_department(get_mongo_db(), department_id)
    except Exception as exc:
        result["mongo_warning"] = str(exc)

    try:
        with get_neo4j_driver().session() as session:
            result["department_status"] = neo4j_queries.get_one_department_status(session, department_id)
    except Exception as exc:
        result["neo4j_warning"] = str(exc)

    redis_client = _try_redis()
    if redis_client and result["department_status"]:
        area = result["department_status"].get("area")
        area_counters = redis_queries.query_all_area_counters(redis_client)
        avg_times = redis_queries.query_all_avg_response_times(redis_client)
        result["redis_area_stats"] = {
            "area": area,
            "total_reports": area_counters.get(area),
            "avg_response_time": avg_times.get(area),
        }
    return _ok("Department dashboard loaded.", dashboard=result)

