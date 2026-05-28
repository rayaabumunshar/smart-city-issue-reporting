import json

from backend.connections import get_redis_client


def _client(redis_client=None):
    return redis_client or get_redis_client()


def _safe(default=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return default
        return wrapper
    return decorator


@_safe(0)
def count_active_sessions(redis_client=None):
    return len(list(_client(redis_client).scan_iter("session:*")))


@_safe({})
def query_all_issue_counters(redis_client=None):
    r = _client(redis_client)
    result = {}
    for key in r.scan_iter("issue_counter:*"):
        result[key.split(":", 1)[1]] = int(r.get(key) or 0)
    return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))


@_safe({})
def query_all_area_counters(redis_client=None):
    r = _client(redis_client)
    result = {}
    for key in r.scan_iter("area_counter:*"):
        area = key.split(":", 1)[1].replace("_", " ")
        result[area] = int(r.get(key) or 0)
    return dict(sorted(result.items(), key=lambda item: item[1], reverse=True))


@_safe({})
def query_all_avg_response_times(redis_client=None):
    r = _client(redis_client)
    result = {}
    for key in r.scan_iter("avg_response_time:*"):
        area = key.split(":", 1)[1].replace("_", " ")
        result[area] = float(r.get(key) or 0)
    return dict(sorted(result.items(), key=lambda item: item[1]))


@_safe(None)
def get_busiest_areas(redis_client=None):
    raw = _client(redis_client).get("cached:busiest_areas")
    return json.loads(raw) if raw else None


@_safe(None)
def get_top_issue_types(redis_client=None):
    raw = _client(redis_client).get("cached:top_issue_types")
    return json.loads(raw) if raw else None


def query_redis_dashboard(redis_client=None):
    return {
        "active_sessions": count_active_sessions(redis_client),
        "issue_counters": query_all_issue_counters(redis_client),
        "area_counters": query_all_area_counters(redis_client),
        "avg_response_times": query_all_avg_response_times(redis_client),
        "busiest_areas": get_busiest_areas(redis_client),
        "top_issue_types": get_top_issue_types(redis_client),
    }


@_safe(None)
def increment_issue_counter(redis_client, report_type):
    return int(_client(redis_client).incr(f"issue_counter:{report_type}"))


@_safe(None)
def increment_area_counter(redis_client, area):
    key = area.replace(" ", "_")
    return int(_client(redis_client).incr(f"area_counter:{key}"))


@_safe(None)
def update_avg_response_time(redis_client, area, response_time):
    r = _client(redis_client)
    key = area.replace(" ", "_")
    count_key = f"response_time_count:{key}"
    avg_key = f"avg_response_time:{key}"
    current_avg = float(r.get(avg_key) or response_time)
    current_count = int(r.get(count_key) or 0)
    new_count = current_count + 1
    new_avg = round(((current_avg * current_count) + response_time) / new_count, 2)
    r.set(avg_key, new_avg)
    r.set(count_key, new_count)
    return new_avg


@_safe(None)
def create_user_session(redis_client, user_id):
    return _client(redis_client).setex(f"session:{user_id}", 3600, "active")


@_safe(None)
def delete_user_session(redis_client, user_id):
    return _client(redis_client).delete(f"session:{user_id}")

