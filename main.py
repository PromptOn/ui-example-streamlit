import streamlit as st

import auth, header, inferences, prompts


if auth.login():
    header.show()

    if st.session_state["nav_selection"] == "Inferences":
        inferences.show()
    elif st.session_state["nav_selection"] == "Prompts":
        prompts.show()
