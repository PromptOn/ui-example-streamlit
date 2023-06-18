import json
import re
from typing import List
import streamlit as st

from prompton import errors as prompton_errors
from prompton import types as prompton_types


import auth
import prompt_selector


def show():
    prompton = auth.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version and prompt_version.id and prompt_version.status:
        with st.form("Update prompt version"):
            is_not_draft = prompt_version.status != "Draft"
            template_default = '[\n {"role": "system", "content": "string" },\n {"role": "user", "content": "" }\n]'
            model_config_default = (
                '{ "model": "gpt-4", "temperature": 0.6, "max_tokens": 2000 }'
            )

            template_formatted = (
                json.dumps([i.dict() for i in prompt_version.template], indent=4)
                if prompt_version.template
                else template_default
            )

            # \\n in json strings to \ followed by a literal new line
            template_formatted = re.sub(r"\\n", "\\\n", template_formatted)

            model_config_formatted = (
                json.dumps(prompt_version.model_config.dict(), indent=4)
                if prompt_version.model_config
                else model_config_default
            )

            pv_status_names = [
                status.value for status in prompton_types.PromptVersionStatus
            ]

            st.write("## Update prompt version")
            new_pv_name = st.text_input("Name", value=prompt_version.name)

            new_pv_status = st.selectbox(
                # options=["Draft", "Testing", "Live", "Archived"],
                options=pv_status_names,
                label="Status",
                index=pv_status_names.index(prompt_version.status),
            )

            new_pv_template = st.text_area(
                "Template",
                value=template_formatted,
                height=150,
                disabled=is_not_draft,
            )

            st.write(
                "Template args: ",
                (
                    (" , ").join(prompt_version.template_arg_names)
                    if prompt_version.template_arg_names
                    else ""
                )
                + " (only updated after reload yet)",
            )

            new_pv_model_config = st.text_area(
                "Model config",
                value=model_config_formatted,
                height=100,
                disabled=is_not_draft,
            )

            submitted = st.form_submit_button("Update")

            if submitted:
                new_pv_model_config_obj = prompton_types.ChatGptChatCompletitionConfig(
                    **json.loads(new_pv_model_config)
                )

                # \ followed by literal new line to -> \\n for json parsing (for new lines in string values)
                json_parsed = re.sub(r"\\\n", "\\\\n", new_pv_template)

                new_pv_template_obj: List[prompton_types.ChatGptMessage] = [
                    prompton_types.ChatGptMessage(**i) for i in json.loads(json_parsed)
                ]

                update_params = {}
                if new_pv_name != prompt_version.name:
                    update_params["name"] = new_pv_name

                if new_pv_template != template_formatted:
                    update_params["template"] = new_pv_template_obj

                if new_pv_model_config != model_config_formatted:
                    update_params["model_config"] = new_pv_model_config_obj

                if new_pv_status and new_pv_status != prompt_version.status:
                    update_params["status"] = new_pv_status

                if update_params == {}:
                    st.warning("Nothing to update")
                else:
                    print("updating pversion :", prompt_version.id, update_params)

                    try:
                        with st.spinner("Updating prompt version..."):
                            updated_pv = prompton.prompt_versions.update_prompt_version(
                                prompt_version.id, **update_params
                            )

                        st.success("Prompt version updated!")
                        st.write(updated_pv)

                    except prompton_errors.UnauthorizedError as e:
                        st.error("😕 Login failed: " + str(e.body["detail"]))
                    except prompton_errors.BadRequestError as e:
                        st.error("😕 Bad request: " + str(e.body))
                    except prompton_errors.UnprocessableEntityError as e:
                        st.error("😕 Unprocessable entity: " + str(e.body))

                    except Exception as e:
                        st.error(
                            "😕 Error while trying to update prompt version: " + str(e)
                        )

        if prompt and prompt.id:
            st.write("## Create new prompt version")

            with st.form("Create new prompt version"):
                st.write(f"Prompt:  {prompt.name} - {prompt.id}")
                _ = st.text_input("Provider", value="OpenAI", disabled=True)
                _ = st.text_input("Status", value="Draft", disabled=True)
                new_pv_name = st.text_input("New prompt version name")
                submitted = st.form_submit_button("Create")

                if submitted:
                    try:
                        with st.spinner("Creating new prompt version..."):
                            new_pv = prompton.prompt_versions.add_prompt_version(
                                prompt_id=prompt.id, name=new_pv_name
                            )

                        st.success(
                            "Prompt version created. Refresh below to see (sorry)"
                        )
                        st.write(new_pv)

                    except prompton_errors.UnauthorizedError as e:
                        st.error("😕 Login failed: " + str(e.body["detail"]))
                    except prompton_errors.BadRequestError as e:
                        st.error("😕 Bad request: " + str(e.body))
                    except prompton_errors.UnprocessableEntityError as e:
                        st.error("😕 Unprocessable entity: " + str(e.body))

                    except Exception as e:
                        st.error(
                            "😕 Error while trying to create prompt version: " + str(e)
                        )

            refresh_button = st.button("Refresh")

            if refresh_button:
                st.experimental_rerun()
