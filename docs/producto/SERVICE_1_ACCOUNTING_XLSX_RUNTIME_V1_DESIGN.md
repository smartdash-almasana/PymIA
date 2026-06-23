# SERVICE_1_ACCOUNTING_XLSX_RUNTIME_V1_DESIGN

VEREDICT:

```text
SERVICE_1_ACCOUNTING_XLSX_RUNTIME_V1_DESIGN: CREATED
```

PURPOSE:

```text
Diseñar la frontera del runtime XLSX contable asistido de Servicio 1.

El runtime, si se implementa después, debe producir un XLSX operativo de revisión a partir de evidencia estructurada declarada.
No produce conciliación definitiva, auditoría, certificación, validación fiscal, cierre contable ni criterio profesional final.
```

POSITIONING:

```text
Servicio 1 = microservicio asistido bajo revisión humana.

Este diseño define un runtime determinístico local para preparar borrador operativo XLSX.
No define motor contable productivo.
No abre APIs, OCR, parser automático, LLM ni chatbot.
```

WHY_THIS_EXISTS:

```text
Servicio 1 ya tiene QA Delivery Checklist, Case Folder Manifest, Delivery Manifest Audit, runbook con edge-case rules y Synthetic XLSX Edge Case Run V2.

Falta estabilizar qué significa XLSX Runtime antes de diseñar Operator Harness V2 o implementar código.
```

SUPPORTED_FAMILIES:

```text
ventas_declaradas_vs_cobros_declarados
compras_declaradas_vs_pagos_declarados
```

UNSUPPORTED_FAMILIES:

```text
bank_api_reconciliation
mercado_pago_api_reconciliation
mercado_libre_api_reconciliation
stock_accounting
fiscal_liquidation
audit_workpaper
certified_reconciliation
automatic_accounting_entries
broad_mixed_case_without_scope_reduction
```

INPUT_CONTRACT:

```text
case_id: required
client_alias: required
case_family: required
period: required
operator: required
human_reviewer: required
accepted_scope: required
rejected_scope: optional
input_tables: required
evidence_manifest: required
visible_differences: optional
evidence_gaps: optional
warnings: optional
stop_conditions: required
forbidden_claims_check: required
next_safe_action: required
```

OUTPUT_CONTRACT:

```text
workbook_type: accounting_xlsx_review_draft
case_id
case_family
period
status
summary_sheet
evidence_declared_sheet
visible_differences_sheet
evidence_gaps_sheet
warnings_sheet
human_review_sheet
limits_sheet
qa_trace_sheet
manifest_trace_sheet
next_safe_action
```

WORKBOOK_REQUIRED_SHEETS:

```text
Resumen
Evidencia declarada
Diferencias visibles
Faltantes de evidencia
Advertencias operativas
Revisión humana
Límites del entregable
QA Trace
Manifest Trace
```

STATUS_VALUES:

```text
READY_FOR_REVIEW_DRAFT
PASS_WITH_WARNINGS
PARTIAL_REVIEW_DRAFT
NEEDS_SCOPE_REDUCTION
NEEDS_HUMAN_REVIEW
BLOCKED_BY_SCOPE
BLOCKED_BY_EVIDENCE
BLOCKED_BY_STOP_CONDITION
BLOCKED_BY_FORBIDDEN_CLAIM
```

EDGE_CASE_BEHAVIOR:

```text
INCOMPLETE_SALES_COLLECTIONS:
- aceptar parcialmente si período y archivos base son claros
- marcar cobros faltantes
- no inventar cobros
- result: PARTIAL_REVIEW_DRAFT

DUPLICATED_COLLECTIONS:
- marcar posibles duplicados
- no netear automáticamente
- requerir revisión humana
- result: PASS_WITH_WARNINGS

MISSING_MASTER_DATA:
- aceptar con advertencias si hay evidencia suficiente
- marcar proveedor, CUIT, fecha, medio o referencia faltante
- result: PASS_WITH_WARNINGS

NEGATIVE_AMOUNTS_AND_CREDIT_NOTES:
- separar ajustes de operaciones normales
- no clasificar automáticamente como pago/cobro ordinario
- result: NEEDS_HUMAN_REVIEW

TOO_BROAD_MIXED_CASE:
- bloquear o pedir reducción de alcance
- no generar workbook amplio
- result: BLOCKED_BY_SCOPE o NEEDS_SCOPE_REDUCTION

NO_TRANSACTION_KEYS:
- permitir sólo vista agregada o pedir columnas mínimas
- no hacer matching fino
- result: NEEDS_SCOPE_REDUCTION
```

FAIL_CLOSED_RULES:

```text
Bloquear generación si:
- falta case_id
- falta período
- falta human_reviewer
- familia no soportada
- alcance demasiado amplio
- falta evidencia mínima
- hay stop condition activa
- forbidden claims no fueron chequeados
- forbidden claims fueron detectados

Permitir borrador con advertencias si:
- faltan llaves pero hay vista agregada posible
- faltan datos maestros pero hay evidencia mínima
- hay duplicados no resueltos
- hay notas de crédito/importes negativos que requieren revisión humana
```

REQUIRED_LANGUAGE:

```text
borrador operativo
evidencia declarada
diferencias visibles
faltantes de evidencia
advertencias operativas
requiere revisión humana
XLSX operativo de revisión
```

FORBIDDEN_LANGUAGE:

```text
auditado
certificado
conciliado definitivamente
validado fiscalmente
exacto
cerrado contablemente
aprobado fiscalmente
reemplaza al contador
garantiza exactitud
listo para presentación fiscal
resultado contable final
```

RELATION_TO_CASE_FOLDER_MANIFEST:

```text
El runtime debe consumir o referenciar el case manifest.
El output debe ser trazable a case_id, manifest, evidencia declarada y next_safe_action.
```

RELATION_TO_DELIVERY_MANIFEST_AUDIT:

```text
El output debe ser auditable por SERVICE_1_DELIVERY_MANIFEST_AUDIT_V1.
No puede pasar a entrega si faltan QA, human reviewer, forbidden claims check o stop_conditions = NONE.
```

RELATION_TO_QA_DELIVERY_CHECKLIST:

```text
El workbook debe exponer datos suficientes para QA:
- evidencia declarada
- diferencias visibles
- faltantes de evidencia
- advertencias operativas
- revisión humana
- límites
- próxima acción segura
```

RELATION_TO_OPERATOR_HARNESS_V2:

```text
Operator Harness V2 debe orquestar piezas ya estabilizadas:
- case folder manifest
- XLSX runtime
- QA checklist
- delivery manifest audit
- owner message
- operator notes

El harness no debe crear nuevas semánticas contables.
```

IMPLEMENTATION_BOUNDARY:

```text
Si se implementa, debe ser determinístico y local.

Permitido:
- validación de input contract
- generación openpyxl
- statuses explícitos
- guardrails fail-closed
- output path provisto por caller

Prohibido:
- APIs externas
- OCR
- parser automático
- LLM
- chatbot
- claims de conciliación definitiva
- clasificación fiscal o contable final
```

TESTING_REQUIREMENTS_IF_IMPLEMENTED:

```text
- workbook contiene hojas requeridas
- bloquea familia no soportada
- bloquea falta de human reviewer
- bloquea stop condition activa
- bloquea forbidden claims
- duplicados salen como warnings
- datos maestros faltantes salen como warnings
- falta de llaves produce scope reduction
- notas de crédito/importes negativos requieren revisión humana
- output preserva lenguaje seguro
- output es auditable por delivery manifest audit
```

PRODUCT_DECISION_REQUIRED:

```text
YES.

Implementar ahora como módulo estable o mantener como protocolo manual/sandbox hasta después de Operator Harness V2 o primer caso real supervisado.
```

RECOMMENDED_DECISION:

```text
Diseñar primero SERVICE_1_OPERATOR_HARNESS_V2.
Luego decidir si el runtime XLSX debe implementarse como módulo.
```

OUT_OF_SCOPE:

```text
conciliación definitiva
auditoría
certificación
validación fiscal
asientos automáticos
APIs bancarias
Mercado Pago API
Mercado Libre API
OCR
parser automático
chatbot libre
Servicio 2
```

NEXT_SAFE_ACTION:

```text
SERVICE_1_OPERATOR_HARNESS_V2_DESIGN
```

COMMIT_READY:

```text
YES
```
