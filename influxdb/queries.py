"""Compatibility wrapper for the Streamlit app InfluxDB query functions.

No database calls are executed automatically when this module is imported.
"""

from smart_city_app.backend.db.influx_queries import (  # noqa: F401
    get_avg_response_time_last_30_days,
    get_reports_count_last_x_hours,
    get_response_time_by_area,
    write_report_event,
)


if __name__ == "__main__":
    print("Import this module and call its functions with an InfluxDB query/write API.")

