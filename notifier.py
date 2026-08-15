from datetime import datetime
import requests
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY = os.getenv("TELEGRAM_PROXY")


def _get_proxies():
    if PROXY:
        return {"http": PROXY, "https": PROXY}
    return None


def _format_projects(project):
    formatted_project = ""
    for k, v in project.items():
        if v is None:
            v = "نامشخص"

        if k == "skills":
            v = ", ".join(v)

        formatted_project += f"{k.capitalize()}: {v}\n"

    return formatted_project


def send_notification(new_projects):
    date = datetime.now().strftime("%Y-%m-%d %H:%S")
    header = f"🔔 Ponisha Job Alert\n🕐 {date}\n\n"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    for project in new_projects.values():
        project_text = _format_projects(project)
        final_message = header + project_text
        try:
            requests.post(
                url,
                data={
                    "chat_id": CHAT_ID,
                    "text": final_message,
                    "disable_web_page_preview": True
                },
                proxies=_get_proxies(),
                timeout=20
            )

        except Exception as e:
            print(f"⚠️ Failed to send Telegram notification: {e}")
