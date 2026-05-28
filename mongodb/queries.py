"""Compatibility wrapper for the Streamlit app MongoDB query functions.

The original file contained demo code that ran immediately on import. Keep
imports safe by exposing reusable functions only.
"""

from smart_city_app.backend.db.mongodb_queries import (  # noqa: F401
    count_reports_by_area,
    count_reports_by_status,
    create_report_mongodb,
    delete_report_by_id,
    find_department_for_report,
    get_all_departments,
    get_all_reports,
    get_all_users,
    get_department_reports_by_status,
    get_distinct_areas,
    get_distinct_report_types,
    get_distinct_statuses,
    get_report_by_id,
    get_reports_by_department,
    get_reports_by_user,
    get_reports_filtered,
    update_report_status,
)


if __name__ == "__main__":
    print("Import this module and call its functions with a MongoDB database object.")

