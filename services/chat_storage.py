import os
import json
from datetime import datetime

DATA_DIR = "data/chat_logs"

def generate_conversation_id(student_id):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{student_id}_{timestamp}"

def get_chat_filepath(student_id, conversation_id):
    os.makedirs(DATA_DIR, exist_ok=True)
    return os.path.join(DATA_DIR, f"{conversation_id}.json")

def save_chat_history(student_id, conversation_id, chat_history):
    filepath = get_chat_filepath(student_id, conversation_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

def load_chat_history(student_id, conversation_id):
    filepath = get_chat_filepath(student_id, conversation_id)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def load_chat_list(student_id):
    os.makedirs(DATA_DIR, exist_ok=True)
    all_files = os.listdir(DATA_DIR)
    return sorted([
        f.replace(".json", "") for f in all_files
        if f.endswith(".json") and f.startswith(student_id)
    ])

def delete_chat(student_id, conversation_id):
    filepath = get_chat_filepath(student_id, conversation_id)
    if os.path.exists(filepath):
        os.remove(filepath)

def rename_chat(student_id, old_id, new_id):
    old_path = get_chat_filepath(student_id, old_id)
    new_id = f"{student_id}_{new_id}" if not new_id.startswith(student_id) else new_id
    new_path = get_chat_filepath(student_id, new_id)
    if os.path.exists(old_path) and not os.path.exists(new_path):
        os.rename(old_path, new_path)