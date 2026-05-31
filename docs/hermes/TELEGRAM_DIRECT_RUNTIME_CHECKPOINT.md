# Telegram Direct Runtime Checkpoint

Fecha: 2026-05-28
Estado: PASS OPERATIVO

## Resumen

El frente Telegram-PymIA dejo de depender de Hermes como runtime de entrada.

El camino operativo validado es:

```text
@pymIA_bot
-> TELEGRAM_BOT_TOKEN
-> python -m pymia.telegram_bot_runtime
-> pymia.telegram_runtime
-> respuesta con [PymIA:TELEGRAM_RUNTIME]
```

Hermes queda fuera del path Telegram-PymIA.

## Commits relevantes

```text
a239ca4 feat(telegram): add direct PymIA runtime without Hermes
96dd02d docs(telegram): document direct PymIA runtime runbook
9ec99fa feat(telegram): receive documents in direct PymIA runtime
4ba04fe feat(telegram): add temporary Excel structural summary
a5b990e docs(telegram): mark Excel summary as structural preview
```

## Bots

```text
@pymIA_bot      -> TELEGRAM_BOT_TOKEN      -> runtime directo PymIA
@PymIA_cod_bot  -> TELEGRAM_PYMIA_CODE_BOT -> otro flujo; no usar para validar este runtime
```

## Evidencia operativa validada

### Texto real

Mensaje enviado a `@pymIA_bot`:

```text
CANARY_DIRECT_RUNTIME_001 RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY
```

Respuesta PASS:

```text
[PymIA:TELEGRAM_RUNTIME] Para analizar si estas ganando plata necesito:
- ventas del periodo
- costos o compras
- gastos fijos

Podes subir un Excel con estos datos o indicarme los valores?
```

### Documento real

Archivo enviado a `@pymIA_bot`:

```text
la_textil_cosida_srl_mar_abr_may_2026 (1).xlsx
```

Respuesta PASS:

```text
[PymIA:TELEGRAM_RUNTIME] Documento recibido: la_textil_cosida_srl_mar_abr_may_2026 (1).xlsx. Ya lo guarde y podes pedirme el analisis cuando quieras.
```

### Preview estructural temporal

Pedido:

```text
analiza el excel
```

Resultado actual:

```text
[PymIA:TELEGRAM_RUNTIME] Resumen estructural del Excel:
Archivo: ...xlsx
Hojas: ...
- Hoja 'ventas': rows=..., cols=..., empty=no
  Columns preview: ...
```

Este output es `STRUCTURAL_PREVIEW_ONLY`.

## Decision clave

`pymia.telegram_excel_summary` es temporal y solo puede describir estructura del archivo.

No es diagnostico financiero.
No reemplaza `excel_diagnostic`.
No reemplaza `microservice_dispatcher.dispatch_candidate(...)`.

## Ruta futura correcta

El diagnostico real debe pasar por:

```text
pymia.smartpyme.microservice_dispatcher.dispatch_candidate(
    candidate,
    evidence_path=archivo_excel,
    output_dir=...
)
```

con:

```text
runtime_classification = excel_diagnostic
status = READY_TO_EXECUTE
```

## Prohibiciones vigentes

```text
- No usar hermes gateway para Telegram-PymIA.
- No volver a sync AppData para este flujo.
- No usar profile pymiafactory como runtime Telegram productivo.
- No usar OWL, memory generica, terminal, skill_view ni tools genericas.
- No crear otro parser Excel paralelo.
- No llamar diagnostico real desde Telegram fuera del dispatcher.
- No hacer claims de rentabilidad desde structural preview.
```

## Criterio PASS futuro

Cualquier respuesta del runtime directo debe contener:

```text
[PymIA:TELEGRAM_RUNTIME]
```

Cualquier respuesta sin sentinel es ruta incorrecta o proceso ajeno.
