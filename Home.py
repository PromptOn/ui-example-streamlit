import streamlit as st

import components.layout as layout
import components.login as login


layout.show_layout()

st.write("# PromptOn UI Demo")

login.login()

st.markdown(
    """
This is a rudimentary technical demo.

For access, email hello@prompton.ai.

* Not all features are exposed.
* API is solid and tested but this UI is not
* If your are in trouble press `r` to Rerun the page (or select it from the top right corner menu)
* UX is not taken into proper consideration

Bottom line:

  Create your own UI using PromptOn's Python or Node SDK
"""
)

st.divider()

col1, col2 = st.columns([10, 2])
col2.write("Design :lemon: Prize - 2023")

repo_link = """
[![Repo](https://badgen.net/badge/icon/GitHub?icon=github&label)  github.com/PromptOn/prompton ](https://github.com/PromptOn/prompton) 
"""
col1.markdown(repo_link, unsafe_allow_html=True)
