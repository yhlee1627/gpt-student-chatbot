import os
import json
import csv
import re
from datetime import datetime
from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv

# ✅ 환경변수 로드
load_dotenv()

# ✅ API 키 불러오기
api_key = st.secrets.get("openai_api_key", os.getenv("OPENAI_API_KEY"))

# ✅ 키 확인
if not api_key:
    raise ValueError("❗ OpenAI API 키가 설정되지 않았습니다. .env 또는 secrets.toml을 확인하세요.")

# ✅ 클라이언트 생성
client = OpenAI(api_key=api_key)

# ✅ system_prompt를 세션에 한 번만 저장 (토큰 절약)
if "system_prompt" not in st.session_state:
    st.session_state["system_prompt"] = """
    당신은 캡스톤 디자인 수업에 참여한 예비교사들을 돕는 AI 멘토입니다.

    당신의 역할은 단순한 정답 제공자가 아니라,
    학생이 자신의 생각을 발전시킬 수 있도록 돕는 사고 촉진자이자 질문 파트너입니다.

    다음과 같은 방식으로 대답해주세요.:

    1. 학생의 사고 수준을 파악해, 그보다 약간 높은 수준의 질문을 던져주세요. (ZPD 기반 피드백)
    2. 정답을 바로 말하지 말고, 사고 흐름을 따라가며 단계적으로 사고를 유도해주세요. (Chain of Thought 방식)
    3. "왜 그렇게 생각했어?", "다른 가능성은?" 같은 소크라테스식 질문을 사용해주세요.
    4. 학생의 표현이 모호하면 질문을 명확하게 재구성하도록 도와주세요.

    특히, 학생은 마이크로비트를 활용한 캡스톤 프로젝트를 설계하고 있습니다.
    기능 구현보다 '설계 사고'를 유도하고, 생각을 확장하는 방향으로 피드백을 제공해 주세요.
    """

# ✅ GPT 응답 함수
def get_gpt_response(prompt, history=None):
    if history is None:
        history = []

    messages = [{"role": "system", "content": st.session_state["system_prompt"]}]
    
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})

    messages.append({"role": "user", "content": prompt})

    chat_response = client.chat.completions.create(
        model="gpt-4o-mini",  # 또는 gpt-3.5-turbo
        messages=messages
    )

    return chat_response.choices[0].message.content

# ✅ CSV로 누적 저장
def save_log(student_id, timestamp, question, answer, file_path="chat_log.csv"):
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([student_id, timestamp, question, answer])

# ✅ JSON으로 대화별 저장
def save_chat_history(student_id, conversation_id, chat_history):
    os.makedirs("data/chat_logs", exist_ok=True)
    filepath = f"data/chat_logs/{conversation_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

# ✅ 특정 대화 불러오기
def load_chat_history(student_id, conversation_id):
    filepath = f"data/chat_logs/{conversation_id}.json"
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ✅ 학생의 전체 대화 목록 가져오기
def load_chat_list(student_id):
    os.makedirs("data/chat_logs", exist_ok=True)
    all_files = os.listdir("data/chat_logs")
    return [f.replace(".json", "") for f in all_files if f.startswith(student_id)]

# ✅ 대화 ID 생성
def generate_conversation_id(student_id):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{student_id}_{now}"