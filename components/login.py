import streamlit as st
from prompton import errors as prompton_errors
from prompton import client as prompton_client

from utils.prompton_helpers import get_prompton

PROMPTON_ENVS = [
    "https://staging.api.prompton.ai",
    "http://127.0.0.1:8000",
    "https://api.prompton.ai",
]


def login():
    if "auth_token" not in st.session_state:
        st.session_state["auth_token"] = None

    if "nav_selection" not in st.session_state:
        st.session_state["nav_selection"] = None

    if "prompton_env" not in st.session_state:
        st.session_state["prompton_env"] = None

    if "current_user" not in st.session_state:
        st.session_state["current_user"] = None

    if "current_org" not in st.session_state:
        st.session_state["current_org"] = None

    if st.session_state["auth_token"]:
        return True
    else:
        with st.form("Login"):
            st.write("### Login ")
            prompton_env = st.selectbox("Environment", PROMPTON_ENVS)

            st.session_state["prompton_env"] = prompton_env

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

                        st.session_state["auth_token"] = token.access_token

                        prompton = get_prompton()

                        st.session_state[
                            "current_user"
                        ] = prompton.users.get_current_user()

                        st.session_state[
                            "current_org"
                        ] = prompton.orgs.get_current_user_org()

                    st.experimental_rerun()

                except prompton_errors.UnauthorizedError as e:
                    st.error("😕 Login failed: " + str(e.body["detail"]))
                except prompton_errors.BadRequestError as e:
                    st.error("😕 Bad request: " + str(e.body))
                except prompton_errors.UnprocessableEntityError as e:
                    st.error("😕 Unprocessable entity: " + str(e.body))

                except Exception as e:
                    st.error("😕 Error while trying to login: " + str(e))
