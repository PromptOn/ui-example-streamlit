from typing import Tuple
import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox as no_default_selectbox

from prompton import types as prompton_types
import auth


def select_prompt_version() -> (
    Tuple[prompton_types.PromptRead | None, prompton_types.PromptVersionRead | None]
):
    prompton = auth.get_prompton()

    col_prompt, col_prompt_version, _ = st.columns([1, 2, 1])
    with st.spinner("Loading prompts..."):
        my_prompts = prompton.prompts.get_prompts_list()

        with col_prompt:
            selected_prompt = no_default_selectbox(
                "Prompt",
                my_prompts,
                format_func=lambda o: o if type(o) == str else o.name,
                no_selection_label="<Select a prompt>",
            )

        def format_prompt_version_fn(o: prompton_types.PromptVersionRead):
            if type(o) == str:
                return o

            pv_string = f"{o.name} - {o.status.value if o.status else ''} "
            if o.model_config:
                pv_string += (
                    f" - {o.model_config.model} - temp: {o.model_config.temperature}"
                )
            return pv_string

        if selected_prompt and selected_prompt.id:
            with st.spinner("Loading versions..."):
                my_prompt_versions = prompton.prompt_versions.get_prompt_versions_list(
                    prompt_id=selected_prompt.id
                )
                with col_prompt_version:
                    selected_pv = no_default_selectbox(
                        "version",
                        my_prompt_versions,
                        format_func=format_prompt_version_fn,
                        no_selection_label="<Select a version>",
                    )

                if selected_pv and selected_pv.id and selected_pv.description:
                    col_prompt_version.markdown(f"_{selected_pv.description}_")

                return selected_prompt, selected_pv

    return None, None
