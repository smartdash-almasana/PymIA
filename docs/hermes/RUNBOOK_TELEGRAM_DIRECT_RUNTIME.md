# Runbook — Telegram Direct Runtime PymIA

Estado: operativo validado.

Este runbook fija el camino actual para Telegram real de PymIA sin Hermes.

## Decisión

El flujo Telegram-PymIA no usa Hermes gateway, plugins Hermes ni AppData.

Flujo vigente:

```text
@pymIA_bot
-> TELEGRAM_BOT_TOKEN
-> python -m pymia.telegram_bot_runtime
-> pymia.telegram_runtime
-> respuesta PymIA controlada
```

## Bots

| Bot | Variable | Uso |
|---|---|---|
| `@pymIA_bot` | `TELEGRAM_BOT_TOKEN` | Runtime directo PymIA validado |
| `@PymIA_cod_bot` | `TELEGRAM_PYMIA_CODE_BOT` | Otro flujo. No usar para esta prueba |

## Comando live

En PowerShell:

```powershell
cd /d E:\BuenosPasos\smartbridge\PymIA
$env:TELEGRAM_BOT_TOKEN="TOKEN_DE_@pymIA_bot"
python -m pymia.telegram_bot_runtime
```

No pegar tokens en chats, commits ni documentación.

## Prueba canary

Enviar a `@pymIA_bot`:

```text
CANARY_DIRECT_RUNTIME_001 RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

## PASS obligatorio

La respuesta debe contener:

```text
[PymIA:TELEGRAM_RUNTIME]
```

y debe pedir evidencia mínima:

```text
- ventas del periodo
- costos o compras
- gastos fijos
```

Respuesta validada:

```text
[PymIA:TELEGRAM_RUNTIME] Para analizar si estas ganando plata necesito:
- ventas del periodo
- costos o compras
- gastos fijos

Podes subir un Excel con estos datos o indicarme los valores?
```

## FAIL

Cualquier respuesta sin sentinel es inválida para este runtime.

Son señales de ruta incorrecta:

```text
Hermes-Runner
memory
OWL
terminal
skill_view
tools
```

También es inválido probar contra `@PymIA_cod_bot`.

## Prohibido para este flujo

```text
hermes gateway run
hermes plugins
sync AppData
profile pymiafactory como runtime Telegram
OWL
memory generica
tools genericas
```

## Nota sobre token revocado

El token anterior de `@pymIA_bot` fue revocado. El runtime directo debe operar solo con el token nuevo cargado en la variable de entorno `TELEGRAM_BOT_TOKEN`.

## Estado de cierre

Prueba real confirmada:

```text
Telegram real
-> @pymIA_bot
-> token nuevo
-> python -m pymia.telegram_bot_runtime
-> [PymIA:TELEGRAM_RUNTIME]
```
