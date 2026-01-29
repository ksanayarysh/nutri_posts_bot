from __future__ import annotations
import requests


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


class TelegramClient:
    def __init__(self, bot_token: str, timeout: int = 40):
        self.bot_token = bot_token
        self.timeout = timeout

    def send_message(self, chat_id: str, text: str, disable_preview: bool = False) -> None:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": _escape_html(text),
            "parse_mode": "HTML",
            "disable_web_page_preview": disable_preview,
        }
        r = requests.post(url, data=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        if not data.get("ok"):
            raise RuntimeError(f"Telegram sendMessage failed: {data}")
