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

EVAL_DIR = "data/evaluation_logs"        # 평가 결과 저장 경로

# ✅ GPT에게 평가 요청
def grade_conversation(chat_data):
    # 🔹 학생 질문만 추출
    dialogue_text = ""
    for user_msg, _ in chat_data:
        dialogue_text += f"학생 질문: {user_msg}\n"

    # 🔹 시스템 프롬프트
    system_prompt = """
너는 교육 평가자야. 아래는 학생이 GPT와 대화하는 과정에서 남긴 질문들이다.
이 질문들만 보고, 다음 루브릭을 기준으로 학생의 사고 수준과 질문 역량을 평가해줘.

루브릭 항목 (각 항목은 1~5점):
1. 질문의 다양성: 다양한 유형(정보, 비교, 적용 등)의 질문을 했는가?
2. 질문의 깊이: 질문이 단순한 정보 요청을 넘어서 사고를 요구하는가?
3. 질문의 진전성: 질문이 점점 더 구체적이고 정교해졌는가?
4. 자기주도성: 대화를 학생이 주도하려는 노력이 있었는가?

출력 예시:

1. 질문의 다양성: 4
설명: 정보요청과 확장질문이 적절히 섞여 있었음.

...

총평: 이 학생은 질문을 통해 사고를 확장하려는 의도를 잘 보여주었음.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": dialogue_text}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 또는 gpt-3.5-turbo
        messages=messages
    )

    content = response.choices[0].message.content

    # ✅ 응답 파싱
    scores = {}
    explanations = {}
    summary = ""
    current_criterion = ""

    for line in content.strip().splitlines():
        line = line.strip()
        if re.match(r"^\d+\.", line):  # 예: "1. 질문의 다양성: 4"
            match = re.match(r"\d+\.\s*(.+?):\s*(\d+)", line)
            if match:
                criterion = match.group(1).strip()
                score = match.group(2).strip()
                scores[criterion] = score
                current_criterion = criterion
        elif line.startswith("설명:") and current_criterion:
            explanations[current_criterion] = line.replace("설명:", "").strip()
        elif line.startswith("총평:"):
            summary = line.replace("총평:", "").strip()

    return {
        "scores": scores,
        "explanations": explanations,
        "summary": summary
    }

# ✅ 평가 결과 저장
def save_evaluation_result(student_id, conversation_id, result):
    os.makedirs(EVAL_DIR, exist_ok=True)
    result_data = {
        "student_id": student_id,
        "conversation_id": conversation_id,
        "scores": result["scores"],
        "explanations": result["explanations"],
        "summary": result["summary"]
    }
    filepath = os.path.join(EVAL_DIR, f"{conversation_id}_evaluation.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

# ✅ 평가 결과 불러오기
def load_evaluation_result(conversation_id):
    filepath = os.path.join(EVAL_DIR, f"{conversation_id}_evaluation.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None