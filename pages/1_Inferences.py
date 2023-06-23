import json
import pytz
import streamlit as st
from datetime import datetime
import pandas as pd

from prompton import types as prompton_types

import utils.prompton_helpers as prompton_helpers
import components.login as login
import components.layout as layout
import components.prompt_selector as prompt_selector

layout.show_layout("Inferences")

if login.login():
    prompton = prompton_helpers.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version:
        inferences = prompton_helpers.get_inferences(prompt_version.id)
        st.write(f"## Inferences ({len(inferences)})")

        refresh_button = st.button("Refresh")

        if refresh_button:
            prompton_helpers.get_inferences.clear()  # type: ignore
            st.experimental_rerun()

        for inf in inferences:
            df = pd.DataFrame([inf.template_args]).T
            style = df.style.hide(axis=1)

            st.write(style.to_html(header=False), unsafe_allow_html=True)

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
                            st.json(json_response, expanded=False)
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
                    created_at = datetime.fromisoformat(inf.created_at).astimezone(
                        pytz.timezone("Europe/London")
                    )
                    created_at_str = created_at.strftime("%d-%b-%y %H:%M:%S %z")

                    st.write(
                        f"{created_at_str} {inf.status.value  } in {round(inf.response.completition_duration_seconds,2) if inf.response.completition_duration_seconds else '?'}s"
                    )

                    st.json(inf.dict(), expanded=False)

            st.divider()
