import json
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers
from utils.prompton_helpers import load_user

from urllib.parse import urlencode


def show_google_login():
    prompton_env = st.session_state.get("prompton_env")

    if prompton_env is not None:
        query_params = st.experimental_get_query_params()

        access_token = None
        if "access_token" in query_params:
            access_token = query_params["access_token"][0]
            del query_params["access_token"]
            st.experimental_set_query_params(**query_params)

            load_user(access_token)

            st.experimental_rerun()

        else:
            headers = _get_websocket_headers()

            oauth_request_params = {}
            if headers and headers.get("Origin"):
                # oauth_request_params = f'?logged_in_redirect_uri={headers.get("Origin")}&prompton_env={prompton_env}'
                oauth_request_params = {
                    "logged_in_redirect_uri": headers.get("Origin"),
                    "prompton_env": prompton_env,
                }

            login_query_params = urlencode(
                {**query_params, **oauth_request_params},
                doseq=True,
            )

            st.markdown(
                f"""<a href="{prompton_env}/oauth/login?{login_query_params}" target="_self">
                <input type="button" value="Google Login" /></a>""",
                unsafe_allow_html=True,
            )
    else:
        st.write("Please select an environment")
