import streamlit as st

import auth
import header
import prompt_selector


if auth.login():
    header.show_header()

    prompton = auth.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version and prompt_version.id:
        inferences = prompton.inferences.get_inferences_list(
            prompt_version_id=prompt_version.id
        )
        st.write("## Inferences")
        st.write(inferences)
