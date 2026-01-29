from __future__ import annotations
import time
from datetime import datetime, timezone

from .config import get_settings
from .topics import pick_daily
from .openai_client import OpenAIClient
from .telegram_client import TelegramClient
from .generator import make_post_text


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_once() -> None:
    s = get_settings()

    rubric, topic = pick_daily()
    print(f"[run_once] rubric={rubric} topic={topic}")
    print(f"[run_once] channel_chat_id={s.tg_channel_chat_id}")

    openai = OpenAIClient(
        api_key=s.openai_api_key,
        model=s.openai_model,
        timeout=s.http_timeout,
        retries=s.retry_count,
        backoff_sec=s.retry_sleep_sec,
    )

    tg = TelegramClient(bot_token=s.tg_bot_token, timeout=s.http_timeout)

    try:
        text = make_post_text(
            openai_client=openai,
            rubric=rubric,
            topic=topic,
            language=s.post_language,
            min_chars=s.min_chars,
            max_chars=s.max_chars,
            max_hashtags=s.max_hashtags,
            bot_link=s.bot_link,
            add_disclaimer=s.add_disclaimer,
        )

        # Публикация в канал
        tg.send_message(chat_id=s.tg_channel_chat_id, text=text)

        # Уведомление тебе
        tg.send_message(
            chat_id=s.admin_chat_id,
            text=f"✅ Пост опубликован\nТема: {topic}",
            disable_preview=True,
        )

    except Exception as e:
        # Уведомление об ошибке
        tg.send_message(
            chat_id=s.admin_chat_id,
            text=f"❌ Ошибка при публикации:\n{e}",
            disable_preview=True,
        )
        raise



def main() -> None:
    s = get_settings()

    last_err: Exception | None = None
    for attempt in range(1, s.retry_count + 1):
        try:
            run_once()
            print(f"[{now_utc_iso()}] OK: posted successfully")
            return
        except Exception as e:
            last_err = e
            print(f"[{now_utc_iso()}] attempt {attempt}/{s.retry_count} failed: {e}")
            if attempt < s.retry_count:
                time.sleep(s.retry_sleep_sec)

    raise SystemExit(f"Failed after {s.retry_count} attempts: {last_err}")


if __name__ == "__main__":
    main()
