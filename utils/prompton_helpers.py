import streamlit as st
from prompton import client as prompton_client

import utils.prompton_helpers as login


def get_prompton():
    prompton_api = prompton_client.PromptonApi(
        environment=st.session_state["prompton_env"],
        token=st.session_state["auth_token"],
    )
    return prompton_api


@st.cache_data(ttl="1hr")
def get_prompt_versions(prompt_id: str):
    prompton = login.get_prompton()
    return prompton.prompt_versions.get_prompt_versions_list(prompt_id=prompt_id)


@st.cache_data(ttl="1hr")
def get_prompts():
    prompton = login.get_prompton()
    return prompton.prompts.get_prompts_list()


@st.cache_data(ttl="1hr")
def get_inferences(prompt_version_id: str):
    prompton = get_prompton()
    return prompton.inferences.get_inferences_list(prompt_version_id=prompt_version_id)
