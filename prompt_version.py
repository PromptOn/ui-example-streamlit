import json
import re
from typing import List
import streamlit as st

from prompton import client as prompton_client
from prompton import errors as prompton_errors
from prompton import types as prompton_types


import auth
import header

if auth.login():
    header.show_header()

    prompton = auth.get_prompton()

    with st.spinner("Loading prompts..."):
        my_prompts = prompton.prompts.get_prompts_list()

        selected_prompt = st.selectbox(
            "Select prompt", my_prompts, format_func=lambda o: o.name
        )

    if selected_prompt and selected_prompt.id:
        with st.spinner("Loading versions..."):
            my_prompt_versions = prompton.prompt_versions.get_prompt_versions_list(
                prompt_id=selected_prompt.id
            )
            selected_pv = st.selectbox(
                "Select prompt version",
                my_prompt_versions,
                format_func=lambda o: o.name + " (" + o.status + ")",
            )

            if selected_pv and selected_pv.id and selected_pv.status:
                with st.form("Update prompt version"):
                    is_not_draft = selected_pv.status != "Draft"
                    template_default = '[\n {"role": "system", "content": "string" },\n {"role": "user", "content": "" }\n]'
                    model_config_default = (
                        '{ "model": "gpt-4", "temperature": 0.6, "max_tokens": 2000 }'
                    )

                    template_formatted = (
                        json.dumps([i.dict() for i in selected_pv.template], indent=4)
                        if selected_pv.template
                        else template_default
                    )

                    # \\n in json strings to \ followed by a literal new line
                    template_formatted = re.sub(r"\\n", "\\\n", template_formatted)

                    model_config_formatted = (
                        json.dumps(selected_pv.model_config.dict(), indent=4)
                        if selected_pv.model_config
                        else model_config_default
                    )

                    pv_status_names = [
                        status.value for status in prompton_types.PromptVersionStatus
                    ]

                    st.write("## Update prompt version")
                    new_pv_name = st.text_input("Name", value=selected_pv.name)

                    new_pv_status = st.selectbox(
                        # options=["Draft", "Testing", "Live", "Archived"],
                        options=pv_status_names,
                        label="Status",
                        index=pv_status_names.index(selected_pv.status),
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
                            (" , ").join(selected_pv.template_arg_names)
                            if selected_pv.template_arg_names
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
                        new_pv_model_config_obj = (
                            prompton_types.ChatGptChatCompletitionConfig(
                                **json.loads(new_pv_model_config)
                            )
                        )

                        # \ followed by literal new line to -> \\n for json parsing (for new lines in string values)
                        json_parsed = re.sub(r"\\\n", "\\\\n", new_pv_template)

                        new_pv_template_obj: List[prompton_types.ChatGptMessage] = [
                            prompton_types.ChatGptMessage(**i)
                            for i in json.loads(json_parsed)
                        ]

                        update_params = {}
                        if new_pv_name != selected_pv.name:
                            update_params["name"] = new_pv_name

                        if new_pv_template != template_formatted:
                            update_params["template"] = new_pv_template_obj  # type: ignore

                        if new_pv_model_config != model_config_formatted:
                            update_params["model_config"] = new_pv_model_config_obj

                        if new_pv_status and new_pv_status != selected_pv.status:
                            update_params["status"] = new_pv_status

                        if update_params == {}:
                            st.warning("Nothing to update")
                        else:
                            print("updating pversion :", selected_pv.id, update_params)

                            try:
                                with st.spinner("Updating prompt version..."):
                                    updated_pv = (
                                        prompton.prompt_versions.update_prompt_version(
                                            selected_pv.id, **update_params
                                        )
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
                                    "😕 Error while trying to update prompt version: "
                                    + str(e)
                                )

        if selected_prompt and selected_prompt.id:
            st.write("## Create new prompt version")

            with st.form("Create new prompt version"):
                st.write(f"Prompt:  {selected_prompt.name} - {selected_prompt.id}")
                _ = st.text_input("Provider", value="OpenAI", disabled=True)
                _ = st.text_input("Status", value="Draft", disabled=True)
                new_pv_name = st.text_input("New prompt version name")
                submitted = st.form_submit_button("Create")

                if submitted:
                    try:
                        with st.spinner("Creating new prompt version..."):
                            new_pv = prompton.prompt_versions.add_prompt_version(
                                prompt_id=selected_prompt.id, name=new_pv_name
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
