from pymia.smartpyme.service_1_consorcios_collection_aging_v1 import evaluate_collection_aging_from_normalized_tables_v1
from pymia.smartpyme.service_1_consorcios_expense_variance_v1 import evaluate_expense_variance_v1
from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    OBS_BANK_UNMATCHED_AMOUNT,
    OBS_BANK_UNMATCHED_COUNT,
    OBS_DEBT_EQUIVALENT_PERIODS,
    OBS_EXPENSE_BUDGET_DEVIATION_PCT,
    OBS_EXPENSE_HISTORICAL_DEVIATION_PCT,
    OBS_UNMATCHED_BANK_OPERATION,
    consorcios_radar_catalog_v1,
    project_bank_reconciliation_to_radar_v1,
    project_collection_aging_to_radar_v1,
    project_expense_variance_to_radar_v1,
)
from pymia.smartpyme.service_1_radar_engine_v1 import evaluate_radar_observation_v1
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    COMM_ALERT,
    COMM_NOTIFICATION,
    build_radar_observation_policy_v1,
)
from pymia.smartpyme.service_1_radar_observable_v1 import OP_EQ, OP_GT, OP_GTE
from pymia.smartpyme.service_2_reconciliation_match_candidates_v1 import build_reconciliation_match_candidates_v1


def test_catalog_exposes_six_neutral_consorcios_observables():
    catalog = consorcios_radar_catalog_v1()
    assert {item.observable_ref for item in catalog} == {
        OBS_DEBT_EQUIVALENT_PERIODS,
        OBS_EXPENSE_BUDGET_DEVIATION_PCT,
        OBS_EXPENSE_HISTORICAL_DEVIATION_PCT,
        OBS_BANK_UNMATCHED_COUNT,
        OBS_BANK_UNMATCHED_AMOUNT,
        OBS_UNMATCHED_BANK_OPERATION,
    }
    forbidden = {"risk", "severity", "positive", "negative", "threshold", "communication_level"}
    for item in catalog:
        assert forbidden.isdisjoint(item.to_dict())


def test_collection_aging_projection_uses_real_capability_result():
    result = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[
            {
                "sheet_name": "Expensas",
                "rows": [
                    {"unidad_funcional": "1A", "saldo_anterior": 200, "expensa_mes": 100},
                    {"unidad_funcional": "2B", "saldo_anterior": 0, "expensa_mes": 100},
                ],
            }
        ]
    )
    observations = project_collection_aging_to_radar_v1(computation_result=result)
    assert [(item.entity_ref, item.observed_value) for item in observations] == [("1A", "2.0"), ("2B", "0.0")]
    assert all(item.observable.observable_ref == OBS_DEBT_EQUIVALENT_PERIODS for item in observations)


def test_expense_variance_projection_uses_both_real_deviation_fields():
    result = evaluate_expense_variance_v1(
        expense_rows=[{"r": "Limpieza", "i": 130}],
        budget_rows=[{"r": "Limpieza", "b": 100, "h": 125}],
        expense_bindings={"rubro": "r", "importe": "i"},
        budget_bindings={"rubro": "r", "presupuesto_mensual": "b", "promedio_historico": "h"},
    )
    observations = project_expense_variance_to_radar_v1(computation_result=result)
    by_ref = {item.observable.observable_ref: item for item in observations}
    assert by_ref[OBS_EXPENSE_BUDGET_DEVIATION_PCT].entity_ref == "Limpieza"
    assert by_ref[OBS_EXPENSE_BUDGET_DEVIATION_PCT].observed_value == "30.0"
    assert by_ref[OBS_EXPENSE_HISTORICAL_DEVIATION_PCT].observed_value == "4.0"


def test_bank_reconciliation_projection_derives_count_amount_and_boolean_from_real_result():
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {"id": "b1", "fecha": "2026-08-01", "importe": 100.0, "referencia": "A"},
            {"id": "b2", "fecha": "2026-08-02", "importe": -40.0, "referencia": "B"},
        ],
        internal_movements=[],
    )
    observations = project_bank_reconciliation_to_radar_v1(reconciliation_result=result)
    by_ref = {item.observable.observable_ref: item.observed_value for item in observations}
    assert by_ref[OBS_BANK_UNMATCHED_COUNT] == "2"
    assert by_ref[OBS_BANK_UNMATCHED_AMOUNT] == "140.0"
    assert by_ref[OBS_UNMATCHED_BANK_OPERATION] is True


def test_projected_metric_can_flow_into_independent_engine_without_vertical_semantics():
    result = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[{"sheet_name": "Expensas", "rows": [{"unidad_funcional": "1A", "saldo_anterior": 200, "expensa_mes": 100}]}]
    )
    observation = project_collection_aging_to_radar_v1(computation_result=result)[0]
    policy = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="debt-policy",
        observable=observation.observable,
        enabled=True,
        operator=OP_GTE,
        comparison_value="2",
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )
    events = evaluate_radar_observation_v1(
        tenant_id="tenant-a",
        observable=observation.observable,
        observed_value=observation.observed_value,
        policies=(policy,),
    )
    assert len(events) == 1
    assert events[0].communication_level == COMM_ALERT


def test_projected_operation_can_flow_into_independent_engine():
    result = build_reconciliation_match_candidates_v1(
        bank_movements=[{"id": "b1", "fecha": "2026-08-01", "importe": 100.0}],
        internal_movements=[],
    )
    observation = next(
        item
        for item in project_bank_reconciliation_to_radar_v1(reconciliation_result=result)
        if item.observable.observable_ref == OBS_UNMATCHED_BANK_OPERATION
    )
    policy = build_radar_observation_policy_v1(
        tenant_id="tenant-a",
        policy_ref="unmatched-operation-policy",
        observable=observation.observable,
        enabled=True,
        operator=OP_EQ,
        comparison_value=True,
        communication_level=COMM_NOTIFICATION,
        confirmed_by_owner=True,
    )
    events = evaluate_radar_observation_v1(
        tenant_id="tenant-a",
        observable=observation.observable,
        observed_value=observation.observed_value,
        policies=(policy,),
    )
    assert len(events) == 1
    assert events[0].communication_level == COMM_NOTIFICATION


def test_plug_rejects_non_radarizable_reconciliation_status():
    try:
        project_bank_reconciliation_to_radar_v1(
            reconciliation_result={"status": "NEEDS_MORE_EVIDENCE", "banco_sin_imputar": []}
        )
    except ValueError as exc:
        assert "not radarizable" in str(exc)
    else:
        raise AssertionError("expected fail-closed result")
