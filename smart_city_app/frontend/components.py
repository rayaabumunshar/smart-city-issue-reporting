import pandas as pd
import streamlit as st


def normalize_for_display(rows):
    cleaned = []
    for row in rows or []:
        item = dict(row)
        for key, value in list(item.items()):
            if hasattr(value, "isoformat"):
                item[key] = value.isoformat(sep=" ", timespec="minutes")
            elif isinstance(value, list) and len(value) == 1:
                item[key] = value[0]
        cleaned.append(item)
    return cleaned


def show_message(result):
    if result.get("success"):
        st.success(result.get("message", "Done."))
    else:
        st.error(result.get("message", "Something went wrong."))


def dataframe(rows, empty_message="No records found."):
    rows = normalize_for_display(rows)
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info(empty_message)


def dict_table(data, key_name="name", value_name="value"):
    if not data:
        st.info("No data available.")
        return
    rows = [{key_name: key, value_name: value} for key, value in data.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True)

