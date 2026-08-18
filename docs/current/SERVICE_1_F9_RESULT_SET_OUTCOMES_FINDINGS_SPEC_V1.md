# Servicio 1 — F9 ResultSet / Outcomes / Findings Spec v1

**Estado:** FROZEN  
**Alcance:** proyección gobernada de resultados matemáticos F8 a `ResultSetV1`, findings factuales y bounded outcome  
**Fuera de alcance:** nueva matemática, causalidad, severidad/riesgo, recomendaciones, UI, persistencia, delivery, discovery F10 y product root

## Decisión congelada

```text
F8_IS_MATH_EXECUTION_AUTHORITY
F9_IS_RESULT_PROJECTION_AUTHORITY
F9_DOES_NOT_EXECUTE_MATH
F9_DOES_NOT_INFER_CAUSALITY
F9_DOES_NOT_ASSIGN_SEVERITY
F9_DOES_NOT_INFER_FINANCIAL_IMPACT
F9_DOES_NOT_GENERATE_RECOMMENDATIONS
F9_DOES_NOT_AUTHORIZE_DELIVERY
```

F9 consume resultados matemáticos ya ejecutados por F8 y la evidencia preparada F7 necesaria para conservar lineage.

## Flujo

```text
F7 Service1PreparedAnalysisEvidenceV1
+
F8 Service1AnalysisMathResultV1
↓
F9 build_service_1_analysis_result_projection_v1
↓
Service1AnalysisResultSetV1
+
Service1FindingV1[]
+
Service1BoundedAnalysisOutcomeV1
```

No existe camino F9 hacia `FormulaEngineService`, `calculate_math_primitive()` ni otra autoridad matemática.

## ResultSet canónico

`Service1AnalysisResultSetV1` conserva:

```text
case_id
analysis_id
analysis_kind
grain
groups
source_sheet_refs
relationship_refs
applied_filters
provenance
integrity
```

Cada grupo conserva:

```text
group_ref
key
measures
member_row_refs
rank
```

Cada medida conserva:

```text
measure_ref
value
unit
currency_code | None
formula_ref | None
source_refs
```

El `currency_code` sólo puede incorporarse si llega explícitamente a F9 como un código alfabético de tres letras. F9 nunca asume ARS, USD ni otra moneda por tenant, locale o memoria.

## Finding canónico F9

La superficie canónica del camino `AnalysisPlan` es:

```text
Service1FindingV1
```

Campos:

```text
case_id
finding_id
category
analysis_id
group_ref
entity_ref
metric_ref
observed_value
unit
currency_code | None
rank | None
classification | None
severity | None
financial_impact | None
evidence_chain
limitations
provenance
integrity
```

### Identidad

`finding_id` es determinístico respecto del contenido matemático-identitario del finding:

```text
case_id
analysis_id
group_ref
metric_ref
observed_value
unit
formula_ref
rank
```

No usa UUID aleatorio ni estado global.

## Evidence chain

`Service1EvidenceChainV1` conserva:

```text
source_refs
member_row_refs
relationship_refs
formula_ref
math_trace
```

La cadena permite reconstruir qué filas F7, relaciones confirmadas y operaciones matemáticas F8 sostienen la observación.

F9 no crea nuevas relaciones ni recalcula lineage.

## Bounded finding, no diagnóstico

Un `Service1FindingV1` F9 es una observación factual de un resultado gobernado.

Por defecto:

```text
classification = None
severity = None
financial_impact = None
recommendation_generated = False
severity_assigned = False
financial_impact_inferred = False
```

Esto es intencional.

La existencia de un valor, incluso monetario, no autoriza a convertirlo automáticamente en:

```text
impacto financiero
pérdida
oportunidad
riesgo
severidad
causa
recomendación
```

Estas propiedades requieren una política gobernada posterior y evidencia suficiente.

## Financial impact

F9 define `Service1FinancialImpactV1` como contrato tipado futuro:

```text
amount
currency_code
impact_kind
basis_ref
```

Pero el builder F9 **no lo infiere ni lo popula automáticamente**.

Por tanto:

```text
FINANCIAL_IMPACT_FIELD_EXISTS = YES
FINANCIAL_IMPACT_AUTOMATIC_INFERENCE = NO
```

Esto remedia la ausencia contractual señalada por la auditoría sin inventar impacto económico.

## Bounded outcome

`Service1BoundedAnalysisOutcomeV1` agrupa los findings producidos por un análisis y transporta:

```text
outcome_id
analysis_id
finding_refs
limitations
forbidden_claims
provenance
```

Flags obligatorios:

```text
causal_diagnosis_generated = False
recommendations_generated = False
severity_assigned = False
financial_impact_inferred = False
runtime_authorized = False
tool_execution_authorized = False
product_ready = False
delivery_authorized = False
diagnosis_generated = False
analysis_execution_authorized = False
```

## Integridad

F9 introduce `Service1IntegrityDigestV1`.

Implementación:

```text
canonical JSON
sort_keys = True
compact separators
UTF-8
SHA-256
```

Se aplica al payload factual de:

```text
Service1FindingV1
Service1AnalysisResultSetV1
```

Funciones de verificación:

```text
verify_service_1_finding_integrity_v1
verify_service_1_result_set_integrity_v1
```

### Qué garantiza

El digest permite detectar cambios de contenido cuando se conserva el digest original.

### Qué NO garantiza

```text
authenticity_asserted = False
non_repudiation_asserted = False
```

No es HMAC, no contiene secreto y no pretende demostrar identidad del emisor.

La auditoría externa sugería una firma HMAC-SHA256. F9 no adopta una firma criptográfica sin threat model, key management y objetivo de seguridad definidos. La huella SHA-256 actual es únicamente integridad/tamper-evidence de contenido.

## Inmutabilidad

Los envelopes F9 son `@dataclass(frozen=True)` y las estructuras JSON anidadas de evidence/provenance se congelan recursivamente:

```text
mapping → MappingProxyType
list/tuple → tuple
```

`to_dict()` produce una copia JSON-safe sin entregar referencias mutables internas.

Valores numéricos no finitos (`NaN`, `inf`) son rechazados por contrato.

## Drift gates

F9 bloquea antes de proyectar si detecta:

```text
CASE_ID_DRIFT
ANALYSIS_ID_DRIFT
DUPLICATE_PREPARED_GROUP_REF
DUPLICATE_PREPARED_ROW_REF
RESULT_GROUP_NOT_IN_F7
RESULT_GROUP_KEY_DRIFT
RESULT_GROUP_MEMBERSHIP_DRIFT
RESULT_MEASURE_SET_DRIFT
RESULT_MEASURE_IDENTITY_DRIFT
DUPLICATE_RESULT_GROUP_REF
CURRENCY_CODE_INVALID
```

F9 no puede cambiar el grain, los grupos, miembros ni medidas provenientes de F7/F8.

## Relación con H-03 de la auditoría externa

Hallazgo externo:

```text
H-03 ActionableFinding incompleto:
- falta ID
- categoría
- impacto financiero
- matriz/cadena de evidencia
- firma/integridad
```

F9 introduce en el camino canónico `AnalysisPlan`:

```text
finding_id = PASS
category = PASS
financial_impact typed field = PASS
financial_impact automatic inference = FORBIDDEN
structured evidence_chain = PASS
content integrity digest = PASS
cryptographic authenticity signature = NOT_CLAIMED
```

### Legacy

`pymia/smartpyme/finding_projection.py::ActionableFinding` no se modifica en F9.

Se clasifica como:

```text
LEGACY_COMPATIBILITY_FINDING
NOT_F9_CANONICAL_FINDING
```

Por lo tanto:

```text
H03_CANONICAL_ANALYSIS_PATH_REMEDIATION = PASS
LEGACY_ACTIONABLE_FINDING_RETIREMENT = NOT_F9
```

La migración o retiro físico del finding legacy debe hacerse sólo cuando el product wiring consumidor haya migrado a F9; no se rompe compatibilidad silenciosamente en esta fase.

## No hardcode

F9 no contiene reglas por:

```text
cafetería
rubro
retail
consorcio
capability específica
```

Las únicas categorías derivadas son estructurales:

```text
ANALYTICAL_RESULT
RANKED_ANALYTICAL_RESULT
```

No son diagnósticos de negocio.

## Gate F9

```text
TYPED_RESULT_SET = PASS
TYPED_CANONICAL_FINDING = PASS
DETERMINISTIC_FINDING_ID = PASS
EVIDENCE_CHAIN = PASS
RELATIONSHIP_LINEAGE = PASS
FORMULA_LINEAGE = PASS
MATH_TRACE_LINEAGE = PASS
BOUNDED_OUTCOME = PASS

SHA256_CONTENT_INTEGRITY = PASS
AUTHENTICITY_CLAIMED = NO
NON_REPUDIATION_CLAIMED = NO

CLASSIFICATION_INFERRED = NO
SEVERITY_INFERRED = NO
FINANCIAL_IMPACT_INFERRED = NO
RECOMMENDATION_GENERATED = NO
CAUSAL_DIAGNOSIS_GENERATED = NO

NO_MATH_EXECUTION = PASS
NO_PRODUCT_ROOT_CHANGE = REQUIRED
NO_P7_CHANGE = REQUIRED
NO_P8_CHANGE = REQUIRED
NO_F8_CHANGE = REQUIRED
NO_UI_CHANGE = REQUIRED
NO_LEGACY_FINDING_CHANGE = REQUIRED
```

F9 se congela sólo si F0–F8 permanecen verdes y el diff queda limitado a la superficie F9/documentación.
