from __future__ import annotations
import random

from .prompts import build_system_prompt, build_user_prompt


def _clamp(text: str, max_chars: int) -> str:
    t = text.strip()
    if len(t) <= max_chars:
        return t
    t = t[:max_chars].rstrip()
    # Try to end on paragraph boundary
    if "\n" in t:
        t = t.rsplit("\n", 1)[0].rstrip()
    return t + "\n\n(продолжение завтра)"


def make_post_text(
    *,
    openai_client,
    rubric: str,
    topic: str,
    language: str,
    min_chars: int,
    max_chars: int,
    max_hashtags: int,
    bot_link: str,
    add_disclaimer: bool,
) -> str:
    include_soft_plug = (random.randint(1, 3) == 1)

    system_prompt = build_system_prompt(
        language=language,
        min_chars=min_chars,
        max_chars=max_chars,
        max_hashtags=max_hashtags,
        bot_link=bot_link,
        include_soft_plug=include_soft_plug,
    )
    user_prompt = build_user_prompt(rubric, topic)

    text = openai_client.generate_text(system_prompt, user_prompt)
    text = _clamp(text, max_chars=max_chars)

    if add_disclaimer:
        text += "\n\nИнформация носит общий характер и не заменяет консультацию врача."
    return text
