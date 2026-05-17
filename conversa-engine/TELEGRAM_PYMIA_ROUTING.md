# Telegram -> PymIA routing validation

## Current observed result

Telegram can trigger Hermes Agent to execute the local PymIA entrypoint:

```bash
cd /opt/PymIA/conversa-engine && ./.venv/bin/python main.py "vendo mucho pero no sé si gano plata"
```

Observed reply contains the PymIA operational signal:

```text
Síntoma registrado: "vendo mucho pero no sé si gano plata"
Hipótesis inicial prioritaria: Tensión de caja
Hipótesis secundarias: Fuga operativa, Margen erosionado
Evidencia requerida: costos, extractos bancarios, lista de precios, movimientos de caja, ventas
```

## Diagnosis

The bridge is functionally reachable, but Hermes still adds conversational framing after the tool result.

## Target

Hermes should call PymIA and return `result.reply_text` without rewriting the operational diagnosis.

## Rule

```text
Hermes conversa.
PymIA computa.
Hermes must not overwrite PymIA's operational result.
```
