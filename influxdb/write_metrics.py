import pandas as pd

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


URL = "http://localhost:8086"

TOKEN = "token"

ORG = "smart_city"

BUCKET = "Smart_City_Bucket"


client = InfluxDBClient(
    url=URL,
    token=TOKEN,
    org=ORG
)

write_api = client.write_api(write_options=SYNCHRONOUS)


reports = pd.read_csv("../data/reports.csv")


for _, row in reports.iterrows():

    if pd.notna(row["response_time"]):
        response_time = float(row["response_time"])
    else:
        response_time = 0.0   

    point = (
        Point("report_events")

        .tag("area", str(row["area"]))
        .tag("type", str(row["type"]))
        .tag("status", str(row["status"]))

        .field("response_time", float(response_time))  
        .field("report_id", str(row["report_id"]))

        .time(row["report_time"], WritePrecision.NS)
    )

    write_api.write(
        bucket=BUCKET,
        org=ORG,
        record=point
    )


print("Data inserted into InfluxDB successfully!")

client.close()
