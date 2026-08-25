# Servicio 1 — R13D1 canonical envelope fixture migration evidence

## Scope

R13D1 migrated only the SEM-2, SEM-3, and F6 test fixture envelopes that
were blocked by the current canonical workbook identity contract. The
fixtures now include `workbook_context` and `provenance`; their existing
column and normalized-table evidence was preserved. No production runtime
module was changed.

## Files changed

- `tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py`
- `tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py`
- `tests/smartpyme/test_service_1_semantic_dimensions_relationships_f6_v1.py`

## Verification

The exact 17 affected tests were executed as one bounded command:

```text
python -m pytest -q \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_provider_neutral_adapter_accepts_closed_structured_proposal \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_context_supports_workbook_first_without_fake_capability \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_contract_rejects_unknown_field \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_does_not_validate_evidence_existence_yet \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_provider_exception_fails_closed_without_exception_text \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_provider_non_mapping_fails_closed \
  tests/smartpyme/test_service_1_llm_semantic_interpreter_v1.py::test_sem2_context_rejects_authority_inside_memory_hint \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_validates_real_columns_evidence_roles_and_relationships \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_nonexistent_column_ref \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_hallucinated_evidence_ref \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_role_outside_allowed_ontology \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_incompatible_role_variable_pair \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_relationship_not_present_in_structural_profile \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_blocks_relationship_type_incompatible_with_structural_profile \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_marks_valid_but_capability_irrelevant_role_without_blocking \
  tests/smartpyme/test_service_1_semantic_proposal_validator_v1.py::test_sem3_explicit_irrelevant_real_ref_is_preserved_for_sem4 \
  tests/smartpyme/test_service_1_semantic_dimensions_relationships_f6_v1.py::test_workbook_profiler_relationship_detection_is_not_product_specific
```

Observed result: **17 passed / 0 failed** in **9.00s**.

No full suite, runtime changes, commit, push, or deploy was performed.
