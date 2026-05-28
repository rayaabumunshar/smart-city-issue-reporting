def create_report_in_neo4j(session, report_id, user_id, department_id, report_type, area):
    query = """
    MATCH (u:User {user_id: $user_id})
    MATCH (d:Department {dep_id: $department_id})
    CREATE (r:Report {
        report_id: $report_id,
        type: $report_type,
        area: $area,
        status: "submitted",
        response_time: null
    })
    CREATE (u)-[:REPORTED]->(r)
    CREATE (d)-[:HANDLES]->(r)
    RETURN u.user_id AS user_id, r.report_id AS report_id, d.dep_id AS department_id
    """
    record = session.run(
        query,
        report_id=report_id,
        user_id=user_id,
        department_id=department_id,
        report_type=report_type,
        area=area,
    ).single()
    return record.data() if record else None


def delete_report_in_neo4j(session, report_id):
    query = """
    MATCH (r:Report {report_id: $report_id})
    DETACH DELETE r
    """
    session.run(query, report_id=report_id)


def update_report_status_neo4j(session, report_id, new_status):
    query = """
    MATCH (r:Report {report_id: $report_id})
    SET r.status = $new_status
    RETURN r.report_id AS report_id, r.status AS status
    """
    record = session.run(query, report_id=report_id, new_status=new_status).single()
    return record.data() if record else None


def get_department_workload(session):
    query = """
    MATCH (d:Department)-[:HANDLES]->(r:Report)
    WHERE r.status IN ["submitted", "in_progress"]
    RETURN d.dep_id AS department_id,
           d.name AS department_name,
           d.area AS area,
           d.type AS issue_type,
           count(r) AS active_reports,
           sum(CASE WHEN r.status = "submitted" THEN 1 ELSE 0 END) AS waiting_reports,
           sum(CASE WHEN r.status = "in_progress" THEN 1 ELSE 0 END) AS in_progress_reports
    ORDER BY active_reports DESC
    """
    return [record.data() for record in session.run(query)]


def get_users_with_most_reports(session, limit=10):
    query = """
    MATCH (u:User)-[:REPORTED]->(r:Report)
    RETURN u.user_id AS user_id,
           u.username AS username,
           count(r) AS total_reports
    ORDER BY total_reports DESC
    LIMIT $limit
    """
    return [record.data() for record in session.run(query, limit=limit)]


def get_one_department_status(session, department_id):
    query = """
    MATCH (d:Department {dep_id: $department_id})-[:HANDLES]->(r:Report)
    RETURN d.dep_id AS department_id,
           d.name AS department_name,
           d.area AS area,
           d.type AS issue_type,
           count(r) AS total_reports,
           sum(CASE WHEN r.status = "submitted" THEN 1 ELSE 0 END) AS waiting_reports,
           sum(CASE WHEN r.status = "in_progress" THEN 1 ELSE 0 END) AS in_progress_reports,
           sum(CASE WHEN r.status = "resolved" THEN 1 ELSE 0 END) AS resolved_reports
    """
    record = session.run(query, department_id=department_id).single()
    return record.data() if record else None

