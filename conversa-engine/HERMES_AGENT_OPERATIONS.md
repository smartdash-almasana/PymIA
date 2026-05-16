# Hermes Agent operations v1

## Operating objective

```text
external channel -> conversa-engine -> pymia.hermes.adapter.HermesAdapter -> result.reply_text -> user
```

## Architectural rule

```text
Hermes conversa.
PymIA computa.
```

## Runtime context

- Local dev OS: Windows 11
- Target runtime OS: Linux VM (GCP)
- PymIA repo local: `E:\BuenosPasos\smartbridge\PymIA`
- PymIA repo VM target: `/opt/smartpyme-factory/repos/PymIA`
- conversa-engine local: `E:\BuenosPasos\smartbridge\PymIA\conversa-engine`
- conversa-engine VM target: `/opt/smartpyme-factory/repos/PymIA/conversa-engine`
- Hermes profile target: `default`
- Preferred provider: Nous Portal
- Fallback provider: OpenRouter owl alfa only if Nous Portal fails

## Boundary

- Hermes Agent runtime is owned by `conversa-engine`.
- `pymia/` must not import Hermes Agent external runtime, Telegram, provider SDKs, LangGraph, SmartPyme or factory code.
- PymIA integration must use the local package import:

```python
from pymia.hermes.adapter import HermesAdapter, HermesInput
```

## Required validation

Windows:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
.\.venv\Scripts\python.exe smoke_test.py
```

Linux VM:

```bash
cd /opt/smartpyme-factory/repos/PymIA/conversa-engine
./.venv/bin/python smoke_test.py
```

Expected:

```text
SMOKE_OK: True
```

## Hermes CLI baseline

Windows:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
.\.venv\Scripts\hermes.exe config
.\.venv\Scripts\hermes.exe config check
.\.venv\Scripts\hermes.exe status
```

Linux VM:

```bash
cd /opt/smartpyme-factory/repos/PymIA/conversa-engine
./.venv/bin/hermes config
./.venv/bin/hermes config check
./.venv/bin/hermes status
```

## Singleton gateway (Windows)

Use this sequence to avoid lock/polling conflicts:

```powershell
# stop any stale/duplicate Hermes gateway process
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'hermes(\.exe)?\s+gateway' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# clear stale lock artifacts for default profile
Remove-Item C:\Users\PC\.hermes\gateway.lock,C:\Users\PC\.hermes\gateway.pid,C:\Users\PC\.hermes\gateway_state.json -Force -ErrorAction SilentlyContinue

# run exactly one gateway
.\.venv\Scripts\hermes.exe gateway run
```

Notes:
- If gateway is already running, do not start a second one.
- `gateway status` may be inconsistent on some Windows setups; prefer `gateway_state.json` and live PID checks.

## Singleton gateway (Linux VM)

```bash
pkill -f "hermes gateway run" || true
rm -f ~/.hermes/gateway.lock ~/.hermes/gateway.pid ~/.hermes/gateway_state.json
cd /opt/smartpyme-factory/repos/PymIA/conversa-engine
./.venv/bin/hermes gateway run
```

## Operational truth checks

```powershell
Get-Content C:\Users\PC\.hermes\gateway_state.json
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'hermes(\.exe)?\s+gateway' } | Select-Object ProcessId,Name,CommandLine
```

Expected `gateway_state.json` core fields:

```text
gateway_state: running
platforms.telegram.state: connected
```

## Provider policy

- Preferred: Nous Portal OAuth (`provider: nous`).
- Preferred model: `deepseek/deepseek-v4-flash`.
- Fallback allowed only if Nous fails: OpenRouter owl alfa.
- Keep provider consistency per active profile before starting gateway.

## Nous Portal setup

Windows:

```powershell
cd E:\BuenosPasos\smartbridge\PymIA\conversa-engine
.\.venv\Scripts\hermes.exe setup
```

During setup:

```text
Provider: Nous Portal
Model: deepseek/deepseek-v4-flash
```

If OAuth is required:

```powershell
.\.venv\Scripts\hermes.exe auth add nous --type oauth
```

Verify:

```powershell
.\.venv\Scripts\hermes.exe status
```

Expected:

```text
Provider: Nous Portal
Model: deepseek/deepseek-v4-flash
Nous Portal: logged in
```

Manual config check, only if needed:

```powershell
.\.venv\Scripts\hermes.exe config edit
```

Expected config keys:

```yaml
model.provider: nous
model.default: deepseek/deepseek-v4-flash
```
