import pandas as pd
import os

# ✅ 사용자 목록 CSV를 불러오는 함수
def load_users(filepath="data/users.csv"):
    if not os.path.exists(filepath):
        print(f"❌ 파일이 존재하지 않음: {filepath}")
        return {}

    try:
        # 모든 열을 문자열(str)로 강제 불러오기
        df = pd.read_csv(filepath, dtype=str)

        # 디버깅용 출력
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