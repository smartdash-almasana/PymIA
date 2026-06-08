# ADR-017 — Identity Scope Boundary: `tenant_id` and `cliente_id`

## Status

Accepted

## Fecha

2026-06-08

## Dueño conceptual

Kernel PymIA / Contract Governance

---

## Context

El repositorio auditado muestra una deriva contractual real sobre identidad:

```text
Código reciente del kernel y del diagnostic core usa tenant_id
↓
StructuredEvidence
DiagnosticCoreInput
DiagnosticCoreResult
PrimaryContextRecord
SCN render / verifier
KnowledgeItem
```

Al mismo tiempo, otros contratos del repositorio usan `cliente_id`:

```text
PathologyEvaluationInput
PathologyFinding
DiagnosticReport
Evidence Chain Contract V1
Owner Decision Contract V1
```

La deriva no puede resolverse tratando ambos campos como sinónimos automáticos, porque el repositorio no los usa de la misma manera.

Además:

- `ADR-006` fija `TenantClinicalContext` y contratos del kernel tenant-scoped.
- `ADR-010` fija contratos conversacionales y de anamnesis también tenant-scoped.
- `docs/contratos/contratos-clinicos-operacionales.md` ya combina en algunos contratos identidad técnica y de negocio.

Sin una decisión explícita, el repositorio mantiene dos problemas:

1. contradicción normativa entre contratos `VIGENTE`;
2. incertidumbre sobre qué identidad debe usarse en cada frontera.

---

## Decision

Se congelan los significados canónicos:

### 1. `tenant_id`

`tenant_id` es la identidad técnica de scope y aislamiento.

Debe usarse cuando el contrato o módulo necesite:

- partición de contexto;
- aislamiento entre tenants;
- trazabilidad técnica entre componentes;
- storage o memoria tenant-scoped;
- ejecución de kernel o gates con frontera técnica explícita.

### 2. `cliente_id`

`cliente_id` es la identidad de negocio del cliente.

Debe usarse cuando el contrato o módulo necesite:

- referencia al cliente en sentido comercial u organizacional;
- ownership de decisiones;
- reporting de negocio;
- artefactos donde la identidad de negocio sea obligatoria aunque la frontera técnica no lo sea.

### 3. Relación entre ambos

`tenant_id` y `cliente_id`:

- no son sinónimos obligatorios;
- pueden coincidir en implementaciones simples;
- pueden coexistir en un mismo contrato si la frontera requiere identidad técnica y de negocio;
- no deben mapearse automáticamente uno al otro sin contrato explícito.

### 4. Regla de uso

Cuando un contrato modele frontera técnica del kernel, la identidad mínima esperada es `tenant_id`.

Cuando un contrato modele ownership o semántica de negocio del cliente, la identidad mínima esperada es `cliente_id`.

Cuando un contrato conecte ambas fronteras, puede requerir ambos campos.

---

## Consequences

### Positivas

- elimina la contradicción normativa central del frente M35 closure/reconciliation;
- alinea el código vigente del kernel con sus ADRs rectoras;
- preserva contratos de negocio sin forzar renombres artificiales;
- permite auditar discrepancias futuras como errores de frontera, no como ambigüedad semántica.

### Negativas / costos

- algunos contratos deberán explicitar si usan identidad técnica, identidad de negocio o ambas;
- la coexistencia aumenta precisión semántica, pero exige disciplina documental.

---

## Rules Introduced

1. Ningún contrato `VIGENTE` debe volver a declarar que `tenant_id` y `cliente_id` son sinónimos automáticos.
2. Ningún contrato `VIGENTE` debe prohibir uno de los campos sólo por convención histórica si la frontera auditada exige el otro.
3. Los contratos y checkpoints del frente `M35_CLOSURE_AND_PROJECT_STATE_RECONCILIATION` deben referenciar esta ADR al tratar identidad.
4. La existencia de `cliente_id` no autoriza reemplazar `tenant_id` en el kernel técnico ya implementado.
5. La existencia de `tenant_id` no elimina la necesidad de `cliente_id` en contratos de negocio o decisión.

---

## Evidence Basis

Código auditado:

- `pymia/contracts/evidence_v1.py`
- `pymia/contracts/primary_context_v1.py`
- `pymia/diagnostic_core/models.py`
- `pymia/diagnostic_core/evidence_binding.py`
- `pymia/diagnostic_core/evidence_sufficiency.py`
- `pymia/diagnostic_core/core.py`
- `pymia/contracts/scn_render_contract.py`
- `pymia/contracts/scn_operational_audit_verifier.py`
- `pymia/domain/entities/knowledge_item.py`
- `pymia/contracts/pathology_contract.py`
- `pymia/contracts/diagnostic_report_contract.py`

Documentos vigentes auditados:

- `docs/adr/ADR-006-tenant-clinical-context-as-input.md`
- `docs/adr/ADR-010-conversational-anamnesis-contract.md`
- `docs/contratos/contratos-clinicos-operacionales.md`
- `docs/contratos/evidence-chain-v1.md`
- `docs/contratos/owner-decision-v1.md`

---

## Not Authorized By This ADR

Esta ADR no autoriza:

- cambios de comportamiento en runtime;
- refactor productivo de código;
- renombres masivos de campos en Python;
- apertura de `M36`;
- cambios en Telegram, parser Excel o integrations.

Su alcance es contractual y de gobernanza documental.
