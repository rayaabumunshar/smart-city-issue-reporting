from influxdb_client import Point


def write_report_event(write_api, bucket, org, report_id, report_type, area, status, response_time=None):
    point = (
        Point("report_events")
        .tag("report_id", report_id)
        .tag("type", report_type)
        .tag("area", area)
        .tag("status", status)
        .field("report_count", 1)
    )
    if response_time is not None:
        point = point.field("response_time", float(response_time))
    write_api.write(bucket=bucket, org=org, record=point)
    return True


def get_reports_count_last_x_hours(query_api, bucket, hours):
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -{int(hours)}h)
      |> filter(fn: (r) => r["_measurement"] == "report_events")
      |> filter(fn: (r) => r["_field"] == "report_count")
      |> count()
    '''
    tables = query_api.query(query)
    return sum(record.get_value() for table in tables for record in table.records)


def get_avg_response_time_last_30_days(query_api, bucket):
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "report_events")
      |> filter(fn: (r) => r["_field"] == "response_time")
      |> mean()
    '''
    values = [record.get_value() for table in query_api.query(query) for record in table.records]
    return round(sum(values) / len(values), 2) if values else None


def get_response_time_by_area(query_api, bucket):
    query = f'''
    from(bucket: "{bucket}")
      |> range(start: -30d)
      |> filter(fn: (r) => r["_measurement"] == "report_events")
      |> filter(fn: (r) => r["_field"] == "response_time")
      |> group(columns: ["area"])
      |> mean()
    '''
    result = {}
    for table in query_api.query(query):
        for record in table.records:
            result[record.values.get("area")] = round(record.get_value(), 2)
    return result

