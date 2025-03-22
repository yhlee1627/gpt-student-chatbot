import streamlit as st
st.set_page_config(page_title="GPT 챗봇", layout="wide")

from auth.login import show_login_page
from auth.chat import show_chat_page, show_sidebar
from auth.admin import show_admin_page

# 세션 초기화
if "student_id" not in st.session_state:
    st.session_state["student_id"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = None

# 페이지 라우팅
if st.session_state["student_id"] == "admin":
    show_admin_page()
elif st.session_state["student_id"] is not None:
    with st.sidebar:
        show_sidebar()
    show_chat_page()
else:
    show_login_page()