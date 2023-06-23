import streamlit as st


def show_sidebar():
    if st.session_state.get("current_user"):
        with st.sidebar:
            if st.session_state["current_user"]:
                my_user = st.session_state["current_user"]
                my_org = st.session_state["current_org"]
                my_role = my_user.role.value if my_user.role else "No role"

                st.write(my_user.email)
                st.write(f" { my_role} @ {my_org.name}")
                st.write("Env: ", st.session_state["prompton_env"])

                logout_submitted = st.button("Logout")

                if logout_submitted:
                    st.session_state.clear()
                    st.cache_data.clear()
                    st.experimental_rerun()
