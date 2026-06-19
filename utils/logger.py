from datetime import datetime

LOG_FILE = "query_logs.txt"

def log_info(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"[INFO] {timestamp} | {message}\n"
        )

def log_error(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"[ERROR] {timestamp} | {message}\n"
        )