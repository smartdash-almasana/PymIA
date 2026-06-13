# P1 — First Report Schema

Estado: VIGENTE

Nota de promoción P1:

```text
READY_FOR_OWNER no equivale a DELIVERED, delivery, aprobación, decisión ni autorización de acción.
```

Esta aclaración incorpora la observación de auditoría externa PASS_WITH_OBSERVATIONS.
Fecha: 2026-06-12
Frente: Diagnóstico inicial y primer informe

## 1. Propósito

Definir el schema conceptual mínimo de `FirstReport`, la devolución owner-facing que traduce un `InitialDiagnosis` en un informe comprensible para el dueño de la PyME.

`FirstReport` no es una decisión, no es una orden de ejecución, no es un delivery operativo y no es una aprobación de acciones.

Su función es devolver claridad fundada, con límites explícitos, a partir de la cadena:

```text
Ficha → Anamnesis → Evidencia → Comprensión → Contraste → Diagnóstico inicial → Primer informe
```

## 2. Fuente obligatoria

`FirstReport` debe originarse desde un `InitialDiagnosis` válido.

No puede originarse directamente desde:

- mensaje libre del dueño;
- variables abstractas;
- fórmulas aisladas;
- patologías no contrastadas;
- memoria conversacional;
- interpretación LLM sin evidencia;
- intuición del operador.

## 3. Schema conceptual mínimo

```yaml
FirstReport:
  report_id: string
  tenant_id: string
  case_id: string
  diagnosis_id: string
  status: DRAFT | READY_FOR_OWNER | BLOCKED
  title: string
  owner_context_summary: string
  declared_symptom_summary: string
  evidence_received: list[EvidenceItem]
  evidence_missing: list[MissingEvidenceItem]
  what_was_understood: string
  what_was_contrasted: list[ContrastItem]
  initial_findings: list[OwnerFacingFinding]
  confidence_limits: list[ConfidenceLimit]
  cannot_claim_yet: list[string]
  suggested_next_evidence: list[NextEvidenceRequest]
  suggested_next_conversation: list[OwnerQuestion]
  first_report_conclusion: string
  trace: ReportTrace
```

## 4. Campos

### 4.1 `report_id`

Identificador único del primer informe.

### 4.2 `tenant_id`

Identidad técnica de aislamiento.

Debe coincidir con el `tenant_id` del diagnóstico inicial.

### 4.3 `case_id`

Identidad del caso operativo.

Debe permitir continuidad del caso.

### 4.4 `diagnosis_id`

Referencia obligatoria al `InitialDiagnosis` que alimenta el informe.

### 4.5 `status`

Estados mínimos:

```text
DRAFT
READY_FOR_OWNER
BLOCKED
```

- `DRAFT`: informe en preparación.
- `READY_FOR_OWNER`: informe apto para devolución al dueño.
- `BLOCKED`: no puede emitirse sin más evidencia o corrección de contexto.

### 4.6 `title`

Título owner-facing, simple y concreto.

Ejemplo:

```text
Primer informe operativo — Caja y ventas de abril
```

### 4.7 `owner_context_summary`

Resumen breve de la PyME y del contexto operativo entendido.

No debe inventar rubro, escala, estructura ni procesos no declarados o no evidenciados.

### 4.8 `declared_symptom_summary`

Resumen del dolor expresado por el dueño, en lenguaje claro.

Ejemplo:

```text
El dueño declaró que vende, pero no logra entender por qué la caja no mejora.
```

### 4.9 `evidence_received`

Lista de evidencia efectivamente recibida.

Cada item debe incluir, como mínimo:

```yaml
EvidenceItem:
  evidence_id: string
  kind: string
  description: string
  period: string | null
  source_ref: string | null
```

### 4.10 `evidence_missing`

Lista de evidencia necesaria pero todavía ausente.

```yaml
MissingEvidenceItem:
  description: string
  why_needed: string
  blocks_claims: list[string]
```

### 4.11 `what_was_understood`

Síntesis de comprensión situada.

Debe explicar qué se entendió del caso antes de emitir hallazgos.

### 4.12 `what_was_contrasted`

Lista de contrastes realizados entre evidencia, hipótesis, taxonomías, fórmulas o criterios.

```yaml
ContrastItem:
  object: string
  evidence_used: list[string]
  result: CONTRASTED | PARTIALLY_CONTRASTED | NOT_CONTRASTED
  summary: string
```

### 4.13 `initial_findings`

Hallazgos comunicables al dueño.

```yaml
OwnerFacingFinding:
  finding_id: string
  title: string
  summary: string
  evidence_refs: list[string]
  severity: INFO | WATCH | ALTERED | CRITICAL
  confidence: LOW | MEDIUM | HIGH
  owner_language: string
```

Regla:

```text
No puede existir finding owner-facing sin evidencia_refs.
```

### 4.14 `confidence_limits`

Límites explícitos de confianza.

```yaml
ConfidenceLimit:
  claim_area: string
  limitation: string
  required_evidence_to_improve: string
```

### 4.15 `cannot_claim_yet`

Afirmaciones que el informe todavía no puede sostener.

Ejemplos:

```text
No puede afirmarse rentabilidad real por producto sin costos completos.
No puede afirmarse faltante de caja sin conciliación bancaria.
```

### 4.16 `suggested_next_evidence`

Evidencia siguiente sugerida para profundizar.

```yaml
NextEvidenceRequest:
  description: string
  reason: string
  expected_use: string
```

### 4.17 `suggested_next_conversation`

Preguntas siguientes al dueño.

No son decisiones. No son acciones aprobadas. Son continuidad de anamnesis/profundización.

```yaml
OwnerQuestion:
  question: string
  reason: string
  related_finding_id: string | null
```

### 4.18 `first_report_conclusion`

Cierre breve del informe.

Debe contener:

- qué se pudo ver;
- qué no se puede afirmar todavía;
- cuál es el próximo paso de evidencia o conversación.

No debe contener:

- decisión aprobada;
- orden de ejecución;
- promesa de resultado;
- recomendación no soportada.

### 4.19 `trace`

Trazabilidad mínima.

```yaml
ReportTrace:
  created_at: string
  created_from: InitialDiagnosis
  source_diagnosis_id: string
  source_evidence_ids: list[string]
  generated_by: string
```

## 5. Prohibiciones

`FirstReport` no puede:

- diagnosticar sin evidencia;
- listar variables universales como punto de partida;
- reemplazar anamnesis;
- reemplazar diagnóstico inicial;
- recomendar acciones ejecutivas sin frontera posterior;
- capturar approval/rejection del dueño;
- crear DecisionRecord;
- abrir OD1;
- abrir C4;
- abrir owner-action pipeline;
- prometer delivery operativo;
- ocultar evidencia faltante.

## 6. Diferencia con `InitialDiagnosis`

```text
InitialDiagnosis = estructura clínica-operacional interna.
FirstReport      = traducción owner-facing del diagnóstico inicial.
```

`FirstReport` debe ser legible para el dueño, pero no debe perder la disciplina de evidencia.

## 7. Diferencia con reporte final o delivery

`FirstReport` no cierra el caso.

Abre una comprensión compartida.

Su resultado natural es:

```text
más evidencia
más preguntas
más contraste
profundización guiada
```

No:

```text
acción aprobada
implementación
automatización
plan cerrado
```

## 8. Ejemplo mínimo

```yaml
report_id: FR-001
tenant_id: tenant_textil_001
case_id: CASE-001
diagnosis_id: DIAG-001
status: READY_FOR_OWNER
title: Primer informe operativo — Caja y margen
owner_context_summary: PyME textil con ventas registradas en Excel y preocupación por caja.
declared_symptom_summary: El dueño declara que vende, pero no logra ver caja disponible.
evidence_received:
  - evidence_id: EV-001
    kind: excel
    description: Ventas abril
    period: abril 2026
    source_ref: ventas_abril.xlsx
evidence_missing:
  - description: Costos completos por producto
    why_needed: Necesarios para estimar margen real.
    blocks_claims:
      - rentabilidad real por producto
what_was_understood: La preocupación principal no es sólo venta, sino relación entre ventas, costos y caja.
what_was_contrasted:
  - object: ventas declaradas contra archivo recibido
    evidence_used: [EV-001]
    result: PARTIALLY_CONTRASTED
    summary: Hay ventas registradas, pero falta costo para margen.
initial_findings:
  - finding_id: F-001
    title: Ventas visibles sin costo suficiente para margen
    summary: El archivo permite ver ventas, pero no permite afirmar rentabilidad.
    evidence_refs: [EV-001]
    severity: WATCH
    confidence: MEDIUM
    owner_language: Se ve movimiento de ventas, pero todavía no alcanza para saber cuánto queda.
confidence_limits:
  - claim_area: margen
    limitation: Falta costo por producto.
    required_evidence_to_improve: Lista de costos o facturas de proveedor.
cannot_claim_yet:
  - No puede afirmarse rentabilidad real por producto.
suggested_next_evidence:
  - description: Lista de costos vigente
    reason: Permite contrastar ventas contra costos.
    expected_use: Calcular margen preliminar.
suggested_next_conversation:
  - question: ¿Los precios del Excel son precios finales cobrados o precios de lista?
    reason: Aclara si las ventas reflejan ingreso real.
    related_finding_id: F-001
first_report_conclusion: Hay ventas observables, pero todavía no hay evidencia suficiente para afirmar margen. El próximo paso es incorporar costos y aclarar precios reales cobrados.
trace:
  created_at: 2026-06-12
  created_from: InitialDiagnosis
  source_diagnosis_id: DIAG-001
  source_evidence_ids: [EV-001]
  generated_by: PymIA
```

## 9. Estado

CANDIDATO.

Este documento define schema conceptual. No autoriza runtime, tests, Pydantic model, owner-action, DecisionRecord ni delivery.
