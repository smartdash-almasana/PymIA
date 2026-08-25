# Prompt Codex — Servicio 1 — R4 Implement V2

**Repo:** `E:\BuenosPasos\smartbridge\PymIA-service1-cafeteria`

## Rol y precondición

Actuá como ejecutor de la implementación focal R4. Antes de editar, leer:

1. `docs/current/evidence/SERVICE_1_R3_CLOSURE_V1.md`
2. sección `R4` de `docs/current/SERVICE_1_RECONSTRUCTION_PLAN_V1.md`
3. `docs/current/SERVICE_1_CANONICAL_AXIS.md`
4. `docs/current/SERVICE_1_ARCHITECTURE_LOCK.md`
5. `docs/current/SERVICE_1_COMPLETION_AND_CERTIFICATION_CONTRACT_V1.md`

Continuar sólo si R3 contiene simultáneamente:

```text
STATUS: CLOSED_PASS
FINAL_VERDICT: PASS
NEXT_ALLOWED_NODE: R4
```

Si falta algo, detenerse como `STOP_PRECONDITION` y no modificar runtime/tests.

## Alcance único

Implementar sólo `R4 — ProductExecutionRequest + ProductExecutionRoot + surfaces` del plan.
El resultado debe tener una única raíz productiva con dependencies/ports separados y exactamente estos cuatro commands explícitos:

```text
WorkbookSemanticStartRequest
WorkbookSemanticContinueRequest
WorkbookAnalysisExecuteRequest
SpecializedDomainExecuteRequest
```

Inspeccionar físicamente antes de editar todos los callers del Product Root, callers de `run_service_1_pipeline_v1`, usos de `service_1_request_kind_v1`, switches/kwargs legacy y superficies CLI/Web/HTTP. Migrar sólo los callers productivos necesarios para cerrar R4.

## Límites

- Preservar todo el worktree existente y `_audit/`; no reset, checkout ni restauración masiva.
- No dispatch por shape de kwargs, flags o presencia de campos.
- No dejar `tool_requests` como quinta ruta productiva.
- No crear wrappers, aliases, fallbacks ni compatibility shims nuevos.
- No adelantar R5+: retiro semántico histórico o `sheet1`, R6 provenance D4→F7, R7 matemática/policy, R8 especializados, R9 ResultRead, R10+ cleanup/registry.
- No modificar F7/F8/F9, P7/P8 authority, matemática, Gemma ni owner dialogue salvo el wiring mínimo exigido por R4.
- No full suite, Playwright, smoke, commit, push ni deploy.

## Verificación focal de ejecución

Ejecutar únicamente L0/L1/L2/L3 necesarios para R4, incluyendo el gate focal prescrito en el plan:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_product_pipeline_v1.py \
  tests/smartpyme/test_service_1_request_kind_dispatch_v1.py \
  tests/smartpyme/test_service_1_assisted_web_http_v1.py \
  tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py
```

Agregar sólo syntax/import, architecture guards y regresión acotada de las superficies tocadas. Si un gate falla, diagnosticar y detenerse; no saltar a R5+.

## Evidencia obligatoria

Persistir únicamente:
`docs/current/evidence/SERVICE_1_R4_IMPLEMENTATION_EVIDENCE_V2.md`

Debe registrar HEAD, branch, worktree preservado, archivos R4, callers before/after, comandos, resultados, gates R4 y blockers. Terminar con:

```text
IMPLEMENTATION_VERDICT: PASS | FAIL | BLOCKED
NEXT_ALLOWED_ACTION: CODEX_R4_VERIFY_SEPARATE_SESSION
FULL_SUITE: NOT RUN
COMMIT: NO
PUSH: NO
DEPLOY: NO
```

`NEXT_ALLOWED_ACTION` sólo puede ser `CODEX_R4_VERIFY_SEPARATE_SESSION` si `IMPLEMENTATION_VERDICT: PASS`.

No realizar la verificación adversarial en esta sesión. La verificación pertenece al prompt separado V2.
