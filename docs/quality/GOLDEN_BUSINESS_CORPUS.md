# Golden Business Corpus

This inventory is the canonical report-only business regression suite. It
reuses the existing corpus evaluators and expected replay oracle; it does not
create or regenerate business expectations.

## C2 multi-business corpus

Authority for every case is `EVIDENCE_ONLY`. The corpus demonstrates that real
physical workbooks can pass through the canonical intake/profile/context path
and that governed semantic coordinates and safe unknowns remain observable.
It does **not** demonstrate runtime authorization, tool execution authority,
product readiness, delivery authorization, automatic reuse, or business
calculation correctness.

| Case | Workbook | Sheet | Expectation |
| --- | --- | --- | --- |
| F11-SALES | `prueba_excels/CASE_001_ventas_junio_2026_margin_leak.xlsx` | `Ventas_Junio_2026` | governed semantic coordinates |
| F11-TEXTILE-SALES | `prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx` | `ventas` | governed semantic coordinates |
| F11-TEXTILE-PURCHASES | `prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx` | `compras` | governed semantic coordinates |
| F11-TEXTILE-STOCK | `prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx` | `stock` | governed semantic coordinates |
| F11-COLLECTIONS | `prueba_excels/cobros_marzo_2026.xlsx` | `Cobros_Marzo_2026` | governed semantic coordinates |
| F11-WORKSHOP | `prueba_excels/taller_mecanico_lubricar_srl.xlsx` | `ORDENES_TRABAJO` | governed semantic coordinates |
| F11-CASH-BANK-SAFE-UNKNOWN | `prueba_excels/first_aid_pilot_004_cash_bank_reconciliation_demo.xlsx` | `Caja_Banco` | safe unknown columns; no confident meaning |

Canonical source: `docs/current/SERVICE_1_C2_GOLDEN_BUSINESS_CORPUS_F11_V1.json`.

## La Textil golden replay

- XLSX source: `prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx`
- Expected oracle: `tests/golden_findings/la_textil_expected.json`
- Pipeline: `build_excel_structured_evidence` → `extract_evidence_pool` →
  `build_narrative_report_v2` → `validate_grounding` →
  `build_operational_audit_result` → `validate_operational_audit_result`.
- Compared fields: complete canonical normalized payload, with explicit checks
  for `tenant_id`, `pathology_findings`, `computed_metrics`, and
  `audit_trail`.
- Expected behavior: deterministic replay matches the preserved oracle. The
  oracle is never updated automatically.

## Physical XLSX product-readiness corpus

- Cases: 7 physical workbooks/sheets (`S1-PHY-001` through `S1-PHY-007`).
- Outcomes: `EXACT_MATCH`, `SAFE_QUESTION`, `SAFE_UNKNOWN`, and
  `FALSE_CONFIDENT` are reported by the existing evaluator.
- Fail-closed expectations: no dangerous false-confidence result, unknown
  meanings remain owner-confirmation questions, and readiness never grants
  runtime or delivery authority.

## Canonical execution

```text
python -m pytest -q -m golden
```

The baseline runner writes the external report to
`E:/BuenosPasos/smartbridge/PYMIA_GOLDEN_BUSINESS_CORPUS_BASELINE_V1.json`.
It records classifications and test identifiers only; it never rewrites an
oracle.
