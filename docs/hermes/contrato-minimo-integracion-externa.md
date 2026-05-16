# Contrato mínimo de integración externa — Hermes ↔ Telegram ↔ PymIA

Contexto heredado. Este documento no autoriza jobs, workflows, orquestación, authorization flow, factory, app.*, MCP legacy ni runtime Hermes duplicado dentro de PymIA. Rige `../../ARCHITECTURE_GUARDRAILS.md`.

## Estado

Contrato operativo mínimo — MVP conversacional externo.

## Objetivo

Definir el contrato mínimo para conectar:

```text
Telegram
→ Hermes externo
→ provider IA externo (opcional)
→ HermesAdapter
→ ClinicalConversationalPort
→ kernel clínico PymIA
```

sin contaminar el core clínico de PymIA.

## Regla rectora

```text
Hermes conversa.
PymIA computa.
```

## Arquitectura mínima permitida

```text
Telegram Bot Runtime (externo)
→ Hermes Runtime (externo)
→ HermesAdapter.handle(HermesInput)
→ ClinicalConversationalPort.handle(ConversationalInput)
→ InitialLaboratoryAnamnesisService
→ AdmissionPipelineV1
→ AdmissionResponseFormatterV1
→ HermesOutput
→ Hermes Runtime
→ Telegram
```

## Boundary obligatorio

PymIA solo acepta:

```text
tenant_id
channel
text
```

Toda metadata externa:

```text
message_id
chat_id
telegram_user_id
session_id
provider_metadata
trace_id
```

es opaca para el kernel clínico.

## Contrato HermesInput

Hermes externo debe construir:

```python
HermesInput(
    tenant_id="tenant-001",
    channel="telegram",
    message_text="vendo mucho pero no sé si gano plata",
    metadata={
        "telegram_chat_id": 123,
        "telegram_message_id": 456,
        "provider": "deepseek",
    },
)
```

## Contrato HermesOutput

PymIA devuelve:

```text
status
mode
reply_text
payload
```

Hermes externo:

- puede enviar `reply_text` al usuario;
- puede loguear `payload`;
- NO puede interpretar `payload` como orden de ejecución.

## Regla para providers IA

Providers IA externos pueden:

- reformular preguntas;
- sostener conversación;
- pedir contexto;
- resumir mensajes;
- traducir lenguaje informal.

Providers IA externos NO pueden:

- decidir hipótesis clínicas;
- crear findings;
- alterar output.message;
- alterar anamnesis;
- alterar laboratorio;
- crear jobs;
- crear workflows;
- crear authorization flows.

La verdad operacional sigue en el kernel PymIA.

## Regla para Telegram

Telegram es solamente canal.

Telegram NO:

- decide modo clínico;
- interpreta hipótesis;
- dispara workflows;
- crea jobs;
- persiste verdad operacional.

## Regla para BEM/OCR

BEM/OCR viven fuera del core PymIA.

Pueden:

- transformar documentos;
- extraer evidencia;
- estructurar datos.

No pueden:

- decidir hipótesis;
- cerrar diagnóstico;
- mutar contratos clínicos.

## Contrato de integración permitido hoy

El runtime externo debe consumir exclusivamente:

```text
pymia.hermes.adapter.HermesAdapter
pymia.hermes.adapter.HermesInput
pymia.hermes.adapter.HermesOutput
```

No debe importar internamente:

```text
pipeline.admission
heuristics
response_formatter
services.initial_laboratory_anamnesis_service
```

## Flujo mínimo de demo Telegram

```text
Telegram recibe mensaje
→ Hermes externo recibe update
→ Hermes externo crea HermesInput
→ HermesAdapter.handle()
→ HermesOutput.reply_text
→ Hermes externo responde por Telegram
```

## Invariantes

```text
PymIA no conoce Telegram.
PymIA no conoce providers IA.
PymIA no conoce BEM.
PymIA no conoce OCR.
PymIA no conoce orchestration.
PymIA no conoce jobs.
```

## Validación requerida

Cada cambio sobre esta frontera debe cerrar con:

```text
pytest -q
check_forbidden_terms(PymIA)
audit_docs_index(PymIA)
run_pymia_demo(..., PymIA)
```
