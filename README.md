# Nutri Poster

Daily Telegram nutrition post generator + publisher.

## Setup
1) Create a Telegram bot, add it as admin to your channel.
2) Copy `.env.example` to `.env` and fill values.
3) Install deps:
   pip install -r requirements.txt

## Run once (manual)
python -m app.run_once

## Smoke test (no Telegram)
python scripts/smoke_test.py

## Scheduling
Use Railway Cron / GitHub Actions / any cron to run:
python -m app.run_once
