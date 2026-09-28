# SERVICE 1 — C2 Tenant Learning F9 — Implementation Evidence V1

STATUS: EVIDENCE
PHASE: F9 — Tenant Learning
DATE: 2026-09-02

## Objective

Persist and re-expose owner-confirmed C2 V2 compositional semantics as tenant-scoped historical hints without granting automatic reuse, semantic rebind, runtime, mathematical, product or delivery authority.

## Reused authority path

F9 does not introduce a second memory system. It extends the existing:
- Service1OwnerConfirmationEventV1
- Service1TenantSemanticContractV1
- structural compatibility selector
- existing compatible_tenant_memory_hints provider context

## Changes

- Service1TenantSemanticContractV1 now accepts confirmation_scope=COMPOSITIONAL_SEMANTIC.
- The confirmed V2 descriptor is validated against the governed V2 taxonomy and bound to the exact physical sheet/column.
- compositional_semantic is serialized with the same immutable tenant semantic contract.
- structurally compatible tenant-memory selection exposes the V2 descriptor as historical evidence only.
- automatic_reuse_authorized=False and semantic_rebind_authorized=False remain mandatory.
- tenant filtering remains exact; another tenant's compositional memory is not returned.

## Fail-closed conditions

- V2 descriptor invalid/outside taxonomy -> blocked.
- descriptor field_ref mismatches the owner-confirmed physical column -> blocked.
- compositional semantics used under any scope other than COMPOSITIONAL_SEMANTIC -> blocked.
- cross-tenant memory -> excluded.
- structural incompatibility -> obsolete hint, not compatible reuse context.

## Compatibility observation

The focal gate exposed four historical SEM-5 tests that expected the pre-V2 legacy grouped dialogue when no F7 semantic_compression or compositional semantics are present. F8 was repaired to preserve that historical branch explicitly until F10; productive F7/F8 traffic remains on semantic units.

## Verification

Command:
python -m pytest -q tests/smartpyme/test_service_1_tenant_semantic_contract_v1.py tests/smartpyme/test_service_1_structural_compatibility_v1.py tests/smartpyme/test_service_1_owner_semantic_answer_projection_v1.py tests/smartpyme/test_service_1_owner_semantic_dialogue_v1.py tests/smartpyme/test_service_1_c2_v2_taller_real_flow.py

Result:
65 passed / 0 failed

## Authority

This phase creates tenant-scoped evidence/hints only. It does not auto-confirm later workbooks and does not grant runtime authority.
