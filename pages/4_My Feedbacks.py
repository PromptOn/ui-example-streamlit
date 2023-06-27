import streamlit as st
import pandas as pd

import utils.prompton_helpers as prompton_helpers
import components.login as login
import components.layout as layout
import components.prompt_selector as prompt_selector

layout.show_layout("My Feedbacks")

if login.login():
    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version:
        my_feedbacks = prompton_helpers.get_my_feedbacks(prompt_version.id)

        if my_feedbacks is not None:
            st.write(f"## My feedbacks ({len(my_feedbacks)})")
            st.write(f"Prompt version: {prompt_version.name}  `{prompt_version.id}`")

            if len(my_feedbacks) == 0:
                st.info(f'No feedback from {st.session_state["current_user"].email}')
            else:
                df_feedbacks = pd.DataFrame([f.dict() for f in my_feedbacks])
                df_feedbacks["created_at"] = df_feedbacks["created_at"].apply(
                    prompton_helpers.format_datetime
                )
                st.write(
                    df_feedbacks[
                        [
                            "created_at",
                            "feedback_for_part",
                            "score",
                            "flag",
                            "note",
                            "metadata",
                            "_id",
                            "inference_id",
                        ]
                    ]
                )

        refresh_button = st.button("Refresh")
        if refresh_button:
            prompton_helpers.get_my_feedbacks.clear()  # type: ignore
            st.experimental_rerun()
