import json
import streamlit as st

from prompton import types as prompton_types

import utils.prompton_helpers as prompton_helpers
import components.login as login
import components.layout as layout
import components.pagination as pagination
import components.inference_details as inference_details
import components.prompt_selector as prompt_selector

layout.show_layout("Inferences")

if login.login():
    prompton = prompton_helpers.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version:
        inferences = prompton_helpers.get_inferences(prompt_version.id)

        current_idx = pagination.show_paginator(len(inferences))

        inf = inferences[current_idx]

        st.markdown("#### Input")
        st.write(inf.template_args)

        st.markdown("#### Response")

        if not inf.response:
            st.write(
                f"No response from {inf.request.provider} yet. Status: {inf.status.value}  id: {inf.id}"
            )

        else:
            if isinstance(inf.response, prompton_types.InferenceResponseData):
                resp = inf.response.raw_response.choices[0].message.content
                try:
                    json_response = json.loads(resp)
                    if type(json_response) == dict:
                        st.json(json_response, expanded=True)
                    else:
                        raise json.JSONDecodeError(
                            "response is Not a dict", "message.content", 0
                        )

                except json.JSONDecodeError as e:  # json.JSONDecodeError:
                    st.write(resp)

            elif isinstance(inf.response, prompton_types.InferenceResponseError):
                st.write("#### Response Error:")
                st.write(inf.status)
            else:
                st.write(f"Unknown response type for inference {inf.id}")

            with st.expander(f" Details "):
                inference_details.show_details(inf)

        st.divider()

        refresh_button = st.button("Refresh")

        if refresh_button:
            prompton_helpers.get_inferences.clear()  # type: ignore
            st.experimental_rerun()
