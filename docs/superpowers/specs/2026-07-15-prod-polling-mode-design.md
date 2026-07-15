# Production Polling Mode Design

**Date:** 2026-07-15
**Status:** Approved

## Overview

Switch the bot's production deployment from webhook (`run_webhook`, TLS cert/key, `SECRET_TOKEN`, inbound port 8443) to long-polling (`run_polling`), matching what dev already uses. The webhook code path is not deleted — it stays available behind a new `USE_WEBHOOK` flag in case webhook mode is needed again later, but production defaults to polling and no longer provisions or requires any webhook-only config.

## Background

`main.py` currently branches on `APP_ENV`:
- `APP_ENV=dev` → `application.run_polling()`
- `APP_ENV=prod` → `application.run_webhook(...)` — needs `WEBHOOK_URL`, `WEBHOOK_LISTEN_HOST`, `WEBHOOK_LISTEN_PORT`, `SECRET_TOKEN`, `PRIVATE_KEY`, `CERT` (self-signed TLS cert/key pair), and an open inbound port (8443) on the production host.

The production bot is not yet live, so there is no cutover/downtime concern. The decision (see prior discussion) is to keep both transport code paths but flip the default to polling, controlled by a dedicated flag independent of `APP_ENV`.

python-telegram-bot's `run_polling()` bootstrap always calls Telegram's `deleteWebhook` before starting the polling loop (confirmed in `telegram/ext/_updater.py`), so no manual webhook-deletion step is needed even if a webhook was previously registered against this bot token.

## Design

### 1. `main.py` — `USE_WEBHOOK` flag

Add:
```python
USE_WEBHOOK = os.getenv('USE_WEBHOOK', '0') == '1'
```

Change the transport branch from:
```python
if APP_ENV == 'prod':
    application.run_webhook(...)
else:
    application.run_polling()
```
to:
```python
if APP_ENV == 'prod' and USE_WEBHOOK:
    application.run_webhook(...)
else:
    application.run_polling()
```

`APP_ENV` keeps its existing dev/prod meaning; `USE_WEBHOOK` is the sole control for which transport is used. All existing `WEBHOOK_URL`/`WEBHOOK_LISTEN_HOST`/`WEBHOOK_LISTEN_PORT`/`SECRET_TOKEN`/`PRIVATE_KEY`/`CERT` env reads stay exactly as they are — they're simply unused unless `USE_WEBHOOK=1`.

### 2. `docker-compose.yml` (prod)

- Remove `WEBHOOK_LISTEN_HOST`, `WEBHOOK_LISTEN_PORT`, `SECRET_TOKEN`, `PRIVATE_KEY`, `CERT`, `WEBHOOK_URL` from the `quranbot_bot` service's `environment:` block.
- Remove the `ports: - "${WEBHOOK_LISTEN_PORT:-8443}:8443"` mapping — nothing listens by default.
- Do not set `USE_WEBHOOK` (defaults to `'0'` → polling).
- No other service in this file changes.

### 3. `docker-compose.local.yml` (dev)

Dev already runs polling (`APP_ENV=dev`) and never used the webhook vars it happened to set. Remove the dead `WEBHOOK_LISTEN_HOST`, `WEBHOOK_LISTEN_PORT` entries and the `8443:8443` port mapping from the `quranbot_bot` service — pure cleanup, no behavior change.

### 4. `.github/workflows/deploy.yml`

- Remove the `Secret Files/privkey.pem` and `Secret Files/cert.pem` reconstruction lines (`SECRET_FILE_PRIVKEY_PEM`, `SECRET_FILE_CERT_PEM`) from the "Reconstruct Secret Files" step.
- Remove `WEBHOOK_URL`, `SECRET_TOKEN` from the step's `env:` inputs and from the generated `.env` (drop the `ENV_WEBHOOK_URL`, `ENV_SECRET_TOKEN` secret references and the corresponding `printf`/`echo` lines).
- Remove the hardcoded `WEBHOOK_LISTEN_HOST=0.0.0.0`, `WEBHOOK_LISTEN_PORT=8443`, `PRIVATE_KEY=...`, `CERT=...` lines from the generated `.env`.
- Do not write `USE_WEBHOOK` at all (defaults to polling).
- The underlying GitHub Secrets (`SECRET_FILE_PRIVKEY_PEM`, `SECRET_FILE_CERT_PEM`, `ENV_WEBHOOK_URL`, `ENV_SECRET_TOKEN`) are left configured in the repo, untouched — deleting GitHub secrets is a separate, explicit action for the user to take if/when desired, not part of this change.

### 5. Docs — `.env.example`, `Readme.md`, `CLAUDE.md`

- `.env.example`: move `WEBHOOK_URL`, `WEBHOOK_LISTEN_HOST`, `WEBHOOK_LISTEN_PORT`, `SECRET_TOKEN`, `PRIVATE_KEY`, `CERT` into a clearly labeled block: `# ── Webhook mode (optional — only used when USE_WEBHOOK=1) ──`. Add `USE_WEBHOOK=0` near `APP_ENV` with a one-line comment explaining that polling is the default transport in both dev and prod.
- `Readme.md`: update the environment variable table to mark the webhook-related rows as "(webhook mode only)"; add a short "Switching to webhook mode" note: set `USE_WEBHOOK=1`, provide `WEBHOOK_URL`/`SECRET_TOKEN`/`PRIVATE_KEY`/`CERT`, re-add the port mapping in `docker-compose.yml`, and restore the removed `deploy.yml` steps.
- `CLAUDE.md`: update the "Environment Variables" section to mention `USE_WEBHOOK` and that polling is the default.

## Out of Scope

- Deleting GitHub Actions secrets (`SECRET_FILE_PRIVKEY_PEM`, `SECRET_FILE_CERT_PEM`, `ENV_WEBHOOK_URL`, `ENV_SECRET_TOKEN`) — left in place, unused, for the user to remove manually if desired.
- Closing inbound port 8443 on the production host's firewall/security group — an operational step outside the repo, flagged to the user but not performed.
- Any change to the Admin Panel or Backup Service — neither uses webhook/TLS config.
- Rewriting or restructuring `main.py` beyond the single conditional described above.

## Testing / Validation

- `python -c "import main"` (or `uv run python -c "import main"`) to confirm no import/syntax errors after the edit.
- Local run via `uv run python main.py` (or `docker compose -f docker-compose.local.yml up --build`) to confirm the bot starts and polls successfully with the updated env files.
- Manual review of the generated `.env` in `deploy.yml` (e.g. via a dry run or reading the step output) to confirm no webhook vars are written and no missing-secret errors occur now that `ENV_WEBHOOK_URL`/`ENV_SECRET_TOKEN` are no longer referenced.
