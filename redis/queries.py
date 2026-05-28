"""
Smart City Project — Redis Queries
All read queries used for display, analytics, and the demo.
"""

from connect import r
from cache_operations import (
    get_busiest_areas,
    get_top_issue_types,
    get_avg_response_time,
    count_active_sessions,
)


# ──────────────────────────────────────────────────────────────
# QUERY 1 — All issue counters (sorted descending)
# ──────────────────────────────────────────────────────────────

def query_all_issue_counters():
    """
    Return all issue type counters sorted by count (highest first).
    Example output: {'trash': 72, 'traffic': 65, 'water': 58, ...}
    """
    result = {}
    for key in r.scan_iter("issue_counter:*"):
        issue_type = key.split(":", 1)[1]
        result[issue_type] = int(r.get(key))
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


# ──────────────────────────────────────────────────────────────
# QUERY 2 — All area counters (sorted descending)
# ──────────────────────────────────────────────────────────────

def query_all_area_counters():
    """
    Return all area counters sorted by count (highest first).
    Example output: {'Downtown': 45, 'University': 40, ...}
    """
    result = {}
    for key in r.scan_iter("area_counter:*"):
        area = key.split(":", 1)[1].replace("_", " ")
        result[area] = int(r.get(key))
    return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))


# ──────────────────────────────────────────────────────────────
# QUERY 3 — All average response times (sorted fastest first)
# ──────────────────────────────────────────────────────────────

def query_all_avg_response_times():
    """
    Return average response times for all areas, sorted fastest first.
    Example output: {'West Side': 98.5, 'Downtown': 112.3, ...}
    """
    result = {}
    for key in r.scan_iter("avg_response_time:*"):
        area = key.split(":", 1)[1].replace("_", " ")
        result[area] = float(r.get(key))
    return dict(sorted(result.items(), key=lambda x: x[1]))


# ──────────────────────────────────────────────────────────────
# QUERY 4 — Dashboard summary (combines multiple reads)
# ──────────────────────────────────────────────────────────────

def query_redis_dashboard():
    """
    Return a full summary of Redis data for the dashboard.
    Reads counters live; uses cached blobs where available.
    """
    return {
        "active_sessions":    count_active_sessions(),
        "issue_counters":     query_all_issue_counters(),
        "area_counters":      query_all_area_counters(),
        "avg_response_times": query_all_avg_response_times(),
        "busiest_areas":      get_busiest_areas(),   # from cache (or None)
        "top_issue_types":    get_top_issue_types(),  # from cache (or None)
    }


# ──────────────────────────────────────────────────────────────
# QUERY 5 — Single area stats
# ──────────────────────────────────────────────────────────────

def query_area_stats(area):
    """
    Return all Redis data for one specific area.
    Useful when a department views their own area dashboard.
    """
    from cache_operations import get_area_counter
    return {
        "area":             area,
        "total_reports":    get_area_counter(area),
        "avg_response_min": get_avg_response_time(area),
    }


# ──────────────────────────────────────────────────────────────
# Quick test — run this file directly to verify queries work
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Issue Counters ===")
    print(query_all_issue_counters())

    print("\n=== Area Counters ===")
    print(query_all_area_counters())

    print("\n=== Avg Response Times ===")
    print(query_all_avg_response_times())

    print("\n=== Dashboard Summary ===")
    summary = query_redis_dashboard()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n=== Downtown Stats ===")
    print(query_area_stats("Downtown"))