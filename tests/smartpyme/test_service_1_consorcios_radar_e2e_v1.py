from pymia.smartpyme.service_1_consorcios_collection_aging_v1 import (
    evaluate_collection_aging_from_normalized_tables_v1,
)
from pymia.smartpyme.service_1_consorcios_expense_variance_v1 import (
    evaluate_expense_variance_v1,
)
from pymia.smartpyme.service_1_consorcios_radar_plug_v1 import (
    OBS_BANK_UNMATCHED_AMOUNT,
    OBS_DEBT_EQUIVALENT_PERIODS,
    OBS_EXPENSE_BUDGET_DEVIATION_PCT,
    project_bank_reconciliation_to_radar_v1,
    project_collection_aging_to_radar_v1,
    project_expense_variance_to_radar_v1,
)
from pymia.smartpyme.service_1_radar_engine_v1 import evaluate_radar_observation_v1
from pymia.smartpyme.service_1_radar_observation_policy_v1 import (
    COMM_ALERT,
    COMM_NOTIFICATION,
    COMM_URGENCY,
    build_radar_observation_policy_v1,
)
from pymia.smartpyme.service_1_radar_observable_v1 import OP_GT, OP_GTE
from pymia.smartpyme.service_2_reconciliation_match_candidates_v1 import (
    build_reconciliation_match_candidates_v1,
)


def test_consorcios_real_vertical_capabilities_reach_owner_defined_radar_events() -> None:
    tenant_id = "tenant_consorcio_e2e"

    aging = evaluate_collection_aging_from_normalized_tables_v1(
        normalized_tables=[
            {
                "sheet_name": "Expensas",
                "rows": [
                    {
                        "unidad_funcional": "UF-12",
                        "saldo_anterior": 200,
                        "expensa_mes": 100,
                    }
                ],
            }
        ]
    )
    aging_observation = project_collection_aging_to_radar_v1(
        computation_result=aging
    )[0]
    assert aging_observation.observable.observable_ref == OBS_DEBT_EQUIVALENT_PERIODS
    aging_policy = build_radar_observation_policy_v1(
        tenant_id=tenant_id,
        policy_ref="owner-debt-two-periods",
        observable=aging_observation.observable,
        enabled=True,
        operator=OP_GTE,
        comparison_value="2",
        communication_level=COMM_ALERT,
        confirmed_by_owner=True,
    )
    aging_events = evaluate_radar_observation_v1(
        tenant_id=tenant_id,
        observable=aging_observation.observable,
        observed_value=aging_observation.observed_value,
        policies=(aging_policy,),
    )
    assert len(aging_events) == 1
    assert aging_events[0].communication_level == COMM_ALERT
    assert aging_events[0].observed_value == "2.0"

    expense = evaluate_expense_variance_v1(
        expense_rows=[{"Rubro": "Limpieza", "Importe": 150}],
        budget_rows=[
            {
                "Rubro": "Limpieza",
                "Presupuesto": 100,
                "Historico": 100,
            }
        ],
        expense_bindings={"rubro": "Rubro", "importe": "Importe"},
        budget_bindings={
            "rubro": "Rubro",
            "presupuesto_mensual": "Presupuesto",
            "promedio_historico": "Historico",
        },
    )
    expense_observations = project_expense_variance_to_radar_v1(
        computation_result=expense
    )
    budget_observation = next(
        item
        for item in expense_observations
        if item.observable.observable_ref == OBS_EXPENSE_BUDGET_DEVIATION_PCT
    )
    expense_policy = build_radar_observation_policy_v1(
        tenant_id=tenant_id,
        policy_ref="owner-expense-deviation",
        observable=budget_observation.observable,
        enabled=True,
        operator=OP_GT,
        comparison_value="40",
        communication_level=COMM_NOTIFICATION,
        confirmed_by_owner=True,
    )
    expense_events = evaluate_radar_observation_v1(
        tenant_id=tenant_id,
        observable=budget_observation.observable,
        observed_value=budget_observation.observed_value,
        policies=(expense_policy,),
    )
    assert len(expense_events) == 1
    assert expense_events[0].communication_level == COMM_NOTIFICATION
    assert expense_events[0].observed_value == "50.0"

    reconciliation = build_reconciliation_match_candidates_v1(
        bank_movements=[
            {
                "id": "BANK-1",
                "fecha": "2026-08-01",
                "importe": 1250.0,
                "descripcion": "Movimiento sin imputar",
                "referencia": "B-001",
            }
        ],
        internal_movements=[],
    )
    bank_observations = project_bank_reconciliation_to_radar_v1(
        reconciliation_result=reconciliation
    )
    amount_observation = next(
        item
        for item in bank_observations
        if item.observable.observable_ref == OBS_BANK_UNMATCHED_AMOUNT
    )
    bank_policy = build_radar_observation_policy_v1(
        tenant_id=tenant_id,
        policy_ref="owner-bank-unmatched-amount",
        observable=amount_observation.observable,
        enabled=True,
        operator=OP_GTE,
        comparison_value="1000",
        communication_level=COMM_URGENCY,
        confirmed_by_owner=True,
    )
    bank_events = evaluate_radar_observation_v1(
        tenant_id=tenant_id,
        observable=amount_observation.observable,
        observed_value=amount_observation.observed_value,
        policies=(bank_policy,),
    )
    assert len(bank_events) == 1
    assert bank_events[0].communication_level == COMM_URGENCY
    assert bank_events[0].observed_value == "1250.0"

    for event in (*aging_events, *expense_events, *bank_events):
        payload = event.to_dict()
        assert "severity" not in payload
        assert "risk" not in payload
        assert "positive" not in payload
        assert "negative" not in payload
