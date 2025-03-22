import streamlit as st
import pandas as pd
import os

# ✅ 사용자 불러오기 함수 (Cloud 또는 CSV)
def load_users():
    if "users" in st.secrets:
        print("✅ secrets.toml에서 사용자 불러옴")
        return st.secrets["users"]

    filepath = "data/users.csv"
    if not os.path.exists(filepath):
        print(f"❌ 파일이 존재하지 않음: {filepath}")
        return {}

    try:
        df = pd.read_csv(filepath, dtype=str)
        print("✅ 불러온 사용자 목록:")
        print(df)
        return dict(zip(df["student_id"], df["password"]))
    except Exception as e:
        print(f"❌ 사용자 목록 불러오기 중 오류 발생: {e}")
        return {}

# ✅ 로그인 인증 함수
def authenticate_user(student_id, password):
    users = load_users()

    print(f"🔍 입력받은 ID: {student_id}, PW: {password}")
    print(f"🔍 DB의 PW: {users.get(student_id)}")

    return users.get(student_id) == password