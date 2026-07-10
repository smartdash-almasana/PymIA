# Service 1 CASE_001 Owner Column Confirmation Packet V1

Status: OWNER_CONFIRMATION_PACKET
Date: 2026-07-10
Scope: CASE_001 owner column meaning confirmations.

## Certified context

- CASE_001 physical XLSX E2E is `PASS_WITH_LIMITS`.
- CASE_001 final state is `NEEDS_OWNER_INPUT`.
- No computation / dry-run has been executed.
- No runner, SaaS runtime, API / storage / worker, autonomous delivery, or final diagnosis is authorized.
- Source XLSX: `CASE_001_ventas_junio_2026_margin_leak.xlsx`.
- Case id produced by the operator CLI: `case_asset_a7e85d9a7ed2`.

Governing evidence:

- `docs/current/SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_EVIDENCE_V1.md`
- `docs/current/SERVICE_1_DOCUMENTARY_RECONCILIATION_V1.md`
- `docs/pymia/SERVICE_1_CASE_001_PHYSICAL_XLSX_E2E_TASKSPEC.md`

Source artifact inspected:

```text
C:\Users\PC\AppData\Local\Temp\opencode\case001_run\.tmp\service_1_cases\case_asset_a7e85d9a7ed2\column_confirmation_packet.json
```

Artifact facts:

```text
packet_type: COLUMN_CONFIRMATION
status: NEEDS_OWNER_CONFIRMATION
runtime_authorized: false
question_count: 12
warnings: []
```

## Accuracy boundary

This packet does not answer the questions. It only transcribes the pending owner
questions from the artifact and provides a controlled response template. Business
meaning must come from the PyME owner. If a key is absent from the artifact, this
document says `not present in artifact` instead of guessing.

## Pending owner questions

| # | question_id | field | sheet/table | column | required | answer_type |
|---|---|---|---|---|---|---|
| 1 | `col_confirm_001` | not present in artifact | `Ventas_Junio_2026` | `fecha` | `true` | `owner_text` |
| 2 | `col_confirm_002` | not present in artifact | `Ventas_Junio_2026` | `comprobante` | `true` | `owner_text` |
| 3 | `col_confirm_003` | not present in artifact | `Ventas_Junio_2026` | `producto_codigo` | `true` | `owner_text` |
| 4 | `col_confirm_004` | not present in artifact | `Ventas_Junio_2026` | `producto` | `true` | `owner_text` |
| 5 | `col_confirm_005` | not present in artifact | `Ventas_Junio_2026` | `categoria` | `true` | `owner_text` |
| 6 | `col_confirm_006` | not present in artifact | `Ventas_Junio_2026` | `cantidad` | `true` | `owner_text` |
| 7 | `col_confirm_007` | not present in artifact | `Ventas_Junio_2026` | `precio_unitario` | `true` | `owner_text` |
| 8 | `col_confirm_008` | not present in artifact | `Ventas_Junio_2026` | `costo_unitario` | `true` | `owner_text` |
| 9 | `col_confirm_009` | not present in artifact | `Ventas_Junio_2026` | `canal` | `true` | `owner_text` |
| 10 | `col_confirm_010` | not present in artifact | `Ventas_Junio_2026` | `venta_total` | `true` | `owner_text` |
| 11 | `col_confirm_011` | not present in artifact | `README` | `CASO` | `true` | `owner_text` |
| 12 | `col_confirm_012` | not present in artifact | `README` | `CASE_001_MARGIN_LEAK_MISSING_COSTS` | `true` | `owner_text` |

### 1. col_confirm_001 — fecha

- **Question id:** `col_confirm_001`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `fecha`
- **Exact owner question:** ¿Qué representa la columna 'fecha' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 2. col_confirm_002 — comprobante

- **Question id:** `col_confirm_002`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `comprobante`
- **Exact owner question:** ¿Qué representa la columna 'comprobante' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 3. col_confirm_003 — producto_codigo

- **Question id:** `col_confirm_003`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `producto_codigo`
- **Exact owner question:** ¿Qué representa la columna 'producto_codigo' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 4. col_confirm_004 — producto

- **Question id:** `col_confirm_004`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `producto`
- **Exact owner question:** ¿Qué representa la columna 'producto' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 5. col_confirm_005 — categoria

- **Question id:** `col_confirm_005`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `categoria`
- **Exact owner question:** ¿Qué representa la columna 'categoria' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 6. col_confirm_006 — cantidad

- **Question id:** `col_confirm_006`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `cantidad`
- **Exact owner question:** ¿Qué representa la columna 'cantidad' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 7. col_confirm_007 — precio_unitario

- **Question id:** `col_confirm_007`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `precio_unitario`
- **Exact owner question:** ¿Qué representa la columna 'precio_unitario' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 8. col_confirm_008 — costo_unitario

- **Question id:** `col_confirm_008`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `costo_unitario`
- **Exact owner question:** ¿Qué representa la columna 'costo_unitario' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 9. col_confirm_009 — canal

- **Question id:** `col_confirm_009`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `canal`
- **Exact owner question:** ¿Qué representa la columna 'canal' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 10. col_confirm_010 — venta_total

- **Question id:** `col_confirm_010`
- **Field:** not present in artifact
- **Sheet/table:** `Ventas_Junio_2026`
- **Column name:** `venta_total`
- **Exact owner question:** ¿Qué representa la columna 'venta_total' en la hoja 'Ventas_Junio_2026'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 11. col_confirm_011 — CASO

- **Question id:** `col_confirm_011`
- **Field:** not present in artifact
- **Sheet/table:** `README`
- **Column name:** `CASO`
- **Exact owner question:** ¿Qué representa la columna 'CASO' en la hoja 'README'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

### 12. col_confirm_012 — CASE_001_MARGIN_LEAK_MISSING_COSTS

- **Question id:** `col_confirm_012`
- **Field:** not present in artifact
- **Sheet/table:** `README`
- **Column name:** `CASE_001_MARGIN_LEAK_MISSING_COSTS`
- **Exact owner question:** ¿Qué representa la columna 'CASE_001_MARGIN_LEAK_MISSING_COSTS' en la hoja 'README'?
- **Why PymIA needs it:** PymIA cannot safely assign semantic meaning to this column without owner confirmation. Treating the name as self-explanatory would be an unsafe inference.
- **What answering unlocks:** this item contributes to column-confirmation completeness. Computation/dry-run remains blocked until all required column meanings are answered and validated.

## Owner response template

The owner should answer every required item. Do not invent answers on behalf of the owner.

```text
[1] col_confirm_001 | sheet/table: Ventas_Junio_2026 | column: fecha
    Question: ¿Qué representa la columna 'fecha' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[2] col_confirm_002 | sheet/table: Ventas_Junio_2026 | column: comprobante
    Question: ¿Qué representa la columna 'comprobante' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[3] col_confirm_003 | sheet/table: Ventas_Junio_2026 | column: producto_codigo
    Question: ¿Qué representa la columna 'producto_codigo' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[4] col_confirm_004 | sheet/table: Ventas_Junio_2026 | column: producto
    Question: ¿Qué representa la columna 'producto' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[5] col_confirm_005 | sheet/table: Ventas_Junio_2026 | column: categoria
    Question: ¿Qué representa la columna 'categoria' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[6] col_confirm_006 | sheet/table: Ventas_Junio_2026 | column: cantidad
    Question: ¿Qué representa la columna 'cantidad' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[7] col_confirm_007 | sheet/table: Ventas_Junio_2026 | column: precio_unitario
    Question: ¿Qué representa la columna 'precio_unitario' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[8] col_confirm_008 | sheet/table: Ventas_Junio_2026 | column: costo_unitario
    Question: ¿Qué representa la columna 'costo_unitario' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[9] col_confirm_009 | sheet/table: Ventas_Junio_2026 | column: canal
    Question: ¿Qué representa la columna 'canal' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[10] col_confirm_010 | sheet/table: Ventas_Junio_2026 | column: venta_total
    Question: ¿Qué representa la columna 'venta_total' en la hoja 'Ventas_Junio_2026'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[11] col_confirm_011 | sheet/table: README | column: CASO
    Question: ¿Qué representa la columna 'CASO' en la hoja 'README'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

[12] col_confirm_012 | sheet/table: README | column: CASE_001_MARGIN_LEAK_MISSING_COSTS
    Question: ¿Qué representa la columna 'CASE_001_MARGIN_LEAK_MISSING_COSTS' en la hoja 'README'?
    Owner confirmed meaning: <owner answer>
    Ambiguity or caveat: <none / explain>

```

## Validation checklist before re-run

- All 12 required items have owner-provided meanings.
- No answer is blank, circular, or ambiguous.
- No business meaning was inferred by PymIA or by an operator.
- Confirmed meanings are captured in a controlled confirmed-columns artifact before re-run.
- `runtime_authorized` remains `false` unless a later governed contract explicitly changes it.

## Stop conditions

- If any required column meaning is missing or ambiguous, CASE_001 remains `NEEDS_OWNER_INPUT`.
- Do not compute margin / cash / stock / reconciliation.
- Do not produce diagnosis or delivery.
- Do not run SaaS runtime, API / storage / worker, real runner, or autonomous delivery.
- Do not create a second XLSX parser.
- Do not claim product-ready or final diagnosis status.

## Next step after owner response

1. Validate owner responses against the checklist above.
2. Create a controlled confirmed-columns JSON artifact from the owner responses.
3. Re-run CASE_001 with the existing operator CLI and the confirmed-columns artifact:

```text
python -m pymia.cli.service_1_operator --file <xlsx> --source-channel cli --confirmed-columns <confirmed-columns.json>
```

4. Only after that re-run, evaluate whether an optional dry-run candidate is methodologically allowed.

Until validated owner responses exist, CASE_001 stays at `NEEDS_OWNER_INPUT` / `PASS_WITH_LIMITS`.
