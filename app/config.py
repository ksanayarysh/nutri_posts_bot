from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str

    tg_bot_token: str
    tg_channel_chat_id: str

    post_language: str
    bot_link: str

    min_chars: int
    max_chars: int
    max_hashtags: int
    add_disclaimer: bool

    http_timeout: int
    retry_count: int
    retry_sleep_sec: float

    admin_chat_id: str


def _must(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


def get_settings() -> Settings:
    return Settings(
        openai_api_key=_must("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5").strip(),

        tg_bot_token=_must("TG_BOT_TOKEN"),
        tg_channel_chat_id=_must("TG_CHANNEL_CHAT_ID"),

        post_language=os.getenv("POST_LANGUAGE", "ru").strip(),
        bot_link=os.getenv("BOT_LINK", "https://t.me/your_bot").strip(),

        min_chars=int(os.getenv("MIN_CHARS", "700")),
        max_chars=int(os.getenv("MAX_CHARS", "1200")),
        max_hashtags=int(os.getenv("MAX_HASHTAGS", "6")),
        add_disclaimer=os.getenv("ADD_DISCLAIMER", "1").strip() == "1",

        http_timeout=int(os.getenv("HTTP_TIMEOUT", "40")),
        retry_count=int(os.getenv("RETRY_COUNT", "3")),
        retry_sleep_sec=float(os.getenv("RETRY_SLEEP_SEC", "2.5")),
        admin_chat_id=_must("ADMIN_CHAT_ID"),
    )
