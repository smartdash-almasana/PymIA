# M35 — Evidence to Core Checkpoint

Fecha original: 2026-06-07
Fecha de reconciliación: 2026-06-08
Estado: CLOSED / RECONCILED
HEAD local reconciliado: `c6d1131`

## Alcance del frente

M35 cerró la transición mínima y determinística:

```text
StructuredEvidence
→ DiagnosticCoreInput
→ DiagnosticCoreV1
```

Sin tocar:

```text
- parser Excel;
- Telegram;
- runtime;
- DiagnosticCoreV1 como frontera de ejecución;
- narrativa para dueño;
- cálculo fuera del core.
```

## Slices certificados

- `M35-S1` cerrado: `StructuredEvidence -> DiagnosticCoreInput`
- `M35-S2` cerrado: `StructuredEvidence -> binder -> DiagnosticCoreV1`
- `M35-S3` cerrado: `source_refs` scoped por fórmula
- `M35-S4` cerrado: fixture Excel -> core sin inventar variables
- `M35-S5` cerrado: evidence binding extendido a fórmulas ya soportadas
- `M35-S6` cerrado: evidence sufficiency report puro por fórmula

## Evidencia usada para el cierre

Evidencia documental y de repositorio:

- `pymia/diagnostic_core/evidence_binding.py`
- `pymia/diagnostic_core/evidence_sufficiency.py`
- `pymia/diagnostic_core/core.py`
- `tests/diagnosticcore/test_evidence_binding.py`
- `tests/diagnosticcore/test_evidence_binding_core_execution.py`
- `tests/diagnosticcore/test_excel_fixture_core_execution.py`
- `tests/diagnosticcore/test_evidence_sufficiency.py`

Evidencia de commits del frente:

- `43624f7 feat(diagnostic-core): extend evidence binding for new formulas`
- `c6d1131 feat(diagnostic-core): add evidence sufficiency report`

Evidencia de validación atribuida:

- usuario/local: `python -m pytest tests/diagnosticcore/test_evidence_sufficiency.py -q -> 5 passed`
- checkpoint previo M35 ya certificaba `S1..S4` como `CLOSED / PASS`
- el repositorio contiene los tests focales de `S5` y `S6` y sus implementaciones asociadas

## Estado real del núcleo al cierre de M35

- `DiagnosticCoreV1` está implementado
- el binding de evidencia está implementado
- el reporte de suficiencia de evidencia está implementado
- `source_refs` están scoped por fórmula
- el frente ya no está en expansión metodológica abierta

## Relación tenant_id / cliente_id

Durante la reconciliación del estado del proyecto se verificó que:

```text
tenant_id = identidad técnica de scope/aislamiento
cliente_id = identidad de negocio
```

No son sinónimos.

La coexistencia explícita entre ambas identidades queda formalizada en los contratos vigentes correspondientes y no modifica el cierre técnico de M35.

Autoridad canónica de esta relación:

```text
ADR-017 — Identity Scope Boundary
```

## Qué queda abierto

Dentro de M35:

```text
nada abierto
```

Fuera de M35:

```text
- la reconciliación documental de contratos/proyecto más allá del núcleo;
- la autorización canónica de un frente nuevo posterior.
```

## Estado de cierre

```text
M35 = CLOSED
```

## Apertura de M36

Al momento de esta reconciliación:

```text
M36 = NOT AUTHORIZED
```

Motivo:

```text
no existe CapabilitySpec canónico de M36
no existe ModuleContract canónico de M36
no existe TaskSpec canónico de M36
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md no autoriza implementación por sí mismo
```
