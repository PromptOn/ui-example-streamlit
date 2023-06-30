import httpx
import streamlit as st
from prompton import errors as prompton_errors
from prompton import client as prompton_client

from utils.prompton_helpers import load_user
from components.google_login import show_google_login


PROMPTON_ENVS = [
    "https://staging.api.prompton.ai",
    "http://localhost:8000",
    "https://api.prompton.ai",
]


def on_selectbox_prompton_env():
    st.session_state["prompton_env"] = st.session_state["selectbox_prompton_env"]


def login():
    query_params = st.experimental_get_query_params()

    if "prompton_env" in query_params and query_params["prompton_env"][0] is not None:
        st.session_state["prompton_env"] = query_params["prompton_env"][0]
        del query_params["prompton_env"]
        st.experimental_set_query_params(**query_params)

    if "auth_token" not in st.session_state:
        st.session_state["auth_token"] = None

    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = None

    if "prompton_env" not in st.session_state:
        st.session_state["prompton_env"] = PROMPTON_ENVS[0]

    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None

    if "current_org" not in st.session_state:
        st.session_state["current_org"] = None

    if st.session_state["auth_token"]:
        return True
    else:
        st.write("### Login ")

        prompton_env = st.selectbox(
            "Environment",
            PROMPTON_ENVS,
            index=PROMPTON_ENVS.index(st.session_state["prompton_env"]),
            key="selectbox_prompton_env",
            on_change=on_selectbox_prompton_env,
        )

        show_google_login()

        st.write("")
        st.write("or")

        with st.form("Login"):
            email = st.text_input("email", key="email")
            password = st.text_input("Password", type="password", key="password")

            submitted = st.form_submit_button("Login")

            if submitted and prompton_env:
                try:
                    prompton = prompton_client.PromptonApi(environment=prompton_env)

                    with st.spinner("Authenticating..."):
                        token = prompton.authentication.get_access_token(
                            username=email, password=password
                        )

                        load_user(token.access_token)

                    st.experimental_rerun()

                except prompton_errors.UnauthorizedError as e:
                    st.error("😕 Login failed: " + str(e.body["detail"]))
                except prompton_errors.BadRequestError as e:
                    st.error("😕 Bad request: " + str(e.body))
                except prompton_errors.UnprocessableEntityError as e:
                    st.error("😕 Unprocessable entity: " + str(e.body))

                except Exception as e:
                    st.error("😕 Error while trying to login: " + str(e))
