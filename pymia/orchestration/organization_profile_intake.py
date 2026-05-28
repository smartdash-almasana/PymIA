from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass(frozen=True)
class OrganizationProfileQuestion:
    id: str
    text: str
    options: list[str]
    target_key: str


@dataclass(frozen=True)
class OrganizationProfileIntakeResult:
    reply_text: str
    updated_progressive_context: dict
    completed: bool
    next_question_id: str | None
    decision_trail_entry: str


def get_procedural_orientation() -> str:
    return (
        "Antes de empezar: podes expresarte libremente y subir documentacion todas las veces que quieras. "
        "Cada documento queda registrado con nombre, fecha y hora de recepcion y pasa a formar parte del "
        "archivo documental de tu organizacion para analisis actuales o futuros. Puedo pedir mas datos si "
        "hacen falta. Los analisis/reportes pueden tardar entre 1 hora y varios dias segun complejidad; "
        "no se hace todo junto. Tambien puedo asistir con conciliaciones, calculos de movimientos, stock, "
        "inventarios, lectura/curacion documental y factoria administrativa. Con los dias, voy construyendo "
        "contexto realista de tu organizacion para darte mas nitidez operativa."
    )


def get_organization_profile_questions() -> list[OrganizationProfileQuestion]:
    common_tail = ["Otro", "No se", "Prefiero no responder"]
    return [
        OrganizationProfileQuestion(
            id="business_type",
            text="Tipo de organizacion/negocio:",
            options=["Persona fisica", "PyME", "Empresa mediana", "Cooperativa"] + common_tail,
            target_key="business_type",
        ),
        OrganizationProfileQuestion(
            id="taxonomy",
            text="Rubro/taxonomia general:",
            options=["Textil", "Alimentos", "Comercio minorista", "Servicios profesionales"] + common_tail,
            target_key="taxonomy",
        ),
        OrganizationProfileQuestion(
            id="activity",
            text="Actividad principal (que vende/fabrica/presta):",
            options=["Vendo productos", "Fabrico productos", "Presto servicios", "Mixto"] + common_tail,
            target_key="activity",
        ),
        OrganizationProfileQuestion(
            id="size",
            text="Tamano aproximado:",
            options=["Micro", "Pequena", "Mediana", "Grande"] + common_tail,
            target_key="size",
        ),
        OrganizationProfileQuestion(
            id="employee_count",
            text="Cantidad de empleados o rango:",
            options=["1", "2-5", "6-20", "21-50", "51+"] + common_tail,
            target_key="employee_count",
        ),
        OrganizationProfileQuestion(
            id="operational_volume",
            text="Volumen operativo aproximado:",
            options=["Bajo", "Medio", "Alto", "Muy alto"] + common_tail,
            target_key="operational_volume",
        ),
        OrganizationProfileQuestion(
            id="sales_channels",
            text="Canales de venta/atencion:",
            options=["Local fisico", "Online", "Marketplace", "Mixto"] + common_tail,
            target_key="sales_channels",
        ),
        OrganizationProfileQuestion(
            id="current_tools",
            text="Herramientas actuales:",
            options=["Planillas", "Sistema ERP", "Sistema contable", "Mixto"] + common_tail,
            target_key="current_tools",
        ),
        OrganizationProfileQuestion(
            id="critical_area",
            text="Area critica percibida:",
            options=["Ventas", "Compras", "Stock", "Caja/finanzas", "Administracion"] + common_tail,
            target_key="critical_area",
        ),
        OrganizationProfileQuestion(
            id="main_problem",
            text="Principal problema actual:",
            options=["Rentabilidad", "Orden administrativo", "Falta de datos", "Desvio de costos"] + common_tail,
            target_key="main_problem",
        ),
        OrganizationProfileQuestion(
            id="document_order_level",
            text="Nivel de orden documental:",
            options=["Bajo", "Medio", "Alto"] + common_tail,
            target_key="document_order_level",
        ),
        OrganizationProfileQuestion(
            id="available_evidence",
            text="Evidencia disponible hoy:",
            options=["Excel ventas", "Excel compras", "Extractos", "Comprobantes", "Mixto"] + common_tail,
            target_key="available_evidence",
        ),
        OrganizationProfileQuestion(
            id="ready_to_upload_document",
            text="Disposicion a subir documentacion ahora:",
            options=["Si, ahora", "Si, hoy", "Si, esta semana", "No por ahora"] + common_tail,
            target_key="ready_to_upload_document",
        ),
    ]


def _build_context(progressive_context: dict) -> dict:
    updated = deepcopy(progressive_context if isinstance(progressive_context, dict) else {})
    profile = updated.get("organization_profile")
    if not isinstance(profile, dict):
        updated["organization_profile"] = {}
    return updated


def start_organization_profile_intake(progressive_context: dict) -> OrganizationProfileIntakeResult:
    updated = _build_context(progressive_context)
    questions = get_organization_profile_questions()
    first = questions[0]
    updated["organization_profile_status"] = "IN_PROGRESS"
    return OrganizationProfileIntakeResult(
        reply_text=f"{get_procedural_orientation()}\n\n{first.text}",
        updated_progressive_context=updated,
        completed=False,
        next_question_id=first.id,
        decision_trail_entry="Organization profile intake started",
    )


def answer_organization_profile_question(progressive_context: dict, answer: str) -> OrganizationProfileIntakeResult:
    updated = _build_context(progressive_context)
    questions = get_organization_profile_questions()
    profile = updated["organization_profile"]

    next_question = None
    for question in questions:
        if question.target_key not in profile:
            next_question = question
            break

    if next_question is None:
        updated["organization_profile_status"] = "COMPLETED"
        return OrganizationProfileIntakeResult(
            reply_text="La ficha organizacional ya esta completa. Si queres, podes subir documentacion para continuar.",
            updated_progressive_context=updated,
            completed=True,
            next_question_id=None,
            decision_trail_entry="Organization profile intake already completed",
        )

    profile[next_question.target_key] = answer

    following_question = None
    for question in questions:
        if question.target_key not in profile:
            following_question = question
            break

    if following_question is None:
        updated["organization_profile_status"] = "COMPLETED"
        return OrganizationProfileIntakeResult(
            reply_text=(
                "Ficha organizacional completa. Gracias. "
                "Cuando quieras, subi documentacion y avanzamos con el siguiente paso."
            ),
            updated_progressive_context=updated,
            completed=True,
            next_question_id=None,
            decision_trail_entry="Organization profile intake completed",
        )

    updated["organization_profile_status"] = "IN_PROGRESS"
    return OrganizationProfileIntakeResult(
        reply_text=following_question.text,
        updated_progressive_context=updated,
        completed=False,
        next_question_id=following_question.id,
        decision_trail_entry=f"Organization profile question answered: {next_question.id}",
    )
