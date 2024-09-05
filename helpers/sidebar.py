import streamlit as st


def show() -> None:
    with st.sidebar:
        st.markdown(f"""
            <a href="/" style="color:black;text-decoration: none;">
                <div style="display:table;margin-top:-11rem;margin-left:0%;">
                    <span style="color: black">&nbsp;AI Tools Chat</span>
                    <span style="font-size: 0.8em; color: grey">&nbsp;&nbsp;v0.1.1</span>
                </div>
            </a>

                """, unsafe_allow_html=True)

        reload_button = st.button("↪︎  Reload Page")
        if reload_button:
            st.session_state.clear()
            st.rerun()
