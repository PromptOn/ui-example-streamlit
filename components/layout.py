import streamlit as st

from .sidebar import show_sidebar


def show_layout(page_title: str | None = None):
    _page_title = "PromptOn"
    if page_title:
        _page_title = _page_title + " - " + page_title

    st.set_page_config(layout="wide", page_title=_page_title, page_icon=":lemon:")

    style = open("./styles.css").read()
    st.markdown(f"""<style>{style}</style>""", unsafe_allow_html=True)

    show_sidebar()
