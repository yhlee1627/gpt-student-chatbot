import os
import json
import pandas as pd

def load_all_evaluation_results():
    path = "data/evaluation_logs"

    # ✅ 폴더가 없으면 생성 (Streamlit Cloud 첫 실행 대비)
    os.makedirs(path, exist_ok=True)

    records = []

    for fname in os.listdir(path):
        if fname.endswith("_evaluation.json"):
            with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                row = {
                    "학생 ID": data["student_id"],
                    "대화 ID": data["conversation_id"]
                }
                row.update(data["scores"])
                records.append(row)

    return pd.DataFrame(records)