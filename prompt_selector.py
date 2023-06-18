from typing import Tuple
import streamlit as st
from prompton import types as prompton_types

import auth


def select_prompt_version() -> (
    Tuple[prompton_types.PromptRead | None, prompton_types.PromptVersionRead | None]
):
    prompton = auth.get_prompton()

    col1, col2, _ = st.columns([1, 2, 1])
    with st.spinner("Loading prompts..."):
        my_prompts = prompton.prompts.get_prompts_list()

        selected_prompt = col1.selectbox(
            "Prompt", my_prompts, format_func=lambda o: o.name
        )

        if selected_prompt and selected_prompt.id:
            with st.spinner("Loading versions..."):
                my_prompt_versions = prompton.prompt_versions.get_prompt_versions_list(
                    prompt_id=selected_prompt.id
                )
                selected_pv = col2.selectbox(
                    "version",
                    my_prompt_versions,
                    format_func=lambda o: o.name + " (" + o.status + ")",
                )

                return selected_prompt, selected_pv

    return None, None
