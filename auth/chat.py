import streamlit as st
from services.gpt_service import get_gpt_response
from services.chat_storage import (
    generate_conversation_id,
    save_chat_history,
    load_chat_history,
    load_chat_list,
    delete_chat,
    rename_chat
)


def show_sidebar():
    student_id = st.session_state["student_id"]
    chat_list = load_chat_list(student_id)

    st.markdown("## 👤 사용자 정보")
    st.markdown(f"**학번:** `{student_id}`")
    st.markdown("---")

    st.markdown("## 💬 대화 목록")

    if st.button("🆕 새 대화 시작"):
        st.session_state["conversation_id"] = generate_conversation_id(student_id)
        st.session_state["chat_history"] = []
        st.rerun()

    for chat_id in chat_list:
        with st.container():
            col1, col2, col3 = st.columns([5, 1, 1])

            # 대화명 표시 및 선택
            with col1:
                if st.button(f"📁 {chat_id}", key=f"select_{chat_id}"):
                    st.session_state["conversation_id"] = chat_id
                    st.session_state["chat_history"] = load_chat_history(student_id, chat_id)
                    st.rerun()

            # ✏️ 이름 변경 버튼
            with col2:
                if st.button("✏️", key=f"rename_{chat_id}"):
                    st.session_state["rename_target"] = chat_id  # 이 대화 ID의 이름을 바꿀 거라는 상태 기록

            # 🗑️ 삭제 버튼
            with col3:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    delete_chat(student_id, chat_id)
                    st.rerun()

        # ✅ 이름 바꾸기 입력창과 버튼 (rename_target에 해당될 때만 표시)
        if st.session_state.get("rename_target") == chat_id:
            new_name = st.text_input("새 이름 입력", key=f"rename_input_{chat_id}", placeholder="새 이름")
            if st.button("변경", key=f"rename_button_{chat_id}") and new_name:
                rename_chat(student_id, chat_id, new_name)
                st.session_state.pop("rename_target", None)  # 상태 초기화
                st.rerun()

    st.markdown("---")
    if st.button("🔓 로그아웃"):
        for key in ["student_id", "chat_history", "conversation_id"]:
            st.session_state.pop(key, None)
        st.rerun()

def show_chat_page():
    st.title("🤖 GPT 챗봇과 대화하기")

    for user_msg, gpt_msg in st.session_state["chat_history"]:
        st.markdown(f"🧑‍🎓 **나:** {user_msg}")
        st.markdown(f"🤖 **GPT:** {gpt_msg}")
        st.markdown("---")

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("GPT에게 질문하기:", key="user_input")
        submitted = st.form_submit_button("보내기")

        if submitted and user_input:
            with st.spinner("GPT가 답변 중입니다..."):
                response = get_gpt_response(user_input, st.session_state["chat_history"])

            st.session_state["chat_history"].append((user_input, response))

            # ✅ conversation_id가 없으면 새로 생성
            if not st.session_state.get("conversation_id"):
                st.session_state["conversation_id"] = generate_conversation_id(st.session_state["student_id"])

            # ✅ 안전하게 저장
            save_chat_history(
                st.session_state["student_id"],
                st.session_state["conversation_id"],
                st.session_state["chat_history"]
            )

            st.rerun()