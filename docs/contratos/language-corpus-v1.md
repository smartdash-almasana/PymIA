# Language Corpus V1 — Corpus de Lenguaje Operativo PymIA

## Status

`DRAFT`.

Documento contractual evolutivo.

Implementación mínima existente:

```text
LC-1 contrato documental
LC-2 schema Pydantic
LC-2B guardrails
LC-3 seed mínimo DRAFT
LC-5 integración focal de labels owner-facing en vertical_slice
```

No runtime.
No Pack todavía.
No modifica el kernel.
No habilita diagnóstico, inferencia, acción ni delivery.

---

## Purpose

El Language Corpus V1 define una fuente común, controlada y versionable de lenguaje para el sistema dueño ↔ PymIA.

Su propósito es gobernar la traducción semántica entre:

- lenguaje libre del dueño;
- conceptos operativos PyME;
- evidencia requerida;
- variables computables;
- fórmulas relacionadas;
- patologías candidatas;
- preguntas del agente;
- narrativa owner-facing;
- lenguaje técnico de operador.

Este contrato existe para evitar que cada módulo invente su propio dialecto, sus propias preguntas, sus propias etiquetas o su propia narrativa.

El corpus preserva el sentido operativo sin convertir lenguaje en diagnóstico.

---

## Definition

El Language Corpus V1 es un contrato de traducción semántica controlada, trazable y no diagnóstica.

Mapea expresiones, conceptos, tags y referencias técnicas de forma gobernada, preservando ambigüedad cuando corresponde.

No asume equivalencia uno-a-uno entre una expresión del dueño y un concepto técnico.

Una misma expresión puede apuntar a múltiples conceptos candidatos. Un concepto puede requerir múltiples evidencias. Una fórmula relacionada no implica diagnóstico. Una patología relacionada no implica hallazgo confirmado.

---

## What this contract is not

El Language Corpus V1 no es:

- motor diagnóstico;
- fórmula matemática;
- patología;
- prompt de sistema;
- embedding;
- clasificador automático;
- evidence gate;
- DecisionRecord;
- Pack Runtime;
- KnowledgePack activo;
- ontología total de la PyME;
- sustituto de la confirmación del dueño;
- sustituto de evidencia estructurada;
- sustituto del DiagnosticCoreV1.

No decide.
No calcula.
No confirma findings.
No ejecuta acciones.
No crea evidencia.
No prescribe.

---

## Core responsibilities

El corpus puede:

- traducir lenguaje técnico a lenguaje owner-facing;
- traducir lenguaje técnico a lenguaje de operador;
- normalizar conceptos operativos;
- asociar expresiones del dueño con conceptos candidatos;
- asociar conceptos con tags;
- asociar conceptos con evidencia requerida;
- asociar conceptos con variables computables;
- asociar conceptos con fórmulas relacionadas;
- asociar conceptos con patologías candidatas;
- proveer preguntas permitidas;
- proveer frases permitidas de reporte;
- definir lenguaje prohibido;
- preservar ambigüedad;
- mantener trazabilidad documental mediante `source_refs`.

El corpus no produce verdad operativa por sí mismo. Sólo ayuda a formular, traducir y relacionar.

---

## Hard boundaries

El Language Corpus V1 debe respetar las siguientes fronteras:

```text
Language Corpus ≠ DiagnosticCoreV1
Language Corpus ≠ Evidence Sufficiency
Language Corpus ≠ Formula Engine
Language Corpus ≠ Pathology Engine
Language Corpus ≠ DecisionRecord
Language Corpus ≠ Owner Confirmation
```

Reglas duras:

- no toca `DiagnosticCoreV1`;
- no altera fórmulas;
- no altera evidence sufficiency;
- no confirma findings;
- no crea evidencia;
- no convierte tags en findings;
- no decide acciones;
- no transforma relato del dueño en hecho;
- no restringe el lenguaje libre del dueño;
- no modifica estados universales del sistema;
- no saltea gates;
- no escribe LearningMemory;
- no activa packs.

El dueño puede hablar libremente. El corpus gobierna cómo PymIA interpreta, traduce y responde de manera controlada.

---

## Concept entry model

Una entrada conceptual del Language Corpus V1 debe describirse con estos campos conceptuales.

```yaml
concept_id: string
canonical_label: string
owner_synonyms: list[string]
owner_expression_patterns: list[string]
technical_synonyms: list[string]
tags: list[string]
related_evidence_ids: list[string]
related_variable_ids: list[string]
related_formula_ids: list[string]
related_pathology_ids: list[string]
allowed_owner_questions: list[string]
allowed_report_phrases: list[string]
allowed_operator_language: list[string]
forbidden_language: list[string]
ambiguity_policy: ASK_CLARIFICATION | REQUEST_EVIDENCE | KEEP_CANDIDATE
diagnostic_authority: NONE
version: string
status: DRAFT | ACTIVE | DEPRECATED
source_refs: list[string]
```

### Field notes

`concept_id` must be stable and machine-readable.

`canonical_label` is a human-readable label. It is not diagnostic authority.

`owner_synonyms` and `owner_expression_patterns` are aids for interpretation. They do not create evidence.

`tags` are indices, not findings.

`related_*` fields are references only. They do not execute logic.

`allowed_owner_questions` must be non-diagnostic and non-prescriptive.

`allowed_report_phrases` must preserve uncertainty, evidence limits and candidate status.

`forbidden_language` prevents certainty, alarmism, prescription or unsupported diagnosis.

`diagnostic_authority` must be `NONE`.

`source_refs` are mandatory for governance.

---

## Ambiguity policy

A single owner expression may map to multiple candidate concepts.

Valid outcomes under ambiguity are only:

```text
ASK_CLARIFICATION
REQUEST_EVIDENCE
KEEP_CANDIDATE
```

Invalid outcomes are:

```text
CONFIRM_FINDING
RUN_FORMULA
CREATE_EVIDENCE
CREATE_DECISION_RECORD
PRESCRIBE_ACTION
DIAGNOSE_PATHOLOGY
```

The corpus must preserve ambiguity until evidence, contracts or owner confirmation resolve it through the appropriate implemented gate.

---

## Allowed consumers

The following layers may consume the Language Corpus, subject to explicit implementation contracts:

- local `vertical_slice` report rendering;
- `owner_questions_builder`;
- future `owner_conversation_initial_diagnosis`;
- future `FirstReport`;
- `OwnerFacingReport` rendering;
- evidence recovery wording;
- formula missing-input narration;
- future pathology narrator;
- operator-facing audit explanations.

All consumption must be read-only.

---

## Forbidden consumers and forbidden usage

The following usages are forbidden:

- `DiagnosticCoreV1` depending on owner-facing labels;
- formula engine reading `owner_synonyms`;
- evidence gate deciding by tags;
- DecisionRecord creation from language;
- finding confirmation from corpus entries;
- pathology activation from owner expressions;
- evidence creation from synonyms;
- action authorization from language;
- runtime mutation of corpus entries during a case.

If a component needs truth, it must use evidence and contracts, not corpus language.

---

## Relation to Pack System

Current status:

```text
Internal documentary contract.
Not a Pack.
Not runtime.
```

Future possible status:

```text
LanguagePack
or KnowledgePack extension
or DomainPack language resource
```

A future LanguagePack may extend language by sector, region or operational context, but it must not mutate the kernel.

A future loader must fail closed if a language resource:

- references unknown formula IDs;
- references unknown evidence IDs;
- introduces diagnostic language;
- introduces prescriptive language;
- attempts to define calculations;
- attempts to confirm findings;
- attempts to alter universal states.

Packs may extend language. They may not change authority.

---

## Governance

Each corpus entry must have:

- version;
- status;
- source_refs;
- explicit diagnostic authority set to `NONE`;
- forbidden language constraints.

Allowed lifecycle:

```text
DRAFT → ACTIVE → DEPRECATED
```

An entry may be rejected before activation if it violates this contract.

Growth rules:

- no free vocabulary expansion without source reference;
- no concept without possible evidence relation;
- no synonym that creates evidence;
- no tag that implies finding;
- no report phrase that asserts unsupported certainty;
- no owner-facing phrase that prescribes action;
- no sector-specific expansion without later pack governance.

The corpus grows from observed cases, architectural decisions, contracts or validated operational need.

---

## Safety rules

The Language Corpus must enforce these safety rules:

- no diagnostic language without evidence and authorized diagnostic layer;
- no prescriptive language;
- no certainty without evidence;
- no conversion of owner phrase into fact;
- no hidden inference;
- no substitution of owner confirmation;
- no replacement of evidence sufficiency;
- no claim stronger than the source artifact;
- no owner-facing alarmism;
- no technical ID exposed as primary owner language when a safer phrase exists.

Allowed phrasing pattern:

```text
Falta evidencia para evaluar {concept}.
```

Allowed phrasing pattern:

```text
Con la evidencia disponible, este punto queda como candidato.
```

Forbidden phrasing pattern:

```text
La causa es {concept}.
```

Forbidden phrasing pattern:

```text
Tenés que hacer {action}.
```

---

## Seed concepts, documentary only

The following examples are documentary only.

They are not runtime data.
They are not active corpus entries.
They do not authorize implementation.

### `op_sales_gross`

```yaml
concept_id: op_sales_gross
canonical_label: ventas brutas
owner_synonyms:
  - ventas
  - facturación
  - ingresos por ventas
owner_expression_patterns:
  - referencia libre a cuánto se vendió
technical_synonyms:
  - ventas_total
  - sales_gross
tags:
  - ventas
  - ingresos
  - evidencia_operativa
related_evidence_ids:
  - ventas_periodo
related_variable_ids:
  - ventas_total
related_formula_ids: []
related_pathology_ids: []
allowed_owner_questions:
  - ¿Las ventas informadas corresponden al período que querés analizar?
allowed_report_phrases:
  - Se identificó evidencia relacionada con ventas del período.
allowed_operator_language:
  - variable de ventas brutas detectada
forbidden_language:
  - el negocio vende bien
  - el problema está en las ventas
ambiguity_policy: REQUEST_EVIDENCE
diagnostic_authority: NONE
version: 0.1.0
status: DRAFT
source_refs:
  - language-corpus-v1.md
```

### `op_cost_cogs`

```yaml
concept_id: op_cost_cogs
canonical_label: costo de mercadería vendida
owner_synonyms:
  - costos
  - costo de productos
  - costo de mercadería
owner_expression_patterns:
  - referencia libre a cuánto costó vender o producir
technical_synonyms:
  - costos_total
  - costo_mercaderia_vendida
  - cogs
tags:
  - costos
  - margen
  - evidencia_operativa
related_evidence_ids:
  - costos_periodo
related_variable_ids:
  - costos_total
related_formula_ids: []
related_pathology_ids: []
allowed_owner_questions:
  - ¿Estos costos corresponden a la mercadería o producción del mismo período que las ventas?
allowed_report_phrases:
  - Se identificó evidencia relacionada con costos del período.
allowed_operator_language:
  - variable de costos detectada
forbidden_language:
  - el costo está mal
  - el margen está destruido
ambiguity_policy: ASK_CLARIFICATION
diagnostic_authority: NONE
version: 0.1.0
status: DRAFT
source_refs:
  - language-corpus-v1.md
```

### `op_cash_collection`

```yaml
concept_id: op_cash_collection
canonical_label: cobranzas
owner_synonyms:
  - cobros
  - cobranzas
  - plata cobrada
  - pagos recibidos
owner_expression_patterns:
  - referencia libre a dinero que entró o debería entrar
technical_synonyms:
  - cobranzas_total
  - cash_collection
tags:
  - caja
  - cobranzas
  - liquidez
  - evidencia_operativa
related_evidence_ids:
  - cobranzas_periodo
related_variable_ids:
  - cobranzas_total
related_formula_ids: []
related_pathology_ids: []
allowed_owner_questions:
  - ¿Tenés registro de qué ventas ya fueron cobradas y cuáles siguen pendientes?
allowed_report_phrases:
  - Falta o puede requerirse evidencia de cobranzas para evaluar caja.
allowed_operator_language:
  - evidencia de cobranzas requerida
forbidden_language:
  - no te pagan
  - estás financiando a tus clientes
ambiguity_policy: REQUEST_EVIDENCE
diagnostic_authority: NONE
version: 0.1.0
status: DRAFT
source_refs:
  - language-corpus-v1.md
```

---

## LC-6 — Evolution contract without Pack Runtime

LC-6 defines how the Language Corpus may evolve without contaminating the kernel and without activating runtime pack behavior.

LC-6 is documentary and methodological only.

It does not authorize:

- dynamic corpus loading;
- Pack Runtime;
- seed expansion;
- owner_questions integration;
- DiagnosticCore integration;
- formula execution;
- pathology activation;
- runtime mutation;
- marketplace behavior;
- automatic learning promotion.

### What may evolve

A corpus entry may evolve only in fields that preserve translation, traceability and owner-facing clarity:

```text
owner_label / canonical_label
technical_label / technical_synonyms
owner_synonyms
owner_expression_patterns
related_variable_ids
tags as metadata only
allowed_owner_questions
allowed_report_phrases
allowed_operator_language
forbidden_language
source_refs
version
status
```

Every addition must preserve diagnostic authority as:

```text
diagnostic_authority: NONE
```

### Validation authority

Corpus growth must be validated by an explicit review path.

Allowed validators:

- human operator;
- architectural auditor;
- contract test;
- documentary checkpoint;
- future pack governance, only if separately authorized.

Forbidden validators:

- runtime inference;
- owner-facing narrative alone;
- tags alone;
- owner synonyms alone;
- formula references alone;
- pathology references alone;
- unreviewed model output.

A model may propose candidate language. It may not approve corpus evolution by itself.

### Versioning rule

Every corpus entry must remain versioned and traceable.

Minimum versioning requirements:

```text
concept_id stable
version explicit
status explicit
source_refs mandatory
diagnostic_authority NONE
```

Allowed status lifecycle:

```text
DRAFT → ACTIVE → DEPRECATED
```

No entry becomes ACTIVE without review evidence.

No entry may be silently overwritten during case execution.

### Fail-closed rule

Language Corpus must fail closed.

Required behavior:

- unknown `concept_id` returns raw ID;
- unknown `variable_id` returns raw ID;
- invalid corpus entry is rejected or ignored;
- incomplete corpus does not diagnose;
- missing label does not invent wording;
- forbidden language blocks the entry or phrase;
- ambiguous owner expression remains candidate until clarification, evidence or an implemented gate resolves it.

Fail-closed means the system may be less fluent, but never more authoritative than the evidence allows.

### Kernel anti-contamination rule

The corpus must never introduce domain knowledge directly into the kernel.

Forbidden patterns:

- hardcoding sectorial language in kernel modules;
- using `tags` as findings;
- using `owner_synonyms` as evidence;
- using `related_pathology_ids` as diagnosis;
- using `related_formula_ids` as formula execution trigger;
- mutating DiagnosticCore behavior through corpus entries;
- changing evidence sufficiency through labels;
- changing universal states through language;
- creating DecisionRecord from language.

Permitted pattern:

```text
kernel loads or receives valid language metadata
→ rendering layer translates known IDs
→ unknown IDs remain raw
→ diagnostic authority remains elsewhere
```

### Relation to future packs

Future packs may extend the corpus only through a separate approved contract.

Possible future extensions:

```text
LanguagePack
DomainPack language resource
SectorPack language resource
CatalogPack language resource
```

LC-6 does not activate those packs.

Until Pack Runtime exists under its own ADR, contract and tests, all corpus evolution remains static, reviewed and fail-closed.

### Explicitly out of scope

LC-6 excludes:

- Pack Runtime;
- dynamic pack loader;
- marketplace;
- runtime pack validation;
- seed expansion;
- DiagnosticCore coupling;
- owner_questions coupling;
- formula engine coupling;
- pathology engine coupling;
- LearningMemory writes;
- automatic promotion from observed conversations;
- database persistence;
- UI or delivery changes.

---

## Acceptance criteria for next implementation slice

The next implementation slice may only open after this contract is approved.

Minimum acceptance criteria for the next slice:

- Pydantic schema validates the concept entry structure;
- seed data loads exactly three draft concepts;
- forbidden language validation exists;
- unknown `concept_id` fails closed or returns the raw ID without inventing labels;
- no imports from `DiagnosticCoreV1`;
- no dependency from formula engine to corpus;
- no conversion of tags into findings;
- no conversion of owner expressions into evidence;
- no runtime mutation during case execution.

---

## Stop conditions

Stop if any proposed implementation:

- lets the corpus diagnose;
- uses corpus entries for evidence sufficiency;
- couples corpus to DiagnosticCoreV1;
- grows concepts without `source_refs`;
- replaces owner confirmation;
- turns tags into findings;
- turns owner expressions into facts;
- creates DecisionRecord from language;
- introduces prescriptive owner-facing language;
- opens Pack Runtime before this contract is validated.

---

## Next allowed step

After LC-6 documentary approval, the next allowed step is not implementation by default.

Allowed next methodological step:

```text
Close LC-6 with a documentary checkpoint and external/focal audit.
```

Any future implementation must require a separate TaskSpec and must not integrate runtime, core, packs, UI, owner conversation, DiagnosticCore or owner_questions unless separately authorized.
