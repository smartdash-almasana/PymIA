# Estado Actual — PymIA / SmartPyme

## Estado

DOCUMENT_INTELLIGENCE_PHASE2F_M1_CERRADA__PENDIENTE_DECISION_SIGUIENTE

## Situación actual

La línea Document Intelligence + capa clínica inicial avanzó hasta Phase 2F / M1.

M1 cerró el primer encuentro taxonómico en la capa clínica/conversacional, sin abrir runtime externo.

Cadena publicada/local relevante:

```text
08ede6c feat(clinical-context): close phase zero taxonomic identity
79024d1 feat(hermes): transport progressive context through adapter
726901c feat(clinical-context): accept previous progressive context for multi-turn enrichment
75a631a feat(clinical-context): surface progressive tenant context in output
31d9f74 feat(clinical-context): build progressive tenant context from anamnesis
4e5a43b feat(clinical-context): add tenant context to conversational boundary
e145b4b feat(document-intelligence): add phase 1 contracts
```

## Trabajo ya realizado

- Document Intelligence Phase 1 quedó implementada como módulo aislado.
- `TenantClinicalContext` entró al boundary conversacional.
- `ProgressiveTenantClinicalContext` se construye desde anamnesis.
- `progressive_context` se expone en output.
- `previous_progressive_context` puede hacer roundtrip en port/service.
- `HermesAdapter` transporta `previous_progressive_context` y `progressive_context` sin persistir ni interpretar.
- Phase 2F / M1 cerró `FASE_0_IDENTIDAD` en `InitialLaboratoryAnamnesisService`.
- El primer contacto sin taxonomía suficiente abre encuadre taxonómico antes de hipótesis, evidencia o análisis.
- Si el dueño responde con datos del organismo PyME, el contexto progresivo puede completar:
  - `industry_hint`
  - `country_code = "AR"`
  - `taxonomy_phase = "FASE_0_IDENTIDAD"`
- Se evita repetir indefinidamente el embudo taxonómico cuando `previous_progressive_context` ya trae `FASE_0_IDENTIDAD`.
- Checkpoints Phase 2B, 2C, 2D y 2E fueron guardados en `Pymia-memoria/`.

## Validación reciente

Gate M1 ejecutado desde workspace padre:

```powershell
$env:PYTHONPATH='E:\BuenosPasos\smartbridge\PymIA'
python -m pytest PymIA/tests/document_intelligence/test_phase2f_taxonomic_first_contact.py PymIA/tests/services/test_initial_laboratory_anamnesis_service.py PymIA/tests/interfaces/test_conversational_port.py -q --tb=short
```

Resultado reportado:

```text
31 passed in 0.83s
```

## Decisión conceptual vigente

El primer contacto debe respetar este orden:

```text
1. Encuadre taxonómico obligatorio del organismo PyME.
2. Síntomas detectados semántica o computacionalmente.
3. Evidencia/datos necesarios.
4. Análisis posterior.
```

Regla rectora:

```text
El organismo encuadra.
El síntoma orienta.
La evidencia valida.
El análisis viene después.
```

## Restricción inmediata

No avanzar a runtime externo ni abrir M2/M3 sin decisión explícita.

No tocar salvo instrucción explícita:

- `conversa-engine/`
- Telegram runtime real
- `tools/`
- `landing/`
- BEM
- `SchemaInferenceEngine`
- Excel parsing
- `pymia/contracts/evidence_v1.py`
- `pymia/contracts/attachment_lifecycle_v1.py`

## Estado del worktree al cierre de M1

M1 fue commiteado de forma atómica en:

```text
08ede6c feat(clinical-context): close phase zero taxonomic identity
```

El worktree conserva cambios mezclados fuera de scope que no pertenecen a M1:

```text
M conversa-engine/audit_boundary_graph.py
M conversa-engine/main.py
M tests/hermes/test_hermes_adapter.py
M tests/interfaces/test_conversational_port.py
M tests/services/test_initial_laboratory_anamnesis_service.py
M tests/test_structured_evidence_boundary.py
?? .pytest_temp/
?? tests/test_conversa_progressive_context_roundtrip.py
?? tests/test_hermes_boundary_bypasses.py
```

No usar `git add .`.

## Próxima tarea activa

Definir el siguiente paso antes de implementar.

Opciones posibles, no iniciadas:

1. Saneamiento documental: crear checkpoint Phase 2F y/o actualizar índice documental.
2. Limpieza de worktree: clasificar cambios mezclados como conservar, descartar o commitear en frentes separados.
3. Auditoría de cambios fuera de scope sin modificar runtime.

No abrir runtime, M2 ni M3 sin scope cerrado.
