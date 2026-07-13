from __future__ import annotations

from collections import Counter
from typing import Any, Final

SUMMARY_SCHEMA_VERSION: Final[str] = "1.0"
SERVICE_NAME: Final[str] = "SERVICE_1"
SUMMARY_FILENAME: Final[str] = "post_tool_owner_delivery_summary.md"

_TOOL_OWNER_LABELS: Final[dict[str, str]] = {
    "precio_margen_basico": "precio y margen básico",
    "caja_diaria_triage": "triage inicial de caja diaria",
    "stock_alertas_basicas": "alertas básicas de stock",
    "gastos_triage": "orden inicial de gastos",
    "proveedores_precio_variacion_triage": "revisión inicial de precios de proveedores",
}

_STATUS_OWNER_LABELS: Final[dict[str, str]] = {
    "OK": "se pudo calcular con los datos disponibles",
    "MISSING_INPUTS": "faltan datos necesarios para calcular",
    "INVALID_INPUT": "el dato existe, pero no es válido para esta revisión",
    "BLOCKED": "no conviene avanzar sin más información",
    "NOT_APPLICABLE": "no aplica con la evidencia disponible",
}


def render_service_1_post_tool_owner_delivery_summary_v1(
    packet: dict[str, Any],
) -> str:
    """Render a final owner-facing summary after First Aid tools ran.

    The renderer is intentionally pure: it reads already-produced packet data and
    pipeline_result fields, performs counting only, and returns markdown. It does
    not execute tools, open XLSX files, infer new facts, or authorize runtime.
    """
    pipeline_result = _required_dict(packet.get("pipeline_result"), "pipeline_result")
    if pipeline_result.get("service_name") != SERVICE_NAME:
        raise ValueError("SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_V1 only accepts SERVICE_1.")
    if pipeline_result.get("runtime_authorized") is not False:
        raise ValueError("SERVICE_1_POST_TOOL_OWNER_DELIVERY_SUMMARY_V1 requires runtime_authorized=False.")

    asset = _optional_dict(packet.get("asset"))
    detected_structure = _optional_dict(packet.get("detected_structure"))
    delivery_flow = _required_dict(pipeline_result.get("delivery_flow"), "delivery_flow")
    tool_results = _required_list(pipeline_result.get("tool_results"), "tool_results")
    deliveries = _required_list(delivery_flow.get("deliveries"), "deliveries")

    filename = str(asset.get("filename") or "archivo recibido")
    sheets = _sheet_names(detected_structure)
    status_counts = Counter(str(result.get("status")) for result in tool_results if isinstance(result, dict))
    missing_entries = _missing_entries(tool_results)
    xlsx_files = [_basename(str(delivery.get("output_path", ""))) for delivery in deliveries if isinstance(delivery, dict)]

    lines: list[str] = [
        "# Entrega PymIA — Servicio 1",
        "",
        "## 1. Resumen ejecutivo",
        "",
        f"Analizamos el archivo **{filename}** como revisión inicial de Servicio 1 sobre datos declarados.",
        "",
        "La entrega contiene cálculos preliminares First Aid y archivos XLSX para revisión humana. No es auditoría, no es certificación y no confirma rentabilidad real.",
        "",
        "Resultado general:",
        "",
        f"- Herramientas aplicadas: **{len(tool_results)}**",
        f"- Resultados OK: **{status_counts.get('OK', 0)}**",
        f"- Datos faltantes: **{status_counts.get('MISSING_INPUTS', 0)}**",
        f"- Datos inválidos: **{status_counts.get('INVALID_INPUT', 0)}**",
        f"- Archivos XLSX generados: **{len(xlsx_files)}**",
        "- Revisión humana requerida: **sí**",
        "",
        "## 2. Archivo revisado",
        "",
        f"- Archivo recibido: **{filename}**",
        "- Tipo de archivo: **XLSX**" if filename.lower().endswith((".xlsx", ".xlsm")) else "- Tipo de archivo: **no determinado**",
        "- Alcance: **primeros auxilios operativos sobre datos declarados**",
        "",
        "## 3. Hojas detectadas",
        "",
    ]

    if sheets:
        lines.extend([f"- {sheet}" for sheet in sheets])
    else:
        lines.append("- No determinado con la evidencia disponible.")

    lines.extend([
        "",
        "## 4. Herramientas aplicadas",
        "",
        "| Herramienta | Uso | Estado |",
        "|---|---|---|",
    ])
    for result in tool_results:
        if not isinstance(result, dict):
            continue
        tool_ref = str(result.get("tool_ref", "tool"))
        status = str(result.get("status", "UNKNOWN"))
        lines.append(
            f"| `{tool_ref}` | {_tool_label(tool_ref)} | {_status_label(status)} |"
        )

    lines.extend([
        "",
        "## 5. Resultados principales",
        "",
    ])
    for result in tool_results:
        if not isinstance(result, dict):
            continue
        lines.extend(_tool_result_lines(result))

    lines.extend([
        "",
        "## 6. Faltantes o bloqueos",
        "",
    ])
    if missing_entries:
        for entry in missing_entries:
            lines.append(f"- `{entry['tool_ref']}`: falta `{entry['missing_input']}`.")
    else:
        lines.append("- No se detectaron faltantes declarados en las herramientas ejecutadas.")

    lines.extend([
        "",
        "## 7. Archivos entregados",
        "",
    ])
    if xlsx_files:
        for filename_out in xlsx_files:
            lines.append(f"- `{filename_out}`")
    else:
        lines.append("- No determinado con la evidencia disponible.")

    lines.extend([
        "",
        "Cada XLSX debe leerse junto con sus hojas de limitaciones y claims prohibidos.",
        "",
        "## 8. Límites de esta entrega",
        "",
        "Esta entrega:",
        "",
        "- no es auditoría contable;",
        "- no es certificación fiscal;",
        "- no es conciliación bancaria definitiva;",
        "- no confirma rentabilidad real;",
        "- no valida que los datos declarados sean correctos;",
        "- no reemplaza revisión humana;",
        "- no reemplaza al contador;",
        "- no ejecuta decisiones automáticas.",
        "",
        "## 9. Próximo paso humano",
        "",
    ])

    if missing_entries:
        lines.append(
            "Revisar los datos faltantes antes de usar esta entrega como conclusión económica o comercial."
        )
    else:
        lines.append(
            "Revisar si los resultados preliminares coinciden con la política comercial esperada y con la evidencia disponible."
        )

    lines.extend([
        "",
        "## 10. Nota final",
        "",
        "Los resultados surgen de los datos disponibles en el archivo recibido y de las herramientas First Aid ejecutadas. Si se corrigen, amplían o completan los datos, la revisión puede cambiar.",
    ])

    return "\n".join(lines).strip() + "\n"


def _required_dict(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a dict.")
    return value


def _optional_dict(value: object) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _required_list(value: object, label: str) -> list[object]:
    if not isinstance(value, list):
        raise ValueError(f"{label} must be a list.")
    return value


def _sheet_names(detected_structure: dict[str, Any]) -> list[str]:
    workbook = detected_structure.get("workbook")
    if not isinstance(workbook, dict):
        return []
    sheets = workbook.get("sheets")
    if not isinstance(sheets, list):
        return []
    names: list[str] = []
    for sheet in sheets:
        if isinstance(sheet, dict) and isinstance(sheet.get("name"), str):
            names.append(str(sheet["name"]))
    return names


def _missing_entries(tool_results: list[object]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for result in tool_results:
        if not isinstance(result, dict):
            continue
        missing_inputs = result.get("missing_inputs")
        if not isinstance(missing_inputs, list):
            continue
        for missing_input in missing_inputs:
            entries.append(
                {
                    "tool_ref": str(result.get("tool_ref", "tool")),
                    "missing_input": str(missing_input),
                }
            )
    return entries


def _basename(path: str) -> str:
    normalized = path.replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1] if normalized else "archivo_xlsx"


def _tool_label(tool_ref: str) -> str:
    return _TOOL_OWNER_LABELS.get(tool_ref, "revisión First Aid")


def _status_label(status: str) -> str:
    return _STATUS_OWNER_LABELS.get(status, status)


def _tool_result_lines(result: dict[str, Any]) -> list[str]:
    tool_ref = str(result.get("tool_ref", "tool"))
    status = str(result.get("status", "UNKNOWN"))
    owner_summary = str(result.get("owner_summary") or _status_label(status))
    lines = [f"### `{tool_ref}`", "", f"- Estado: **{status}**", f"- Lectura: {owner_summary}"]

    computed_results = result.get("computed_results")
    if isinstance(computed_results, dict) and computed_results:
        lines.append("- Resultados calculados:")
        for key, value in computed_results.items():
            lines.append(f"  - `{key}`: `{value}`")

    missing_inputs = result.get("missing_inputs")
    if isinstance(missing_inputs, list) and missing_inputs:
        lines.append("- Faltantes:")
        for missing_input in missing_inputs:
            lines.append(f"  - `{missing_input}`")

    lines.append("")
    return lines
