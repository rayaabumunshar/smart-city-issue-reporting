import sys
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from backend import services  # noqa: E402
from backend.connections import get_redis_client  # noqa: E402
from backend.db.redis_queries import create_user_session, delete_user_session  # noqa: E402
from frontend.admin_pages import render_admin_pages  # noqa: E402
from frontend.department_pages import render_department_pages  # noqa: E402
from frontend.user_pages import render_user_pages  # noqa: E402


st.set_page_config(page_title="Smart City Reports", layout="wide")


def load_reference_data():
    result = services.get_reference_data_service()
    if not result.get("success"):
        st.sidebar.warning(result.get("message"))
        return {"report_types": [], "areas": [], "statuses": [], "departments": [], "users": []}
    return result


def sidebar_login(reference_data):
    st.sidebar.title("Smart City Reports")
    role = st.sidebar.selectbox("Role", ["Admin", "User", "Department"])
    st.session_state["role"] = role

    if role == "User":
        user_ids = [user.get("user_id") for user in reference_data.get("users", [])]
        default_user = st.session_state.get("user_id") or (user_ids[0] if user_ids else "U001")
        user_id = st.sidebar.selectbox(
            "User ID",
            user_ids if user_ids else [default_user],
            index=(user_ids.index(default_user) if default_user in user_ids else 0),
        )
        st.session_state["user_id"] = user_id
        if st.sidebar.button("Start demo session"):
            try:
                create_user_session(get_redis_client(), user_id)
                st.sidebar.success("Session stored in Redis.")
            except Exception as exc:
                st.sidebar.warning(f"Redis unavailable: {exc}")
        if st.sidebar.button("End demo session"):
            try:
                delete_user_session(get_redis_client(), user_id)
                st.sidebar.success("Session removed.")
            except Exception as exc:
                st.sidebar.warning(f"Redis unavailable: {exc}")

    if role == "Department":
        dep_ids = [dep.get("dep_id") for dep in reference_data.get("departments", [])]
        default_dep = st.session_state.get("department_id") or (dep_ids[0] if dep_ids else "D001")
        department_id = st.sidebar.selectbox(
            "Department ID",
            dep_ids if dep_ids else [default_dep],
            index=(dep_ids.index(default_dep) if default_dep in dep_ids else 0),
        )
        st.session_state["department_id"] = department_id

    return role


def main():
    reference_data = load_reference_data()
    role = sidebar_login(reference_data)

    st.title("Smart City Problem Reporting System")
    if role == "Admin":
        render_admin_pages(reference_data)
    elif role == "User":
        render_user_pages(st.session_state["user_id"], reference_data)
    else:
        render_department_pages(st.session_state["department_id"])


if __name__ == "__main__":
    main()
