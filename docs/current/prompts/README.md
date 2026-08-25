# Servicio 1 — Prompts operativos vigentes

**Estado:** `CURRENT_PROMPT_INDEX`
**Fecha:** 2026-08-23

## Agente operativo vigente

```text
CODEX ONLY
```

Qwen ya no forma parte de la cadena operativa. Sus evidencias anteriores se conservan únicamente como evidencia histórica emitida.

## Estado actual

```text
R0/R1 = CLOSED_PASS
R2 = CLOSED_PASS
R3 = CLOSED_PASS
R4 = CLOSED_PASS
R4_5_INTEGRATION_CHECKPOINT_V1 = FAIL_INTEGRATION_CHECKPOINT
NEXT_ALLOWED_ACTION = R4_5_STALE_CLI_TEST_REPAIR
R5 = BLOCKED
```

## Prompts vigentes

Secuencia vigente:

1. `SERVICE_1_CODEX_R4_5_REPAIR_STALE_CLI_TEST_V1.md` — reparación focal del único test stale detectado por R4.5; no runtime.
2. `SERVICE_1_CODEX_R4_5_INTEGRATION_CHECKPOINT_RETRY_V2.md` — nueva sesión read-only; sólo un PASS aquí habilita R5.

R4 implementación/verificación ya están cerrados PASS. `SERVICE_1_CODEX_R4_5_INTEGRATION_CHECKPOINT_V1.md` queda como evidencia del primer checkpoint fallido y no debe reutilizarse para el retry.

`SERVICE_1_CODEX_R4_EXECUTE_AND_VERIFY_V1.md` queda retirado y no debe ejecutarse.

## Cadena

Leer:

`SERVICE_1_ORCHESTRATION_CHAIN_V1.md`

## Autoridad de operación

- `../SERVICE_1_AGENT_OPERATING_INSTRUCTIONS_V1.md`
- `../SERVICE_1_IMPLEMENTATION_HANDOFF_V1.md`
- `../SERVICE_1_RECONSTRUCTION_PLAN_V1.md`
- `../SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`

No reconstruir prompts desde chats ni documentos históricos.
No full suite fuera de los checkpoints prescritos.
No commit, push ni deploy sin autorización explícita del usuario.
