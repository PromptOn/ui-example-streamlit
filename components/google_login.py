import json
import streamlit as st
from streamlit_javascript import st_javascript

from utils.prompton_helpers import load_user

from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


# NB: this where we reached the limits of Streamlit:
#      streamlit encapsulates page in an iframe in hosted env - too many hacks to get this working
#        and still need to open google sign in new window


def show_google_login():
    prompton_env = st.session_state.get("selectbox_prompton_env")

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
            current_url_str = st_javascript(
                "await fetch('').then(r => window.parent.location.href)"
            )
            current_url = urlparse(current_url_str)

            oauth_request_params = {
                # "logged_in_redirect_uri": headers.get("Origin"),
                "logged_in_redirect_uri": f"{current_url.scheme}://{current_url.netloc}{current_url.path}",
                "prompton_env": prompton_env,
            }

            login_query_params = urlencode(
                {**query_params, **oauth_request_params},
                doseq=True,
            )

            st.markdown(
                f"""<a href="{prompton_env}/oauth/login?{login_query_params}" target="_blank">
                <input type="button" value="Google Login" /></a>""",
                unsafe_allow_html=True,
            )
    else:
        st.write("Please select an environment")
