import streamlit as st

import auth, layout, inferences, prompts


if auth.login():
    layout.show()

    if st.session_state["nav_selection"] == "Inferences":
        inferences.show()
    elif st.session_state["nav_selection"] == "Prompts":
        prompts.show()
