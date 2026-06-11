from __future__ import annotations

import argparse
from pathlib import Path

from pymia.faithful_operator import OperatorPhase, run_local_operator_flow


DEFAULT_OWNER_MESSAGE = "Vendo más pero no me queda plata."
DEFAULT_OWNER_CONFIRMATION = "Sí, correcto, esas columnas representan mis ventas, costos, productos y período."
DEFAULT_EXCEL_CANDIDATES = (
    Path("prueba_excels/Cafeteria ABC.xlsx"),
    Path("prueba_excels/Cafetería ABC.xlsx"),
)
DEFAULT_REPORT_PATH = Path(".tmp/faithful_operator_demo_report.md")


def _resolve_default_excel() -> Path | None:
    for candidate in DEFAULT_EXCEL_CANDIDATES:
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def render_local_operator_demo(
    *,
    owner_message: str = DEFAULT_OWNER_MESSAGE,
    excel_path: Path | str | None = None,
    owner_confirmation: str | None = DEFAULT_OWNER_CONFIRMATION,
    tenant_id: str = "demo_cafeteria_abc",
    storage_dir: Path | str | None = Path(".tmp/faithful_operator_demo_storage"),
) -> str:
    resolved_excel = Path(excel_path) if excel_path is not None else _resolve_default_excel()
    result = run_local_operator_flow(
        owner_message,
        excel_path=resolved_excel,
        owner_confirmation=owner_confirmation,
        tenant_id=tenant_id,
        storage_dir=storage_dir,
    )
    states = result["states"]
    final_state = result["state"]

    lines = [
        "PYMIA FAITHFUL OPERATOR — DEMO LOCAL ASISTIDA",
        "",
        "Alcance: demo local, sin canal, sin producto, sin diagnóstico final automático.",
        "",
        "ENTRADA DEL DUEÑO",
        owner_message,
        "",
        "EVIDENCIA",
        str(resolved_excel) if resolved_excel is not None else "SIN_EXCEL_DISPONIBLE",
        "",
        "RECORRIDO",
    ]

    for index, state in enumerate(states, start=1):
        lines.append(f"{index}. {state.current_state.value}")

    lines.extend(
        [
            "",
            "TRAZABILIDAD",
            f"tenant_id: {final_state.tenant_id}",
            f"intake_id: {final_state.intake_id}",
            f"evidence_id: {final_state.evidence_id or 'pendiente'}",
            f"run_id: {final_state.run_id or 'pendiente'}",
            f"output_hash: {final_state.output_hash or 'pendiente'}",
            "",
            "SALIDA PARA OPERADOR ASISTIDO",
            str(result["response"]),
        ]
    )

    if final_state.current_state != OperatorPhase.CLOSED:
        lines.extend(
            [
                "",
                "ESTADO",
                final_state.current_state.value,
                "",
                "SIGUIENTE PREGUNTA",
                final_state.next_question,
            ]
        )

    return "\n".join(lines)


def render_operator_assisted_packet(demo_text: str) -> str:
    return "\n".join(
        [
            "# Paquete local para operador asistido",
            "",
            "Uso: entregar esta lectura como base de trabajo humano. No es producto, canal ni diagnóstico final automático.",
            "",
            "## Demo ejecutada",
            "",
            "```text",
            demo_text,
            "```",
            "",
            "## Control operativo",
            "",
            "- Verificar con el dueño que la evidencia corresponde al período correcto.",
            "- Confirmar que las columnas usadas representan ventas, costos y productos reales.",
            "- Registrar cualquier corrección antes de sostener una recomendación operativa.",
            "",
            "## Límite",
            "",
            "Este paquete no declara causa definitiva ni automatiza decisiones. Sirve para operación asistida trazable.",
        ]
    )


def write_operator_assisted_packet(demo_text: str, output_path: Path | str = DEFAULT_REPORT_PATH) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_operator_assisted_packet(demo_text), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo local mínima del PymIA Faithful Operator.")
    parser.add_argument("--excel", type=Path, default=None, help="Ruta al Excel real de evidencia.")
    parser.add_argument("--message", default=DEFAULT_OWNER_MESSAGE, help="Mensaje inicial del dueño pyme.")
    parser.add_argument("--confirmation", default=DEFAULT_OWNER_CONFIRMATION, help="Confirmación/corrección del dueño.")
    parser.add_argument("--tenant-id", default="demo_cafeteria_abc", help="Tenant técnico de demo.")
    parser.add_argument("--storage-dir", type=Path, default=Path(".tmp/faithful_operator_demo_storage"))
    parser.add_argument("--write-report", action="store_true", help="Escribe un paquete markdown local para operador asistido.")
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH, help="Ruta de salida del paquete markdown.")
    args = parser.parse_args()

    demo_text = render_local_operator_demo(
        owner_message=args.message,
        excel_path=args.excel,
        owner_confirmation=args.confirmation,
        tenant_id=args.tenant_id,
        storage_dir=args.storage_dir,
    )
    print(demo_text)

    if args.write_report:
        report_path = write_operator_assisted_packet(demo_text, args.report_path)
        print("\nREPORTE_LOCAL_ESCRITO")
        print(report_path)


if __name__ == "__main__":
    main()
