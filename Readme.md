# Quran Completion Bot

A Telegram bot for collaborative Quran completion circles (Khatma). Users create Khatmas (30-part Quran recitation projects), book individual parts with deadlines, and receive automated reminders.

Live bot: [Quran Completion Bot](https://t.me/QuranCompletionBot)

Built in Python ❤️.

---

## Quick Start (Docker)

```bash
# 1. Copy and fill in environment variables
cp .env.example .env

# 2. Pre-authenticate Google Drive (once, before first deploy)
uv run python -c "from bot.DriveManager import DriveManager; DriveManager()"
# Complete the browser OAuth flow — saves Secret Files/token.json

# 3. Build and start all services
docker compose up --build -d

# 4. View logs
docker compose logs -f quranbot_bot
```

## Local Development

```bash
# Install dependencies
uv sync

# Start the bot (requires .env with DATABASE_URI pointing to a local Postgres)
uv run python main.py

# In separate terminals (optional):
uv run uvicorn db.Admin:app --port 8002
uv run uvicorn db.Backup_Database:app --port 8001
```

## Environment Variables

Copy `.env.example` and fill in the required values:

| Variable | Description |
|---|---|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `WEBHOOK_URL` | Public HTTPS URL for the webhook (e.g. `https://1.2.3.4:8443`) |
| `DATABASE_URI` | Full PostgreSQL URI (asyncpg format) |
| `QURAN_FILES_CHANNEL_ID` | Telegram channel ID storing Quran file assets |
| `QURAN_DAILY_PAGE_CHANNEL_ID` | Channel ID for daily page posts |
| `SECRET_TOKEN` | Webhook secret token |
| `PRIVATE_KEY` | Path to TLS private key file |
| `CERT` | Path to TLS certificate file |
| `ADMIN_PAGE_PASSWORD` | Password for the sqladmin web UI |
| `ADMIN_SECRET_KEY` | Secret key for admin session cookies |
| `DEVELOPER_CHAT_ID` | Telegram chat ID to receive backup notifications |
| `GOOGLE_DRIVE_BACKUP_FOLDER_ID` | Google Drive folder ID for database backups |

## Lint & Format

```bash
ruff check . --config .ruff.toml
ruff format . --config .ruff.toml
pre-commit run --all-files
```

## Project Structure

```
main.py                      # Bot entrypoint: handlers, job queue, webhook
db/
  db.py                      # All async DB operations (SQLAlchemy + asyncpg)
  models.py                  # ORM models (User, Khatma, Khatma_Parts, Quran_File, …)
  Admin.py                   # sqladmin web UI (port 8002)
  Backup_Database.py         # Backup service: pg_dump → gzip → Google Drive (port 8001)
  sql_functions.py           # SQLAlchemy utcnow() extension
  reset_db.py                # DESTRUCTIVE schema reset — manual use only
bot/
  router.py                  # Handler registration grouped by domain
  state_dispatcher.py        # @register_state dispatch table
  MainMenu/                  # 8 handler modules (one per feature area)
  DriveManager.py            # Google Drive OAuth2 client
  Schedule_Jobs.py           # 5 background jobs
config/
  UserStates.py              # State machine string constants
  CallBackData.py            # Callback data constants
  Keyboards.py               # Keyboard factory functions
  Text.py                    # Arabic message template builders
domain/                      # DTOs / value objects (ExpiredPart, NotificationPart, …)
docker/
  entrypoint.sh              # Waits for Postgres, then starts the service
  healthcheck.py             # SELECT 1 health probe for Docker
```

## Database Reset

Never run this from the bot. To reset the schema on the host:

```bash
python -m db.reset_db
```

All data is permanently deleted.

## Testing

```bash
uv add --dev pytest pytest-asyncio
uv run pytest tests/
```

Highest-value targets: utility functions in `bot/Global_Functions.py` and DB repository functions in `db/db.py`.
