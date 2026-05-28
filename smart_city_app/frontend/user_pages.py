import streamlit as st

from backend import services
from frontend.components import dataframe, show_message


def render_user_pages(user_id, reference_data):
    tab_submit, tab_reports = st.tabs(["Submit Report", "My Reports"])
    with tab_submit:
        with st.form("submit_report_form"):
            st.text_input("User ID", value=user_id, disabled=True)
            report_type = st.selectbox("Report type", reference_data.get("report_types", []))
            area = st.selectbox("Area", reference_data.get("areas", []))
            comment = st.text_area("Comment")
            submitted = st.form_submit_button("Submit report", type="primary")
        if submitted:
            if not comment.strip():
                st.error("Please add a short comment.")
            else:
                result = services.submit_report_service(user_id, report_type, area, comment.strip())
                show_message(result)
                report = result.get("report", {})
                for warning_key in ("neo4j_warning", "influx_warning"):
                    if report.get(warning_key):
                        st.warning(report[warning_key])

    with tab_reports:
        result = services.get_user_reports_service(user_id)
        if not result.get("success"):
            show_message(result)
        dataframe(result.get("reports", []), "You have not submitted any reports yet.")

