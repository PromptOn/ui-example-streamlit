import streamlit as st
import auth


def show_header():
    if st.session_state["auth_token"]:
        st.set_page_config(layout="wide", page_title="Prompton API Example")
        prompton = auth.get_prompton()

        my_org = prompton.orgs.get_current_user_org()
        my_user = prompton.users.get_current_user()
        my_role = my_user.role.value if my_user.role else "No role"

        col1, col2, _, col3 = st.columns([10, 5, 5, 5])

        col1.write(f"{my_user.email}  @  {my_org.name} ( { my_role} )")

        col2.write(st.session_state["prompton_env"])

        with col3:
            logout_submitted = st.button("Logout")
            if logout_submitted:
                st.session_state["auth_token"] = None
                st.experimental_rerun()
