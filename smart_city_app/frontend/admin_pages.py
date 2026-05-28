import streamlit as st

from backend import services
from frontend.components import dataframe, dict_table, show_message


def render_admin_pages(reference_data):
    tabs = st.tabs([
        "Reports",
        "Analytics",
        "Department Workload",
        "Top Users",
        "InfluxDB",
    ])
    with tabs[0]:
        render_reports_tab(reference_data)
    with tabs[1]:
        render_analytics_tab()
    with tabs[2]:
        render_workload_tab()
    with tabs[3]:
        render_top_users_tab()
    with tabs[4]:
        render_influx_tab()


def _select_optional(label, values):
    return st.selectbox(label, ["All"] + list(values))


def render_reports_tab(reference_data):
    st.subheader("View All Reports")
    col1, col2, col3 = st.columns(3)
    with col1:
        report_type = _select_optional("Type", reference_data.get("report_types", []))
        area = _select_optional("Area", reference_data.get("areas", []))
    with col2:
        status = _select_optional("Status", reference_data.get("statuses", []))
        departments = [d.get("dep_id") for d in reference_data.get("departments", [])]
        department_id = _select_optional("Department", departments)
    with col3:
        users = [u.get("user_id") for u in reference_data.get("users", [])]
        user_id = _select_optional("User", users)

    filters = {
        "report_type": None if report_type == "All" else report_type,
        "area": None if area == "All" else area,
        "status": None if status == "All" else status,
        "department_id": None if department_id == "All" else department_id,
        "user_id": None if user_id == "All" else user_id,
    }
    result = services.get_admin_reports_service(filters)
    reports = result.get("reports", [])
    dataframe(reports)

    report_ids = [report["report_id"] for report in reports]
    if report_ids:
        st.divider()
        selected_report = st.selectbox("Report to delete", report_ids)
        if st.button("Delete selected report", type="primary"):
            show_message(services.delete_report_service(selected_report))
            st.rerun()


def render_analytics_tab():
    dashboard = services.get_admin_dashboard_service(hours=24).get("dashboard", {})
    redis_data = dashboard.get("redis", {})
    st.metric("Active sessions", redis_data.get("active_sessions", 0))
    col1, col2 = st.columns(2)
    with col1:
        st.write("Issue counters")
        dict_table(redis_data.get("issue_counters") or dashboard.get("mongo_status_counts", {}), "issue", "count")
        st.write("Busiest areas")
        dict_table(redis_data.get("area_counters") or dashboard.get("mongo_area_counts", {}), "area", "count")
    with col2:
        st.write("Average response times")
        dict_table(redis_data.get("avg_response_times", {}), "area", "minutes")
        st.write("Top issue types cache")
        dataframe(redis_data.get("top_issue_types") or [])


def render_workload_tab():
    dashboard = services.get_admin_dashboard_service(hours=24).get("dashboard", {})
    if dashboard.get("neo4j_warning"):
        st.warning(f"Neo4j unavailable: {dashboard['neo4j_warning']}")
    dataframe(dashboard.get("department_workload", []))


def render_top_users_tab():
    dashboard = services.get_admin_dashboard_service(hours=24).get("dashboard", {})
    dataframe(dashboard.get("users_with_most_reports", []))


def render_influx_tab():
    hours = st.number_input("Reports in last X hours", min_value=1, max_value=720, value=24)
    dashboard = services.get_admin_dashboard_service(hours=hours).get("dashboard", {})
    if dashboard.get("influx_warning"):
        st.warning(f"InfluxDB unavailable: {dashboard['influx_warning']}")
    st.metric(f"Reports/events in last {hours} hours", dashboard.get("reports_last_x_hours") or 0)
    st.write("Average response time by area")
    dict_table(
        dashboard.get("influx_response_by_area") or dashboard.get("redis", {}).get("avg_response_times", {}),
        "area",
        "minutes",
    )

