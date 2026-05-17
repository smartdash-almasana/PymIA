from __future__ import annotations

from symptom_pathology_catalog import (
    get_candidate_pathologies,
    get_mayeutic_questions,
    get_required_evidence,
    get_required_variables,
    match_symptoms_from_owner_message,
)


def main() -> None:
    message = "vendo mucho pero no sé si gano plata"
    matches = match_symptoms_from_owner_message(message)
    assert matches, "Expected at least one catalog match"

    entry = matches[0]
    assert entry.symptom_id == "sospecha_perdida_margen"
    assert "desalineacion_costo_precio" in get_candidate_pathologies(entry.symptom_id)
    assert "precio_venta_real" in get_required_variables(entry.symptom_id)
    assert "facturas_proveedor" in get_required_evidence(entry.symptom_id)
    assert get_mayeutic_questions(entry.symptom_id)

    print("CATALOG_INPUT:", message)
    print("CATALOG_MATCH:", entry.symptom_id)
    print("CANDIDATE_PATHOLOGIES:", ", ".join(entry.candidate_pathologies))
    print("REQUIRED_VARIABLES:", ", ".join(entry.required_variables))
    print("REQUIRED_EVIDENCE:", ", ".join(entry.required_evidence))
    print("CATALOG_SMOKE_OK:", True)


if __name__ == "__main__":
    main()
