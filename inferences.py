import json
import pytz
import streamlit as st
from datetime import datetime

import auth
import prompt_selector
from prompton import types as prompton_types


def show():
    prompton = auth.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version and prompt_version.id:
        inferences = prompton.inferences.get_inferences_list(
            prompt_version_id=prompt_version.id
        )
        st.write(f"## Inferences ({len(inferences)})")
        for inf in inferences:
            acol1, acol2 = st.columns([1, 5])
            scol1, scol2 = st.columns([1, 5])
            if inf.template_args:
                for arg, val in inf.template_args.items():
                    acol1.write(f"**{arg}:** ")
                    acol2.write(val)

            if inf.response:
                if (
                    isinstance(inf.response, prompton_types.InferenceResponseData)
                    and inf.request
                ):
                    scol1.write("Response:")
                    resp = inf.response.raw_response.choices[0].message.content
                    try:
                        json_response = json.loads(resp)
                        if type(json_response) == dict:
                            scol2.json(json_response, expanded=False)
                        else:
                            raise json.JSONDecodeError(
                                "response is Not a dict", "message.content", 0
                            )

                    except json.JSONDecodeError as e:  # json.JSONDecodeError:
                        scol2.write(resp)

                elif isinstance(inf.response, prompton_types.InferenceResponseError):
                    scol1.write("Response Error:")
                    scol2.write(inf.status)
                else:
                    scol1.write(f"Unknown response type for inference {inf.id}")

                with st.expander(f" Details "):
                    created_at = datetime.fromisoformat(
                        inf.created_at if inf.created_at else ""
                    ).astimezone(pytz.timezone("Europe/London"))
                    created_at_str = created_at.strftime("%d-%b-%y %H:%M:%S %z")

                    st.write(
                        f"{created_at_str} {inf.status.value if inf.status else '<unknown status>'} in {round(inf.response.completition_duration_seconds,2) if inf.response.completition_duration_seconds else '?'}s"
                    )

                    st.json(inf.dict(), expanded=False)

                st.divider()
