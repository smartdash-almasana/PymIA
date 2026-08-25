# Servicio 1 — Orchestration Chain V1

**Estado:** `AUTHORITATIVE_AGENT_HANDOFF_CHAIN`
**Objetivo:** operación sin usuario intermediario y con Codex como único agente operativo vigente.

## Regla

Codex debe leer la evidencia persistida del ciclo anterior y escribir la evidencia del ciclo actual. Ninguna instrucción ni resultado operativo debe depender de copiar/pegar por chat.

## Cadena vigente

```text
R0/R1
→ evidencia histórica cerrada:
  docs/current/evidence/SERVICE_1_R0_R1_QWEN_VERIFICATION_V1.md

R2
→ cierre: docs/current/evidence/SERVICE_1_R2_CLOSURE_V1.md
→ FINAL_VERDICT = PASS
→ NEXT_ALLOWED_NODE = R3

R3
→ cierre: docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md
→ FINAL_VERDICT = PASS
→ NEXT_ALLOWED_NODE = R4

R4
→ prompt: docs/current/prompts/SERVICE_1_CODEX_R4_IMPLEMENT_V2.md
→ Codex implementa R4 en una sesión focal
→ output: docs/current/evidence/SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md
→ sólo IMPLEMENTATION_VERDICT = PASS habilita una nueva sesión Codex
→ prompt: docs/current/prompts/SERVICE_1_CODEX_R4_VERIFY_V2.md
→ Codex verifica R4 en modo read-only, sin reparar findings
→ output: docs/current/evidence/SERVICE_1_R4_VERIFICATION_EVIDENCE_V2.md
→ sólo FINAL_VERDICT = PASS habilita R4.5

R4.5
→ prompt: docs/current/prompts/SERVICE_1_CODEX_R4_5_INTEGRATION_CHECKPOINT_V1.md
→ Codex ejecuta checkpoint transversal R0–R4 en modo read-only
→ output: docs/current/evidence/SERVICE_1_R4_5_INTEGRATION_CHECKPOINT_V1.md
→ sólo FINAL_VERDICT = PASS habilita R5

R5 en adelante
→ Codex ejecuta el nodo
→ Codex cambia a rol verificador read-only del mismo ciclo
→ Codex persiste un único archivo EXECUTE_VERIFY
→ sólo FINAL_VERDICT = PASS habilita el nodo siguiente
```

Qwen queda fuera de la cadena operativa desde 2026-08-23. Sus archivos anteriores se conservan sólo como evidencia histórica ya emitida; no se generan nuevas dependencias hacia Qwen.

## Política de continuación

- Cada prompt Codex debe depender de evidencia física persistida del nodo anterior.
- Cada ciclo debe separar explícitamente:
  1. fase de ejecución;
  2. fase de verificación read-only;
  3. veredicto final.
- Si la verificación devuelve FAIL, FAIL_NOT_PROVEN o BLOCKED, no avanzar al nodo siguiente.
- La dirección técnica genera el siguiente prompt contra archivos del repo, no contra resúmenes de chat.
- Ningún agente solicita al usuario transportar resultados.
- No full suite salvo checkpoint prescrito.
- No commit, push ni deploy sin autorización explícita.

## Autoridad

Arquitectura:

```text
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
```

Ejecución y cierre:

```text
docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md
docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md
```

## Prohibición

No generar prompts que dependan de contenido existente sólo en chat. Todo dato necesario debe estar persistido en `docs/current/` o ser observable físicamente en el repo.
