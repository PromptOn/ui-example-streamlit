import json
import random
import streamlit as st
from typing import OrderedDict, List, cast
from dataclasses import dataclass

import utils.prompton_helpers as prompton_helpers
from prompton import types as prompton_types
from prompton import errors as prompton_errors

from streamlit_antd_components import buttons
import dirtyjson

import components.inference_details as inference_details


@dataclass
class Eval:
    part_name: str | None
    score: int | None = None
    note: str = ""
    flag: str | None = None


EvalList = List[Eval]


SCORE_IDX_TO_SCORE_VAL: List[int | None] = [None, -2, -1, 1, 2]


def reset_form(parts: List[str | None]):
    for i, p in enumerate(parts):
        st.session_state["note_" + str(i)] = ""
        st.session_state["flag_" + str(i)] = None
        st.session_state["score_" + str(i)] = 0


def rating_component(part_idx: int):
    score = buttons(
        [
            dict(label="", icon="question-circle", type="link"),
            dict(label="Bad", icon="exclamation-triangle"),
            dict(label="So-so", icon="hand-thumbs-down"),
            dict(label="Good", icon="hand-thumbs-up"),
            dict(label="Excellent", icon="stars"),
        ],
        align="center",
        shape="round",
        grow=False,
        key="score_" + str(part_idx),
        return_index=True,
        compact=True,
    )
    st.session_state["score_" + str(part_idx)] = score

    return score


def show_form(
    inf_id: str, inf_resp: prompton_types.InferenceResponseData, parts: List[str | None]
):
    if (
        st.session_state.get("save_success_parts")
        and len(st.session_state["save_success_parts"]) > 0
    ):
        reset_form(st.session_state["save_success_parts"])

    with st.form(key="feedback_form"):
        raw_model_resp = inf_resp.raw_response.choices[0].message.content
        json_response = None
        try:
            json_response = json.loads(raw_model_resp)

        except json.JSONDecodeError as e:
            try:
                json_response = dict(dirtyjson.loads(raw_model_resp))
                st.warning(f"Note: Response is non standard JSON response. Repaired")

            except dirtyjson.Error:
                if len(parts) > 1 or (len(parts) == 1 and parts[0] is not None):
                    st.warning(
                        f"Response is not valid JSON can't extract `{parts}`, showing full response"
                    )

        for part_idx, part in enumerate(parts):
            if len(parts) > 1:
                st.write(f"#### `{part if part else 'Overall'}`")

            if json_response is None:
                inference_details.show_model_response(raw_model_resp)

            elif type(json_response) == dict and json_response.get(part):
                if type(json_response[part]) == str:
                    inference_details.show_model_response(
                        json_response[part]
                        .replace("\\n", "<br/>")
                        .replace("\n", "<br/>")
                    )
                else:
                    st.json(json_response[part], expanded=True)
            else:
                print("json_response", json_response)
                st.write(json_response)

            #
            #  Rating components
            #
            rcol1, rcol2 = st.columns([10, 9])
            with rcol1:
                _ = rating_component(part_idx)

            note = st.session_state.get("note_" + str(part_idx))
            _ = rcol2.text_area(
                "Note",
                label_visibility="collapsed",
                key="note_" + str(part_idx),
                placeholder=f"Optional comment about {part}...",
                height=80,
            )

        submitted = st.form_submit_button("Submit & Next", type="primary")

    if submitted:
        update_ct = 0
        error_ct = 0
        if "save_success_parts" not in st.session_state:
            st.session_state["save_success_parts"] = []

        for part_idx, part in enumerate(parts):
            score_idx = cast(int, st.session_state.get("score_" + str(part_idx)))

            score = SCORE_IDX_TO_SCORE_VAL[score_idx]

            note = st.session_state.get("note_" + str(part_idx))
            flag = st.session_state.get("flag_" + str(part_idx))

            if score or note or flag:
                try:
                    error_ct += 1

                    prompton = prompton_helpers.get_prompton()
                    prompton.feedbacks.add_feedback(
                        inference_id=inf_id,
                        feedback_for_part=part,
                        score=score,
                        note=note,
                        flag=flag,
                    )

                    st.session_state["save_success_parts"].append(part)
                    update_ct += 1
                    error_ct -= 1

                except prompton_errors.UnauthorizedError as e:
                    st.error("😕 Login failed: " + str(e.body["detail"]))
                except prompton_errors.BadRequestError as e:
                    st.error("😕 Bad request: " + str(e.body))
                except prompton_errors.UnprocessableEntityError as e:
                    st.error("😕 Unprocessable entity: " + str(e.body))

                except Exception as e:
                    st.error("😕 Error while trying to add feedback: " + str(e))

        if error_ct > 0:
            st.error(f"😕 Error(s) while adding {error_ct} feedbacks")
        elif update_ct == 0:
            st.warning("No feedback given, nothing to update")

        if update_ct > 0:
            prompton_helpers.get_inference_parts_to_evaluate.clear()  # type: ignore
            prompton_helpers.get_my_feedbacks.clear()  # type: ignore

            # this only stays if there was an  error with an other feedback.
            #    Otherwise success message from "save_success_parts" session state shown after rerun
            st.success(f"{update_ct} Feedbacks added successfully")

        if update_ct > 0 and error_ct == 0:
            st.experimental_rerun()

    if (
        st.session_state.get("save_success_parts")
        and len(st.session_state["save_success_parts"]) > 0
    ):
        st.success(
            f'Added feedback for {st.session_state["save_success_parts"]}\nNext one loaded'
        )

        st.session_state["save_success_parts"] = []

    return submitted
