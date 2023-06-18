import streamlit as st

import auth
import header


if auth.login():
    header.show_header()

    prompton = auth.get_prompton()

    st.write("## My Prompts")
    with st.spinner("Loading prompts..."):
        my_prompts = prompton.prompts.get_prompts_list()
        st.write(my_prompts)

    st.write("## My Prompt Versions")
    with st.spinner("Loading versions..."):
        my_prompt_versions = prompton.prompt_versions.get_prompt_versions_list()
        st.write(my_prompt_versions)
