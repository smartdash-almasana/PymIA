# Service 1 CASE_001 Online Owner Column Reentry Mapping V1

Status: DOCUMENTARY_MAPPING
Date: 2026-07-10
Scope: CASE_001 column-confirmation questions to owner online reentry.

## Verdict

CASE_001 has a certified owner-question source, but online owner column reentry is **not yet certified for this specific packet**.

This document maps the 12 column-confirmation questions into the existing Servicio 1 reentry primitives as a candidate wiring plan. It does not implement code, does not execute runtime, and does not authorize computation/dry-run.

## Certified current state

- `XLSX_PHYSICAL_E2E_OFFICIAL_ENTRYPOINT`: `PASS_WITH_LIMITS`.
- `CASE_001_FINAL_STATE`: `NEEDS_OWNER_INPUT`.
- Owner column confirmation packet exists and is committed at `51e57b5`.
- The PyME owner, not the operator, must provide column meanings.
- Existing operator CLI exposes `--question-bundle`, `--question-ref`, `--owner-answer`, and `--owner-reentry-storage-dir` primitives.
- Existing question bundle schema supports `SOURCE_COLUMN_CONFIRMATION = "column_confirmation_matrix"` and `ANSWER_TYPE_CONFIRM_COLUMN_ROLE = "confirm_column_role"`.
- Existing reentry projection can project pending/answered questions from a `Service1QuestionBundleV1` plus `Service1CaseReentryReadModelV1`.
- Existing operator CLI accepts `--confirmed-columns` for a later re-run, but a controlled CASE_001 conversion from online answers to confirmed-columns JSON is not certified here.

## Not certified by this document

- Online UI integration for this exact CASE_001 packet.
- Automatic conversion from owner online answers into `confirmed-columns.json`.
- CASE_001 re-run after online answers.
- Computation/dry-run, real runner, SaaS runtime, API/storage/worker, autonomous delivery, or final diagnosis.

## Source-to-target mapping

| Layer | Artifact / primitive | Status for CASE_001 | Notes |
|---|---|---|---|
| Source artifact | `column_confirmation_packet.json` | Certified input | 12 required owner questions; `runtime_authorized: false`. |
| Owner-facing packet | `docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATION_PACKET_V1.md` | Certified documentation | Transcribes the 12 questions and response template. |
| Online reentry target | `Service1QuestionBundleV1` / `Service1CaseReentryReadModelV1` / `project_service_1_reentry_v1` | Candidate mapping only | Primitives exist; CASE_001 packet-to-online bundle wiring is not yet certified. |
| Owner answer capture | CLI primitives `--question-bundle`, `--question-ref`, `--owner-answer`, `--owner-reentry-storage-dir` | Primitive exists | This is not the final online UX; it proves the answer-binding shape. |
| Output target | controlled `confirmed-columns.json` | Gap | Must be derived only from validated owner answers. Do not create it yet. |
| Next executable step | re-run CASE_001 with `--confirmed-columns` | Blocked | Allowed only after validated owner answers and controlled confirmed-columns artifact exist. |

## Candidate question-bundle shape

The existing schema suggests this candidate mapping:

```text
source: column_confirmation_matrix
answer_type: confirm_column_role
target_ref: case_001:<sheet_name>:<column_name>
question_ref: service_1:column_confirmation_matrix:case_001_<sheet_name>_<column_name>
required: true
status: PENDING
runtime_authorized: false
owner_confirmation_required: true
```

This is a candidate mapping because no TaskSpec/evidence currently proves this CASE_001 `column_confirmation_packet.json` can be ingested online as-is.

## Question mapping

| # | source question_id | sheet/table | column | owner-facing question | candidate online question_ref | answer type | validation requirement |
|---|---|---|---|---|---|---|---|
| 1 | `col_confirm_001` | `Ventas_Junio_2026` | `fecha` | ¿Qué representa la columna 'fecha' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_fecha` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 2 | `col_confirm_002` | `Ventas_Junio_2026` | `comprobante` | ¿Qué representa la columna 'comprobante' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_comprobante` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 3 | `col_confirm_003` | `Ventas_Junio_2026` | `producto_codigo` | ¿Qué representa la columna 'producto_codigo' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_producto_codigo` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 4 | `col_confirm_004` | `Ventas_Junio_2026` | `producto` | ¿Qué representa la columna 'producto' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_producto` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 5 | `col_confirm_005` | `Ventas_Junio_2026` | `categoria` | ¿Qué representa la columna 'categoria' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_categoria` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 6 | `col_confirm_006` | `Ventas_Junio_2026` | `cantidad` | ¿Qué representa la columna 'cantidad' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_cantidad` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 7 | `col_confirm_007` | `Ventas_Junio_2026` | `precio_unitario` | ¿Qué representa la columna 'precio_unitario' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_precio_unitario` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 8 | `col_confirm_008` | `Ventas_Junio_2026` | `costo_unitario` | ¿Qué representa la columna 'costo_unitario' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_costo_unitario` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 9 | `col_confirm_009` | `Ventas_Junio_2026` | `canal` | ¿Qué representa la columna 'canal' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_canal` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 10 | `col_confirm_010` | `Ventas_Junio_2026` | `venta_total` | ¿Qué representa la columna 'venta_total' en la hoja 'Ventas_Junio_2026'? | `service_1:column_confirmation_matrix:case_001_ventas_junio_2026_venta_total` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 11 | `col_confirm_011` | `README` | `CASO` | ¿Qué representa la columna 'CASO' en la hoja 'README'? | `service_1:column_confirmation_matrix:case_001_readme_caso` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |
| 12 | `col_confirm_012` | `README` | `CASE_001_MARGIN_LEAK_MISSING_COSTS` | ¿Qué representa la columna 'CASE_001_MARGIN_LEAK_MISSING_COSTS' en la hoja 'README'? | `service_1:column_confirmation_matrix:case_001_readme_case_001_margin_leak_missing_costs` | `confirm_column_role` | Owner answer must explicitly define the column meaning; blank, circular, or ambiguous answers keep CASE_001 in `NEEDS_OWNER_INPUT`. |

## Certified vs candidate vs gap

| Category | Items |
|---|---|
| Documented/certified today | CASE_001 physical XLSX intake/folder evidence is `PASS_WITH_LIMITS`; CASE_001 is `NEEDS_OWNER_INPUT`; 12 owner questions exist; owner-facing confirmation packet is committed at `51e57b5`; reentry/question-bundle primitives exist in code. |
| Candidate mapping | Convert each column-confirmation question into a `Service1QuestionV1` with `source=column_confirmation_matrix`, `answer_type=confirm_column_role`, and a stable `question_ref` derived from sheet + column. |
| Gap / not certified yet | CASE_001-specific online ingestion of this packet, online owner UX, answer validation rules, conversion to `confirmed-columns.json`, and re-run evidence. |

## Stop conditions

- No manual operator-invented answers.
- No `confirmed-columns.json` until owner answers are captured and validated.
- No computation/dry-run before validated owner answers.
- No real runner, SaaS runtime, API/storage/worker, or autonomous delivery.
- No final diagnosis or product-ready claim.
- No second XLSX parser.
- No claim that online CASE_001 owner reentry is certified until a TaskSpec and evidence prove it.

## Next methodological step

Run a focused audit of whether the existing online/reentry primitives can ingest this packet as-is:

```text
column_confirmation_packet.json
-> Service1QuestionBundleV1(candidate)
-> owner_answer reentry
-> projection of answered/pending questions
-> controlled confirmed-columns.json candidate
```

If the audit proves existing primitives are enough, create a TaskSpec for CASE_001 online owner column reentry wiring.

If the audit finds a missing boundary or contract, create the required ADR / CapabilitySpec / ModuleContract before code.

## Files inspected for this mapping

- `docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md`
- `docs/current/SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_V1.md`
- `docs/current/SERVICE_1_CASE_001_OWNER_COLUMN_CONFIRMATION_PACKET_V1.md`
- `docs/current/S1_SAAS_RUNTIME_BOUNDARY_CONTRACTS_V1.md`
- `PymIA-Live/pymia/cli/service_1_operator.py`
- `PymIA-Live/pymia/smartpyme/service_1_question_bundle_v1.py`
- `PymIA-Live/pymia/smartpyme/service_1_case_reentry_read_model_v1.py`
- `PymIA-Live/pymia/smartpyme/service_1_reentry_projection_v1.py`
- `C:\Users\PC\AppData\Local\Temp\opencode\case001_run\.tmp\service_1_cases\case_asset_a7e85d9a7ed2\column_confirmation_packet.json`
