import os
import json
import re
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

# ✅ GPT 응답 함수 (이전 대화 포함)
def get_gpt_response(prompt, history=None):
    if history is None:
        history = []

    messages = [{"role": "system", "content": "너는 학생을 도와주는 친절한 조수야."}]
    for user, assistant in history:
        messages.append({"role": "user", "content": user})
        messages.append({"role": "assistant", "content": assistant})

    messages.append({"role": "user", "content": prompt})

    chat_response = client.chat.completions.create(
        model="gpt-4o-mini",  # 또는 gpt-3.5-turbo
        messages=messages
    )
    return chat_response.choices[0].message.content

# ✅ CSV로 누적 저장 (기존 방식 유지)
def save_log(student_id, timestamp, question, answer, file_path="chat_log.csv"):
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([student_id, timestamp, question, answer])

# ✅ JSON으로 대화별 저장 (새 기능)
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