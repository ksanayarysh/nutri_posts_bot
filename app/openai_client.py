from __future__ import annotations
import json
import time
import requests


class OpenAIClient:
    def __init__(self, api_key: str, model: str, timeout: int = 120, retries: int = 5, backoff_sec: float = 2.0):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.retries = retries
        self.backoff_sec = backoff_sec

    def generate_text(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.model,
            "instructions": system_prompt,
            "input": [
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": user_prompt}],
                }
            ],
        }

        last_err: Exception | None = None

        for attempt in range(1, self.retries + 1):
            try:
                r = requests.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    data=json.dumps(payload),
                    timeout=self.timeout,
                )

                if not r.ok:
                    # 429/5xx worth retrying; 4xx usually not (but keep message)
                    msg = f"OpenAI error {r.status_code}: {r.text}"
                    if r.status_code in (429, 500, 502, 503, 504):
                        raise RuntimeError(msg)
                    raise RuntimeError(msg)

                data = r.json()
                text = data.get("output_text", "")
                if isinstance(text, str) and text.strip():
                    return text.strip()

                # Fallback parse
                chunks = []
                out = data.get("output")
                if isinstance(out, list):
                    for item in out:
                        if isinstance(item, dict):
                            for c in item.get("content", []) or []:
                                if isinstance(c, dict) and isinstance(c.get("text"), str):
                                    chunks.append(c["text"])
                final = "\n".join(chunks).strip()
                if final:
                    return final

                raise RuntimeError(f"OpenAI: no text in response: {data}")

            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectTimeout) as e:
                last_err = e
            except Exception as e:
                last_err = e

            if attempt < self.retries:
                time.sleep(self.backoff_sec * attempt)

        raise RuntimeError(f"OpenAI request failed after {self.retries} attempts: {last_err}")
