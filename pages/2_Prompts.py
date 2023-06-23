import json
import re
from typing import Any, List
import streamlit as st
from annotated_text import annotated_text

from prompton import errors as prompton_errors
from prompton import types as prompton_types

import utils.prompton_helpers as prompton_helpers
import components.login as login
import components.layout as layout
import components.prompt_selector as prompt_selector


layout.show_layout()

if login.login():
    prompton = prompton_helpers.get_prompton()

    prompt, prompt_version = prompt_selector.select_prompt_version()

    if prompt_version:
        with st.form("Update prompt version"):
            is_not_draft = prompt_version.status != "Draft"

            template_formatted = (
                json.dumps([i.dict() for i in prompt_version.template], indent=4)
                if prompt_version.template
                else ""
            )

            description_formatted = (
                prompt_version.description if prompt_version.description else ""
            )

            # \\n in json strings to \ followed by a literal new line
            template_formatted = re.sub(r"\\n", "\\\n", template_formatted)

            model_config_formatted = (
                json.dumps(prompt_version.model_config.dict(), indent=4)
                if prompt_version.model_config
                else ""
            )

            pv_status_names = [
                status.value for status in prompton_types.PromptVersionStatus
            ]

            st.write("## Update prompt version")

            st.markdown(f"Id: `{prompt_version.id}`")
            new_pv_name = st.text_input("Name", value=prompt_version.name)

            new_pv_description = st.text_area(
                "Description", value=description_formatted
            )

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
                placeholder='E.g.: [\n {"role": "system", "content": "string" },\n {"role": "user", "content": "" }\n]',
            )

            annotated_text(
                "Template args: ",
                *[
                    [(a, "", "#3d0f42", "#fff"), " "]
                    for a in prompt_version.template_arg_names
                ],
            )

            new_pv_model_config = st.text_area(
                "Model config",
                value=model_config_formatted,
                placeholder='E.g.:\n { "model": "gpt-4", "temperature": 0.6, "max_tokens": 2000 }',
                height=100,
                disabled=is_not_draft,
            )

            submitted = st.form_submit_button("Update")

            if submitted:
                # TODO: PromptVersionUpdate schema should be exposed via SDK
                update_params: dict[str, Any] = {}

                if new_pv_name != prompt_version.name:
                    update_params["name"] = new_pv_name

                if new_pv_template != template_formatted:
                    # \ followed by literal new line to -> \\n for json parsing (for new lines in string values)
                    template_json_parsed = re.sub(r"\\\n", "\\\\n", new_pv_template)

                    new_pv_template_obj: List[prompton_types.ChatGptMessage] = [
                        prompton_types.ChatGptMessage(**i)
                        for i in json.loads(template_json_parsed)
                    ]

                    update_params["template"] = new_pv_template_obj

                if new_pv_model_config != model_config_formatted:
                    new_pv_model_config_obj = (
                        prompton_types.ChatGptChatCompletitionConfig(
                            **json.loads(new_pv_model_config)
                        )
                    )
                    update_params["model_config"] = new_pv_model_config_obj

                if new_pv_status and new_pv_status != prompt_version.status:
                    update_params["status"] = new_pv_status

                if new_pv_description != description_formatted:
                    update_params["description"] = new_pv_description

                if update_params == {}:
                    st.warning("Nothing to update")
                else:
                    print("updating pversion :", prompt_version.id, update_params)

                    try:
                        with st.spinner("Updating prompt version..."):
                            updated_pv = prompton.prompt_versions.update_prompt_version(
                                prompt_version.id, **update_params
                            )
                        update_params = {}
                        # FIXME: there is an error when you update second time
                        st.success("Prompt version updated!")

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

    if prompt:
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

                    prompton_helpers.get_prompt_versions.clear()  # type: ignore
                    st.success(
                        "Prompt version created. Click refresh below to update versions dropdown (sorry)"
                    )

                    st.write(new_pv)

                except prompton_errors.UnauthorizedError as e:
                    st.error("😕 Login failed: " + str(e.body["detail"]))
                except prompton_errors.BadRequestError as e:
                    st.error("😕 Bad request: " + str(e.body))
                except prompton_errors.UnprocessableEntityError as e:
                    st.error("😕 Unprocessable entity: " + str(e.body))

                except Exception as e:
                    st.error("😕 Error while trying to create prompt version: " + str(e))

        refresh_button = st.button("Refresh")

        if refresh_button:
            prompt_selector.refresh_prompt_versions()
