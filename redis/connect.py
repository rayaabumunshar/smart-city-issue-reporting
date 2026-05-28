# redis/connect.py
import redis
print("=" * 40)
print("Redis Connection Test")
print("=" * 40)

try:

    r = redis.Redis(host='localhost', port=6379, db=0)
    response = r.ping()
    if response:
        print(" SUCCESS! Connected to Redis")
        print(f" Host: localhost:6379")
        print(f" Redis Version: {r.info()['redis_version']}")
    
except Exception as e:
    print(" FAILED! Could not connect to Redis")
    print(f"Error: {e}")
    print("\n Make sure you started redis on docker!")
    print("\n docker start redis")