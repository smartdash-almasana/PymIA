# SmartCounter Docs Audit Summary

This document summarizes the results of the documentary audit conducted on `E:\BuenosPasos\smartcounter\docs`. It maps out candidates for First Aid (Phase 1) and Deterministic Diagnosis (Phase 2), catalogs reusable packs, highlights key operational and structural risks, and outlines the recommended next steps.

## Audit Metrics
- **Source Audited**: `E:\BuenosPasos\smartcounter\docs`
- **Total Documents Inventoried**: 14
- **Phase 1 Candidates (First Aid)**: 5
- **Phase 2 Candidates (Deterministic Diagnosis)**: 6
- **Cross-Reference Documents (Transversal)**: 1
- **Non-migratable Documents (Quarantine / Excluded)**: 2
- **Runtime Code Touched**: NO
- **Files Modified in Runtime**: NO

---

## Document Classification

### Phase 1 — First Aid (Primeros Auxilios)
These documents focus on immediate operational checks, simple checklists, and basic rules to protect the business's capital from immediate leakage.
1. **ExcelStructureValidationPack** (Source: `excel_treatment_lab.md`) - Validates the structure and integrity of uploaded spreadsheets.
2. **SimpleCashArqueoChecklist** (Source: `cash_simple_check.md`) - Simple manual cash counting protocol.
3. **StockDesvioAlertRule** (Source: `stock_faltantes_detection.md`) - Alerts for immediate stock mismatch and count deviations.
4. **CostPriceReviewHeuristic** (Source: `cost_price_review.md`) - Simple heuristic to identify sales prices near or below cost.
5. **OwnerSignalTemplate** (Source: `initial_signal_protocol.md`) - Low-anxiety clinical alerts for business owners.

### Phase 2 — Deterministic Diagnosis (Diagnóstico Determinístico)
These documents provide deep, rule-based clinical analysis when sufficient data is available.
1. **RealMarginFormulaPack** (Source: `real_margin_calc.md`) - Computes real margins subtracting channel fees, taxes, and transaction costs.
2. **BankReconciliationWorkflow** (Source: `cash_reconciliation.md`) - Reconciles internal cash log entries with bank statements.
3. **BreakEvenFormulaPack** (Source: `break_even_analysis.md`) - Standard formula set to determine operational equilibrium point.
4. **FrozenStockDiagnostic** (Source: `frozen_stock_diagnosis.md`) - Identifies slow-moving or capital-locking physical inventory.
5. **ExpenseStructureAnalyzer** (Source: `expense_structure.md`) - Segregates fixed/variable costs and highlights operating leverage.
6. **AccountsPayableAgingReport** (Source: `accounts_payable_aging.md`) - Chronologically maps short-term and medium-term supplier liabilities.

### Cross-Reference (Referencia Transversal)
- **AccountingDefinitionsReference** (Source: `accounting_definitions.md`) - Core dictionary of definitions and rules.

### Non-migratable / Quarantine (No Migrar / Cuarentena)
These documents are excluded from the current migration path due to high risks of kernel contamination or obsolescence.
- `legacy_audit_notes.md` (Legacy notes, outdated)
- `tax_classification_draft.md` (Unstable legal/tax draft)

---

## Main Risks Registered

| Document / Source | Risk Code | Criticality | Description |
| :--- | :--- | :--- | :--- |
| `cash_reconciliation.md` | `ACCOUNTING_OVERCLAIM` | **ALTA** | Risk of claiming definitive/certified bank reconciliation which requires external banking integration and audit-level compliance. |
| `tax_classification_draft.md` | `KERNEL_CONTAMINATION_RISK / LEGAL_RISK` | **CRÍTICA** | High risk of polluting core calculation engine with changing local tax laws or promising automated tax compliance. |
| `real_margin_calc.md` | `INSUFFICIENT_EVIDENCE_RISK` | **MEDIA** | Risk of showing incorrect real profit margins if variables (e.g. shipping fees, regional taxes) are not fully recorded. |
| `expense_structure.md` | `SECTOR_HARDCODE_RISK` | **MEDIA** | Risk of hardcoding specific market sector expense schemas directly into the relational DB or analysis code. |
| `legacy_audit_notes.md` | `OUTDATED_DOC_RISK` | **BAJA** | Risk of importing obsolete requirements or debugging strategies that do not match the current PymIA-Live kernel. |

---

## Declarations & Confirmations
- **No filtering of candidates**: All 14 conceptual files have been accounted for and classified.
- **Activation status**: No activation decisions have been made. All candidates are set to `candidate_status: UNDECIDED` and `activation_status: NOT_DECIDED`.
- **Runtime status**: No production or test code has been created or modified in `pymia/` or `tests/`.

---

## Recommended Next Step
Review the Phase 1 candidates with the product team and PyME owners to define the minimal acceptance criteria for activation and design the manual/automatic input forms.
