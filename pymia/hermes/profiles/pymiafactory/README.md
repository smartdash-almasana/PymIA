# pymiafactory Profile

This directory contains the configuration template for the `pymiafactory` Hermes profile.

## Files

- `profile.yaml` — Non-secret configuration (plugin paths, defaults, feature flags)
- `required_env.yaml` — List of required environment variables (secrets)

## Usage

### 1. Validate Configuration (Dry Run)

Check that repo-side sources exist and required env vars are defined:

```bash
python scripts/hermes_sync_profile.py --profile pymiafactory --dry-run
```

### 2. Sync to AppData (Future)

Copy plugin code and config to the Hermes runtime profile:

```bash
python scripts/hermes_sync_profile.py --profile pymiafactory
```

This will:
- Copy `pymia/hermes/plugins/pymia_telegram_bridge/` → `C:\Users\PC\AppData\Local\hermes\profiles\pymiafactory\plugins\pymia-telegram-bridge\`
- Copy `profile.yaml` → `C:\Users\PC\AppData\Local\hermes\profiles\pymiafactory\config\`
- Validate required env vars are present
- Detect drift (uncommitted changes in AppData)
- Abort if drift detected without `--force`

### 3. Set Up Secrets

Create `.env` in the AppData profile directory:

```
C:\Users\PC\AppData\Local\hermes\profiles\pymiafactory\.env
```

With contents:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
SUPERMEMORY_API_KEY=sk_live_...
OPENROUTER_API_KEY=sk-or-...
```

## Architecture

```
Repo (source of truth):
  E:\BuenosPasos\smartbridge\PymIA\pymia\hermes\profiles\pymiafactory\
    profile.yaml
    required_env.yaml

Runtime (AppData):
  C:\Users\PC\AppData\Local\hermes\profiles\pymiafactory\
    config\profile.yaml
    plugins\pymia-telegram-bridge\__init__.py (wrapper)
    .env (secrets, not versioned)
```

## Rollback

To rollback to a previous version:

```bash
git checkout <previous-commit>
python scripts/hermes_sync_profile.py --profile pymiafactory --force
```
