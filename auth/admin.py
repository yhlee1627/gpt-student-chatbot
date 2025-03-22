import streamlit as st
import pandas as pd
import plotly.express as px
import os

from services.chat_storage import load_chat_list, load_chat_history
from services.gpt_rubric import (
    grade_conversation,
    save_evaluation_result,
    load_evaluation_result
)
from services.evaluation_stats import load_all_evaluation_results
from services.pdf_report import generate_pdf_report

def show_admin_page():
    st.title("🛠️ 관리자 페이지")

    # ✅ 탭 구성
    tab1, tab2 = st.tabs(["📄 학생 개별 평가 보기", "📊 전체 평가 통계"])

    # -------------------------------
    # 📄 탭 1: 학생 개별 대화 및 평가
    # -------------------------------
    with tab1:
        # ✅ 사용자 목록 불러오기 (secrets 또는 users.csv)
        if "users" in st.secrets:
            student_ids = list(st.secrets["users"].keys())
        else:
            try:
                users_df = pd.read_csv("data/users.csv", dtype=str)
                student_ids = users_df["student_id"].tolist()
            except FileNotFoundError:
                st.error("❗ 사용자 목록을 불러올 수 없습니다.")
                student_ids = []

        student_ids = [uid for uid in student_ids if uid != "admin"]

        if not student_ids:
            st.warning("학생 정보가 없습니다.")
            return

        selected_student = st.selectbox("👥 학생 선택", student_ids)

        chat_list = load_chat_list(selected_student)
        selected_chat = st.selectbox("💬 대화 선택", chat_list if chat_list else ["(대화 없음)"])

        if selected_chat and selected_chat != "(대화 없음)":
            chat_data = load_chat_history(selected_student, selected_chat)
            st.markdown(f"### 📁 대화 ID: `{selected_chat}`")

            for user_msg, gpt_msg in chat_data:
                st.markdown(f"**🧑‍🎓 {selected_student}:** {user_msg}")
                st.markdown(f"**🤖 GPT:** {gpt_msg}")
                st.markdown("---")

            # GPT 자동 평가
            if chat_data:
                if st.button("🧠 GPT 자동 평가"):
                    with st.spinner("GPT가 평가 중입니다..."):
                        result = grade_conversation(chat_data)
                        save_evaluation_result(selected_student, selected_chat, result)
                    st.success("✅ 평가 결과가 저장되었습니다.")

            # 평가 결과 표시
            eval_result = load_evaluation_result(selected_chat)
            if eval_result:
                st.markdown("### 📊 GPT 평가 결과")
                explanation_dict = eval_result.get("explanations", {})
                for criterion, score in eval_result["scores"].items():
                    explanation = explanation_dict.get(criterion, "")
                    st.markdown(f"- **{criterion}**: `{score}`점")
                    if explanation:
                        st.caption(f"📝 {explanation}")
                st.markdown("**총평:**")
                st.success(eval_result["summary"])

                # PDF 다운로드
                pdf_path = generate_pdf_report(selected_student, selected_chat, eval_result)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📄 PDF 리포트 다운로드",
                        data=f,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf"
                    )
            else:
                st.info("이 대화는 아직 GPT 자동 평가되지 않았습니다.")

    # -------------------------------
    # 📊 탭 2: 전체 평가 통계
    # -------------------------------
    with tab2:
        df = load_all_evaluation_results()

        if df.empty:
            st.info("아직 저장된 평가 결과가 없습니다.")
        else:
            score_columns = ["질문의 다양성", "질문의 깊이", "질문의 진전성", "자기주도성"]
            df[score_columns] = df[score_columns].astype(float)

            st.markdown("### ✅ 항목별 평균 점수")
            avg_scores = df[score_columns].mean().reset_index()
            avg_scores.columns = ["항목", "평균 점수"]

            fig = px.bar(avg_scores, x="항목", y="평균 점수", text="평균 점수",
                         color="항목", color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition="outside")
            fig.update_layout(yaxis_range=[0, 5], height=400)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### 👥 학생별 평가 테이블")
            st.dataframe(df, use_container_width=True)

            selected_person = st.selectbox("🔍 학생별 점수 보기", df["학생 ID"].unique())
            if selected_person:
                per_student_df = df[df["학생 ID"] == selected_person]
                for idx, row in per_student_df.iterrows():
                    st.markdown(f"#### 🎯 대화: {row['대화 ID']}")
                    scores = row[score_columns]
                    fig2 = px.bar(scores, x=scores.index, y=scores.values,
                                  text=scores.values, color=scores.index,
                                  color_discrete_sequence=px.colors.qualitative.Set3)
                    fig2.update_traces(textposition="outside")
                    fig2.update_layout(yaxis_range=[0, 5], height=300)
                    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------------
    # 🔓 로그아웃
    # -------------------------------
    st.markdown("---")
    if st.button("🔓 로그아웃"):
        for key in ["student_id", "chat_history", "conversation_id"]:
            st.session_state.pop(key, None)
        st.rerun()