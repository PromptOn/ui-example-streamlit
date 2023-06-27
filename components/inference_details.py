from typing import Dict, List


import streamlit as st
import pandas as pd

from prompton import types as prompton_types
from utils.prompton_helpers import format_datetime


def show_details(inf: prompton_types.InferenceRead):
    created_at_str = format_datetime(inf.created_at)

    compl_duration = (
        round(inf.response.completition_duration_seconds, 2)
        if inf.response and inf.response.completition_duration_seconds
        else "?"
    )

    total_tokens = (
        inf.response.raw_response.usage.total_tokens
        if isinstance(inf.response, prompton_types.InferenceResponseData)
        else "N/A"
    )

    st.write(
        f"`{inf.status.value}` in `{compl_duration}` secs | total tokens: `{total_tokens}` | `{created_at_str}` | prompt version: `{inf.prompt_version_id}`"
    )

    st.json(inf.dict(), expanded=False)


def show_args(template_args: Dict[str, str], highlight_args: List[str] = []):
    _template_args = template_args.copy()

    # for key, val in _template_args.items():
    #     _template_args[key] = val.replace("\n", "<br>")

    if len(highlight_args) == 0:
        args_high = _template_args
        args_detail = {}
    else:
        args_high = {k: v for k, v in _template_args.items() if k in highlight_args}
        args_detail = {
            k: v for k, v in _template_args.items() if k not in highlight_args
        }

    st.write(args_high)
    # for key, val in args_high.items():
    # st.markdown(f"**{key}**<br>{val}", unsafe_allow_html=True)

    if len(args_detail) > 0:
        with st.expander("Additional input: " + ", ".join(args_detail.keys())):
            st.write(args_detail)
            # for key, val in args_detail.items():
            #     st.markdown(f"**{key}**<br>{val}", unsafe_allow_html=True)


def show_model_response(response: str):
    st.markdown(
        """<div class="model-response">""" + response + "</div>",
        unsafe_allow_html=True,
    )
