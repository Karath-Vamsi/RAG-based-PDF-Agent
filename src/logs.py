import os

LOG_DIR = "log_history"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "conversation_log.txt")

def log_conversation_to_file(messages, file_path=LOG_FILE_PATH):
    with open(file_path, "a") as f:
        for msg in messages:
            f.write(f"{msg.type.upper()}: {msg.content}\n")
        f.write("\n---\n")