# M31P-002 — Solicitud de datos para piloto computable

## Estado

DATA_REQUEST_PENDING

## Origen

Este archivo resuelve operativamente el issue:

```text
#7 — M31-P: cargar primer caso piloto computable
```

No existe todavía caso suficiente para crear un piloto computable.

Por lo tanto, M31P-002 queda como solicitud de datos, no como piloto ejecutado.

## Veredicto de clasificación

```yaml
pilot_id: M31P-002
classification: DATA_REQUEST_PENDING
counts_for_pass_operativo: false
reason: faltan datos mínimos de caso real o realista
```

## Datos mínimos requeridos

Para convertir este pedido en `docs/smartpyme/pilots/M31P-002.md`, completar:

```yaml
pilot_id: M31P-002
tenant_ref:
case_date:
business_type:
case_origin:
owner_problem_statement:
owner_operational_meaning:
received_evidence:
  -
missing_evidence:
  -
protocol_steps_applied:
  - intake
  - evidence_review
  - assisted_analysis
  - output_or_blocking_reason
output_delivered:
final_status:
execution_time_minutes:
operational_cost:
human_intervention:
operator_notes:
blockers:
  -
candidate_learnings:
  -
repeatability_assessment:
limitations:
  -
```

## Preguntas bloqueantes

### 1. Caso / tenant

- ¿Qué referencia anonimizada tendrá el caso?
- ¿Qué fecha corresponde?
- ¿Qué rubro o tipo de PyME es?
- ¿El origen es cliente real, prospecto, demo realista o caso interno?

### 2. Problema declarado

- ¿Qué dijo el dueño PyME?
- ¿Cuál es el dolor económico u operativo concreto?

### 3. Sentido operativo

- ¿Qué período quiere mirar?
- ¿Qué significa la evidencia aportada?
- ¿Qué proceso real hay detrás?
- ¿Qué decisión necesita tomar?

### 4. Evidencia recibida

- ¿Qué archivos, datos o documentos existen?
- ¿Hay Excel, PDF, extractos, facturas, listas de precios, ventas, compras, costos o stock?

### 5. Evidencia faltante

- ¿Qué falta para aplicar el protocolo M31 sin inventar diagnóstico?

### 6. Medición operativa

- ¿Cómo se medirá `execution_time_minutes`?
- ¿Qué valor tendrá `operational_cost` o corresponde `not_applicable`?
- ¿Qué intervención humana se espera?

### 7. Salida o bloqueo

- ¿Se espera entrega, salida parcial, bloqueo o unsupported?
- ¿Cómo se evaluará repetibilidad?

## Restricciones

- No crear `M31P-002.md` hasta tener datos suficientes.
- No declarar PASS_OPERATIVO.
- No abrir M32.
- No tocar código productivo.
- No declarar producto.
- No implementar Guided Evidence Recovery.
- No convertir aprendizajes candidatos en LearningMemory automática.

## Próximo paso

Completar los datos faltantes o mantener M31P-002 como `DATA_REQUEST_PENDING`.
