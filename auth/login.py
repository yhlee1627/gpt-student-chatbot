import streamlit as st
from services.user_service import authenticate_user

def show_login_page():
    st.title("🔐 GPT 챗봇 로그인")

    with st.form("login_form"):
        student_id = st.text_input("학번을 입력하세요")
        password = st.text_input("비밀번호를 입력하세요", type="password")
        submitted = st.form_submit_button("로그인")

        if submitted:
            if authenticate_user(student_id, password):
                st.session_state["student_id"] = student_id
                st.rerun()
            else:
                st.error("학번 또는 비밀번호가 올바르지 않습니다.")