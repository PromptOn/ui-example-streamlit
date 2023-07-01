import streamlit as st


def step_idx(key, step: int):
    def _step_idx():
        st.session_state[key] += step

    return _step_idx


def show_paginator(data_length: int, key: str) -> int:
    col1, col2, col3, col4 = st.columns([1, 2, 1, 8])

    if key not in st.session_state:
        st.session_state[key] = 1

    current_idx = col2.selectbox(
        label="Inference",
        label_visibility="collapsed",
        options=list(range(1, data_length + 1)),
        key=key,
    )

    col3.write(f"/{data_length}")

    if not current_idx:
        current_idx = 1

    if current_idx > 1:
        col1.button("<", on_click=step_idx(key, -1))

    if current_idx < data_length:
        col4.button("\\>", on_click=step_idx(key, 1))

    return current_idx - 1
