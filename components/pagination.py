import streamlit as st

# this is https://mui.com/material-ui/react-pagination/ component
pagination_layout = {
    "color": "primary",
    "style": {"margin-top": "5px", "margin-bottom": "5px", "margin-left": "5px"},
}


def show_paginator(data_length: int, key: str | None = None) -> int:
    col1, col2 = st.columns([1, 8])

    current_idx = col1.selectbox(
        label="Inference",
        label_visibility="collapsed",
        options=list(range(1, data_length + 1)),
        key=key,
    )

    col2.write(f"/{data_length}")

    if current_idx is None:
        current_idx = 0

    return current_idx - 1
