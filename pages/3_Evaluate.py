from typing import List

import streamlit as st


import utils.prompton_helpers as prompton_helpers
import components.login as login
import components.layout as layout
import components.pagination as pagination
import components.prompt_selector as prompt_selector
import components.inference_details as inference_details
import components.evaluate_form as evaluate_form

layout.show_layout("Evaluate")

#
#  Query params
#
query_params = st.experimental_get_query_params()

# if your response is JSON evaluate specific parts of the response separately:
# /Evaluate?part=json_section1&part=json_section2
parts_to_eval: List[str | None] = [None]
_parts = query_params.get("part", None)
if _parts is not None:
    parts_to_eval = [p for p in _parts]

# if your prompt temaplte have a lot of input and you want to highlight specific arguments and show the rest in an expander:
# /Evaluate?highlight_arg=interview_question&highlight_arg=candidate_answer
highlight_args = query_params.get("highlight_arg", [])


if "current_page_idx" not in st.session_state:
    st.session_state["current_page_idx"] = 0

if login.login():
    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version:
        to_eval = prompton_helpers.get_inference_parts_to_evaluate(
            prompt_version.id, parts_to_eval
        )

        st.markdown("<div id='linkto_top'></div>", unsafe_allow_html=True)

        if to_eval is not None:
            if len(to_eval) == 0 or st.session_state.get("current_page_idx", 0) >= len(
                to_eval
            ):
                st.info(
                    f'No inferences without feedback from {st.session_state["current_user"].email}'
                )

            else:
                # st.session_state["current_page_idx"] = pagination.show_paginator(
                #     len(to_eval)
                # )

                inf_resp, parts, full_inf = to_eval[
                    st.session_state["current_page_idx"]
                ]

                # st.write(
                #     f'### Input {st.session_state["current_page_idx"] + 1} / {len(to_eval)}'
                # )
                #
                st.write(f"### Evaluate")

                inference_details.show_args(full_inf.template_args, highlight_args)

                _ = evaluate_form.show_form(full_inf.id, inf_resp, parts)

                st.markdown(
                    f" {len(to_eval)} more to finish\t<a href='#linkto_top'>Scroll to top</a>",
                    unsafe_allow_html=True,
                )

                st.divider()

                with st.expander(f"Details for inference `{full_inf.id}`"):
                    inference_details.show_details(full_inf)

            refresh_button = st.button("Refresh")
            if refresh_button:
                prompton_helpers.get_inference_parts_to_evaluate.clear()  # type: ignore
                prompton_helpers.get_my_feedbacks.clear()  # type: ignore
                st.experimental_rerun()
