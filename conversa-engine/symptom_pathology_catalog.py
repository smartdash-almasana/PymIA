from __future__ import annotations

from dataclasses import dataclass
from unicodedata import normalize


@dataclass(frozen=True)
class SymptomCatalogEntry:
    symptom_id: str
    name: str
    owner_pains: tuple[str, ...]
    operational_symptom: str
    candidate_pathologies: tuple[str, ...]
    hypothesis_template: str
    candidate_skills: tuple[str, ...]
    required_variables: tuple[str, ...]
    required_evidence: tuple[str, ...]
    mayeutic_questions: tuple[str, ...]
    advancement_criteria: tuple[str, ...]
    blocking_criteria: tuple[str, ...]


def _fold(text: str) -> str:
    text = normalize("NFKD", text.lower())
    return "".join(ch for ch in text if not ch.encode("ascii", "ignore") == b"")


CATALOG: tuple[SymptomCatalogEntry, ...] = (
    SymptomCatalogEntry(
        symptom_id="sospecha_perdida_margen",
        name="Sospecha de pérdida de margen",
        owner_pains=(
            "pierdo plata",
            "vendo pero no gano",
            "vendo mucho pero no gano",
            "vendo mucho pero no se si gano plata",
            "no me queda plata",
            "no me deja margen",
            "me aumentaron los costos",
            "no se si los precios estan actualizados",
        ),
        operational_symptom="Sospecha de deterioro del margen real frente al margen esperado.",
        candidate_pathologies=(
            "desalineacion_costo_precio",
            "costo_reposicion_desactualizado",
            "descuentos_no_controlados",
            "mix_productos_deteriorado",
            "comisiones_impuestos_no_imputados",
            "merma_stock_impactando_margen",
        ),
        hypothesis_template="Investigar si existe pérdida de margen por desalineación entre costos reales y precios de venta durante {periodo}.",
        candidate_skills=("skill_margin_leak_audit",),
        required_variables=("periodo", "productos_o_familias", "margen_esperado", "precio_venta_real", "costo_reposicion"),
        required_evidence=("ventas_pos", "excel_ventas", "facturas_proveedor", "lista_costos", "promociones_descuentos", "inventario_merma_si_aplica"),
        mayeutic_questions=(
            "¿Qué período querés revisar?",
            "¿Querés revisar todos los productos o una familia puntual?",
            "¿Tenés ventas y facturas de proveedor de ese período?",
            "¿Tenés una lista de precios o costos actualizada?",
        ),
        advancement_criteria=("existe demanda_original", "existe periodo o posibilidad de pedirlo", "existe evidencia de ventas o costos", "existe skill candidata"),
        blocking_criteria=("no hay ventas ni costos", "no hay período", "no hay productos o familias identificables"),
    ),
)


def match_symptoms_from_owner_message(message: str) -> list[SymptomCatalogEntry]:
    folded_message = _fold(message)
    matches: list[SymptomCatalogEntry] = []
    for entry in CATALOG:
        if any(_fold(pain) in folded_message for pain in entry.owner_pains):
            matches.append(entry)
    return matches


def get_symptom(symptom_id: str) -> SymptomCatalogEntry:
    for entry in CATALOG:
        if entry.symptom_id == symptom_id:
            return entry
    raise KeyError(symptom_id)


def get_candidate_pathologies(symptom_id: str) -> tuple[str, ...]:
    return get_symptom(symptom_id).candidate_pathologies


def get_required_variables(symptom_id: str) -> tuple[str, ...]:
    return get_symptom(symptom_id).required_variables


def get_required_evidence(symptom_id: str) -> tuple[str, ...]:
    return get_symptom(symptom_id).required_evidence


def get_mayeutic_questions(symptom_id: str) -> tuple[str, ...]:
    return get_symptom(symptom_id).mayeutic_questions


def get_blocking_criteria(symptom_id: str) -> tuple[str, ...]:
    return get_symptom(symptom_id).blocking_criteria
