from influxdb_client import InfluxDBClient

print("=" * 40)
print("InfluxDB Connection Test")
print("=" * 40)

URL = "http://localhost:8086"
TOKEN = "token"
ORG = "smart_city"
BUCKET = "Smart_City_Bucket"

try:
    client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
    
    health = client.health()
    
    print("SUCCESS! Connected to InfluxDB")
    print(f" URL: {URL}")
    print(f"Status: {health.status}")
    print(f" Bucket: {BUCKET}")
    
    client.close()
    
except Exception as e:
    print("FAILED! Could not connect to InfluxDB")
    print(f"Error: {e}")
    print("\n Make sure you started influxdb on docker!")
    print("\ndocker start influxdb")
