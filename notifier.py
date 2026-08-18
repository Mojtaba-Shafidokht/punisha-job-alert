import os
import re
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PROXY = os.getenv("TELEGRAM_PROXY")

RLM = "\u200F"
LRI = "\u2066"
PDI = "\u2069"

_LTR_RUN = re.compile(r'[A-Za-z0-9,./:_%-]+')


def _isolate_ltr_runs(text):
    return _LTR_RUN.sub(lambda m: f"{LRI}{m.group()}{PDI}", text)


def _get_proxies():
    if PROXY:
        return {"http": PROXY, "https": PROXY}
    return None


FIELD_LABELS = {
    "title": "عنوان پروژه",
    "description": "توضیحات پروژه",
    "skills": "مهارت‌های مورد نیاز",
    "deadline": "زمان پیشنهاد",
    "bids": "تعداد پیشنهادها",
    "budget": "بودجه‌ی کارفرما",
    "url": "آدرس پروژه",
}


def _format_projects(project):
    formatted_project = ""
    for k, v in FIELD_LABELS.items():
        value = project.get(k)
        if project.get(k) is None:
            value = "نامشخص"

        if project.get(k) is not None and k == "skills":
            value = ", ".join(project.get(k))

        formatted_project += _isolate_ltr_runs(f"{RLM}{v}: \n{value}\n\n")

    return formatted_project


def send_notification(new_projects):
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
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


def send_login_alert():
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"🔔 Ponisha Job Alert\n🕐 {date}\n\n"
    alert_text = "⚠️ Session expired - run with --login to sign in again."
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    final_message = header + alert_text
    try:
        requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": final_message
            },
            proxies=_get_proxies(),
            timeout=20
        )

    except Exception as e:
        print(f"⚠️ Failed to send Telegram notification: {e}")