# SmartCounter Risk Register

This document registers critical design, compliance, and operational risks identified during the documentary audit of the SmartCounter docs. These risks must be resolved or mitigated before activating any corresponding candidates in `PymIA-Live`.

## Registered Risks

| ID / Document | Risk Type / Code | Criticality | Description / Operational Danger | Recommended Mitigation / Sufficiency Guard |
| :--- | :--- | :--- | :--- | :--- |
| **cash_reconciliation.md** | `ACCOUNTING_OVERCLAIM` | **ALTA** | Promising automated, definitive bank reconciliation raises false expectations. True bank reconciliation requires double-entry accounting integration and external statements audit. | Set strict boundaries stating this is a cashbook matching tool, not a certified accounting balance. Disable claims of official audit reconciliation. |
| **tax_classification_draft.md** | `KERNEL_CONTAMINATION_RISK / LEGAL_RISK` | **CRÍTICA** | Hardcoding local tax definitions or automating tax category mappings inside the calculation core can lead to legal liabilities and code bloat. | Quarantined. Do not migrate this logic to the core database or application logic. Keep tax categorization outside runtime. |
| **real_margin_calc.md** | `INSUFFICIENT_EVIDENCE_RISK` | **MEDIA** | Generating margin reports with missing variables (such as variable gateway processing commissions or regional tax rates) can mislead the seller into thinking they are profitable when they are losing money. | Implement a **Sufficiency Guard** that requires the user to explicitly define channel fee rules or flags when transactional details are incomplete. |
| **legacy_audit_notes.md** | `OUTDATED_DOC_RISK` | **BAJA** | Migrating legacy notes or old requirements can contaminate the team's scope with deprecated data models. | Keep notes archived for history only. Mark as non-migratable. |
| **expense_structure.md** | `SECTOR_HARDCODE_RISK` | **MEDIA** | Hardcoding cost classification structures for a single industry sector limits the system's ability to scale to general PyMEs. | Keep categories configurable at the tenant/account level rather than hardcoded in the codebase database schemas. |

---

## Prohibited Claims

Under no circumstances should the active tools or user interfaces present the following claims to the owner:
- **auditoría contable certificada** (certified accounting audit)
- **conciliación bancaria definitiva** (definitive bank reconciliation)
- **clasificación fiscal automática** (automatic tax classification)
- **rentabilidad real confirmada sin evidencia completa** (confirmed real profitability without complete evidence)
- **diagnóstico integral de la empresa** (global enterprise diagnostic)

All features must be treated as mechanical validation indicators under the `UNDECIDED` candidate status.
