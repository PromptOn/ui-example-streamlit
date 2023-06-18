import streamlit as st
import auth
from streamlit_option_menu import option_menu


def show():
    st.set_page_config(layout="wide", page_title="Prompton API Example")

    show_header()
    show_sidebar()


def show_header():
    pass


def show_sidebar():
    with st.sidebar:
        choose = option_menu("PromptOn", ["Inferences", "Prompts"], default_index=0)
        st.session_state["nav_selection"] = choose

        if st.session_state["auth_token"]:
            prompton = auth.get_prompton()

            my_org = prompton.orgs.get_current_user_org()
            my_user = prompton.users.get_current_user()
            my_role = my_user.role.value if my_user.role else "No role"

            st.write(my_user.email)
            st.write(f" { my_role} @ {my_org.name}")
            st.write("Env: ", st.session_state["prompton_env"])

            logout_submitted = st.button("Logout")
            if logout_submitted:
                st.session_state["auth_token"] = None
                st.experimental_rerun()
