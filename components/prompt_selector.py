from typing import Tuple
import streamlit as st
from streamlit_extras.no_default_selectbox import selectbox as no_default_selectbox

from prompton import types as prompton_types
from utils.prompton_helpers import get_prompt_versions
from utils.prompton_helpers import get_prompts


def refresh_prompt_versions():
    get_prompt_versions.clear()
    st.session_state["prompt_versions"] = get_prompt_versions(
        st.session_state["selected_prompt"].id
    )
    st.experimental_rerun()


def format_prompt_version_fn(o: prompton_types.PromptVersionRead):
    if type(o) == str:
        return o

    pv_string = f"{o.name} - {o.status.value if o.status else ''} "
    if o.model_config:
        pv_string += f" - {o.model_config.model} - temp: {o.model_config.temperature}"
    return pv_string


def select_prompt_version() -> (
    Tuple[prompton_types.PromptRead | None, prompton_types.PromptVersionRead | None]
):
    if "selected_prompt_version" not in st.session_state:
        st.session_state["selected_prompt_version"] = None

    if "selected_prompt" not in st.session_state:
        st.session_state["selected_prompt"] = None

    col_prompt, col_prompt_version, _ = st.columns([1, 2, 1])
    with st.spinner("Loading prompts..."):
        my_prompts = get_prompts()

        with col_prompt:
            selected_prompt_idx = 0

            if st.session_state["selected_prompt"]:
                for idx, prompt in enumerate(my_prompts):
                    if prompt.id == st.session_state["selected_prompt"].id:
                        selected_prompt_idx = idx + 1  # idx 0 is for no selection
                        break

            st.session_state["selected_prompt"] = no_default_selectbox(
                "Prompt",
                my_prompts,
                format_func=lambda o: o if type(o) == str else o.name,
                no_selection_label="<Select a prompt>",
                index=selected_prompt_idx,
            )

        if st.session_state["selected_prompt"]:
            with st.spinner("Loading versions..."):
                my_prompt_versions = get_prompt_versions(
                    st.session_state["selected_prompt"].id
                )

                with col_prompt_version:
                    selected_pv_idx = 0

                    if st.session_state["selected_prompt_version"]:
                        for idx, prompt_version in enumerate(my_prompt_versions):
                            if (
                                prompt_version.id
                                == st.session_state["selected_prompt_version"].id
                            ):
                                selected_pv_idx = idx + 1  # idx 0 is for no selection
                                break

                    st.session_state["selected_prompt_version"] = no_default_selectbox(
                        "version",
                        my_prompt_versions,
                        format_func=format_prompt_version_fn,
                        no_selection_label="<Select a version>",
                        index=selected_pv_idx,
                    )

                if (
                    st.session_state["selected_prompt_version"]
                    and st.session_state["selected_prompt_version"].description
                ):
                    col_prompt_version.caption(
                        f'{st.session_state["selected_prompt_version"].description}'
                    )

                return (
                    st.session_state["selected_prompt"],
                    st.session_state["selected_prompt_version"],
                )

    return None, None
