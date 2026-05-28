"""
Smart City Project — Redis Cache Operations
Handles: sessions, counters, avg response time, cached aggregations
"""

import json
from connect import r


# ──────────────────────────────────────────────────────────────
# SESSIONS
# ──────────────────────────────────────────────────────────────

def create_session(user_id, ttl=3600):
    """Create an active session. TTL in seconds (default 1 hour)."""
    r.setex(f"session:{user_id}", ttl, "active")
    print(f"Session created for {user_id} (TTL: {ttl}s)")


def get_session(user_id):
    """Return session status or None if expired."""
    return r.get(f"session:{user_id}")


def delete_session(user_id):
    """Delete a session (logout)."""
    deleted = r.delete(f"session:{user_id}")
    if deleted:
        print(f"Session deleted for {user_id}")
    else:
        print(f"No session found for {user_id}")


def get_session_ttl(user_id):
    """Seconds remaining on a session. -2 = not found."""
    return r.ttl(f"session:{user_id}")


def count_active_sessions():
    """Count all active session keys."""
    return len(list(r.scan_iter("session:*")))


# ──────────────────────────────────────────────────────────────
# ISSUE COUNTERS
# ──────────────────────────────────────────────────────────────

def increment_issue_counter(issue_type):
    """Increment counter for an issue type. Returns new value."""
    return int(r.incr(f"issue_counter:{issue_type}"))


def get_issue_counter(issue_type):
    """Get current count for one issue type."""
    val = r.get(f"issue_counter:{issue_type}")
    return int(val) if val else 0


def set_issue_counter(issue_type, count):
    """Set a counter directly (used during data load)."""
    r.set(f"issue_counter:{issue_type}", count)


# ──────────────────────────────────────────────────────────────
# AREA COUNTERS
# ──────────────────────────────────────────────────────────────

def increment_area_counter(area):
    """Increment report counter for an area. Returns new value."""
    key = area.replace(" ", "_")
    return int(r.incr(f"area_counter:{key}"))


def get_area_counter(area):
    """Get current report count for one area."""
    key = area.replace(" ", "_")
    val = r.get(f"area_counter:{key}")
    return int(val) if val else 0


def set_area_counter(area, count):
    """Set an area counter directly (used during data load)."""
    key = area.replace(" ", "_")
    r.set(f"area_counter:{key}", count)


# ──────────────────────────────────────────────────────────────
# AVERAGE RESPONSE TIME
# ──────────────────────────────────────────────────────────────

def set_avg_response_time(area, minutes):
    """Store average response time (minutes) for an area."""
    key = area.replace(" ", "_")
    r.set(f"avg_response_time:{key}", round(minutes, 2))


def get_avg_response_time(area):
    """Get cached average response time for an area."""
    key = area.replace(" ", "_")
    val = r.get(f"avg_response_time:{key}")
    return float(val) if val else None


def update_avg_response_time(area, new_response_time):
    """
    Recalculate and update the cached average when a report is resolved.
    Uses a simple running average.
    """
    current = get_avg_response_time(area) or new_response_time
    new_avg = round((current + new_response_time) / 2, 2)
    set_avg_response_time(area, new_avg)
    return new_avg


# ──────────────────────────────────────────────────────────────
# CACHED AGGREGATIONS  (JSON with TTL)
# ──────────────────────────────────────────────────────────────

def set_busiest_areas(areas_list, ttl=3600):
    """Cache top busiest areas as JSON. areas_list = [{'area':..,'count':..}]"""
    r.set("cached:busiest_areas", json.dumps(areas_list))
    r.expire("cached:busiest_areas", ttl)


def get_busiest_areas():
    """Return cached busiest areas or None if expired."""
    raw = r.get("cached:busiest_areas")
    return json.loads(raw) if raw else None


def set_top_issue_types(types_list, ttl=3600):
    """Cache top issue types as JSON. types_list = [{'type':..,'count':..}]"""
    r.set("cached:top_issue_types", json.dumps(types_list))
    r.expire("cached:top_issue_types", ttl)


def get_top_issue_types():
    """Return cached top issue types or None if expired."""
    raw = r.get("cached:top_issue_types")
    return json.loads(raw) if raw else None


def invalidate_caches():
    """Delete aggregation caches so they get recomputed on next read."""
    r.delete("cached:busiest_areas")
    r.delete("cached:top_issue_types")


# ──────────────────────────────────────────────────────────────
# DEPARTMENT LOOKUP  (Hash)
# ──────────────────────────────────────────────────────────────

def set_department_name(dep_id, name):
    """Add one entry to the department lookup hash."""
    r.hset("dept_lookup", dep_id, name)


def get_department_name(dep_id):
    """Fast O(1) lookup: dep_id → department name."""
    return r.hget("dept_lookup", dep_id)


# ──────────────────────────────────────────────────────────────
# INTEGRATION HOOKS  (called by the Streamlit app)
# ──────────────────────────────────────────────────────────────

def on_new_report(issue_type, area):
    """
    Call this every time a report is submitted.
    Increments counters and invalidates stale caches.
    """
    new_issue_count = increment_issue_counter(issue_type)
    new_area_count  = increment_area_counter(area)
    invalidate_caches()

    return {
        "issue_type":      issue_type,
        "new_issue_count": new_issue_count,
        "area":            area,
        "new_area_count":  new_area_count,
    }


def on_report_resolved(area, response_time_minutes):
    """
    Call this when a report is marked as resolved.
    Updates the cached average response time for that area.
    """
    return update_avg_response_time(area, response_time_minutes)
