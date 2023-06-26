import streamlit as st
from streamlit_pagination import pagination_component

# this is https://mui.com/material-ui/react-pagination/ component
pagination_layout = {
    "color": "primary",
    "style": {"margin-top": "5px", "margin-bottom": "5px", "margin-left": "5px"},
}


def show_paginator(data_length: int, key: str | None = None):
    st.markdown(
        """
    <style>
        iframe {
            height: 50px;
            width: 500px;
        }     
    </style>
    """,
        unsafe_allow_html=True,
    )

    selected_idx: int = pagination_component(
        data_length + 1, layout=pagination_layout, key=key
    )

    return selected_idx
