import os
import json
import pandas as pd

def load_all_evaluation_results():
    path = "data/evaluation_logs"
    records = []

    for fname in os.listdir(path):
        if fname.endswith("_evaluation.json"):
            with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                row = {
                    "학생 ID": data["student_id"],
                    "대화 ID": data["conversation_id"]
                }
                row.update(data["scores"])  # 점수 포함
                records.append(row)

    return pd.DataFrame(records)