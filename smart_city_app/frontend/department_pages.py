import streamlit as st

from backend import services
from frontend.components import dataframe, show_message


ALLOWED_STATUSES = ["submitted", "in_progress", "resolved", "rejected"]


def render_department_pages(department_id):
    tabs = st.tabs(["Assigned Reports", "Filter By Status", "Update Status", "Department Analytics"])
    with tabs[0]:
        result = services.get_department_reports_service(department_id)
        dataframe(result.get("reports", []), "No reports assigned to this department.")

    with tabs[1]:
        status = st.selectbox("Status", ["All"] + ALLOWED_STATUSES)
        result = services.get_department_reports_service(department_id, None if status == "All" else status)
        dataframe(result.get("reports", []))

    with tabs[2]:
        result = services.get_department_reports_service(department_id)
        reports = result.get("reports", [])
        report_ids = [report["report_id"] for report in reports]
        if not report_ids:
            st.info("No assigned reports to update.")
        else:
            with st.form("update_status_form"):
                report_id = st.selectbox("Report ID", report_ids)
                new_status = st.selectbox("New status", ALLOWED_STATUSES)
                submitted = st.form_submit_button("Update status", type="primary")
            if submitted:
                update_result = services.update_report_status_service(report_id, new_status)
                show_message(update_result)
                report = update_result.get("report", {})
                for warning_key in ("neo4j_warning", "influx_warning"):
                    if report.get(warning_key):
                        st.warning(report[warning_key])
                st.rerun()

    with tabs[3]:
        result = services.get_department_dashboard_service(department_id)
        dashboard = result.get("dashboard", {})
        status = dashboard.get("department_status") or {}
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total reports", status.get("total_reports", len(dashboard.get("reports", []))))
        col2.metric("Waiting", status.get("waiting_reports", 0))
        col3.metric("In progress", status.get("in_progress_reports", 0))
        col4.metric("Resolved", status.get("resolved_reports", 0))
        if dashboard.get("redis_area_stats"):
            st.write("Redis area stats")
            st.json(dashboard["redis_area_stats"])
        if dashboard.get("neo4j_warning"):
            st.warning(f"Neo4j unavailable: {dashboard['neo4j_warning']}")

