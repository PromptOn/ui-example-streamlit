from typing import List, Tuple
import streamlit as st
from datetime import datetime
from tzlocal import get_localzone

from prompton import client as prompton_client
from prompton import types as prompton_types


def get_prompton():
    prompton_api = prompton_client.PromptonApi(
        environment=st.session_state["prompton_env"],
        token=st.session_state["auth_token"],
    )
    return prompton_api


@st.cache_data(ttl="1d")
def get_prompt_version_list(prompt_id: str):
    prompton = get_prompton()
    return prompton.prompt_versions.get_prompt_versions_list(prompt_id=prompt_id)


@st.cache_data(ttl="1d")
def get_prompt_version_by_id(prompt_version_id: str):
    prompton = get_prompton()
    return prompton.prompt_versions.get_prompt_version_by_id(id=prompt_version_id)


@st.cache_data(ttl="1d")
def get_prompt_by_id(prompt_id: str):
    prompton = get_prompton()
    return prompton.prompts.get_prompt_by_id(id=prompt_id)


@st.cache_data(ttl="1d")
def get_prompts():
    prompton = get_prompton()
    return prompton.prompts.get_prompts_list()


@st.cache_data(ttl="1hr")
def get_inferences(prompt_version_id: str):
    prompton = get_prompton()
    return prompton.inferences.get_inferences_list(prompt_version_id=prompt_version_id)


@st.cache_data(ttl="1d")
def get_my_feedbacks(prompt_version_id: str):
    prompton = get_prompton()

    my_feedbacks = prompton.feedbacks.get_feedbacks_list(
        prompt_version_id=prompt_version_id,
        prompton_user_id=st.session_state["current_user"].id,
    )

    return my_feedbacks


def get_inferences_to_evaluate(prompt_version_id: str):
    """Returns a list of inferences that the user has not yet evaluated the overall feedback
    (ie. feedback.feedback_for_part = None))"""
    _inferences_to_eval = get_inference_parts_to_evaluate(prompt_version_id, [None])
    inferences_to_eval = [item[2] for item in _inferences_to_eval]
    return inferences_to_eval


@st.cache_data(ttl="1hr")
def get_inference_parts_to_evaluate(
    prompt_version_id: str, parts_to_evaluate: List[str | None]
):
    """Returns a list of tuples (inference response, parts, full inference) that the user has not yet evaluated.
    If no parts_to_evaluate is provided then only overall feedbacks considered (i.e. feedback.feedback_for_part = None))
    """
    inferences = get_inferences(prompt_version_id=prompt_version_id)

    my_feedbacks = get_my_feedbacks(prompt_version_id=prompt_version_id)

    inferences_to_eval: List[
        Tuple[
            prompton_types.InferenceResponseData,
            List[str | None],
            prompton_types.InferenceRead,
        ]
    ] = []

    for _, inf in enumerate(inferences):
        if (
            inf.status == prompton_types.InferenceResponseStatus.PROCESSED
            and isinstance(inf.response, prompton_types.InferenceResponseData)
        ):
            parts_not_evaluated = parts_to_evaluate.copy()

            for _, fb in enumerate(my_feedbacks):
                if (
                    inf.id == fb.inference_id
                    and fb.feedback_for_part in parts_to_evaluate
                ):
                    try:
                        parts_not_evaluated.remove(fb.feedback_for_part)
                    except ValueError:
                        pass

            if len(parts_not_evaluated) > 0:
                inferences_to_eval.append((inf.response, parts_not_evaluated, inf))

    return inferences_to_eval


def format_datetime(dt_str: str) -> str:
    """Formats an iso datetime string to a human readable format in clients local TimeZone."""
    dt = datetime.fromisoformat(dt_str).astimezone(get_localzone())
    _dt_str = dt.strftime("%d-%b-%y %H:%M:%S")
    return _dt_str
