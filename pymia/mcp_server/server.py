from __future__ import annotations

import asyncio
from typing import Any

from pymia.mcp_server.first_clinical_interview import (
    TOOL_NAME,
    invoke_first_clinical_interview,
)

_TOOL_DESCRIPTION = (
    "Ejecuta el primer contacto clínico de PymIA con el dueño. "
    "Respeta el orden taxonómico antes del pipeline clínico. "
    "No diagnostica. Devuelve mensaje, anamnesis, laboratorio y contexto progresivo actualizado."
)


def build_app() -> Any:
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError(
            "El paquete opcional 'mcp' no está disponible. "
            "Instalar dependencia MCP antes de ejecutar el server stdio real."
        ) from exc

    app = FastMCP("pymia")

    @app.tool(name=TOOL_NAME, description=_TOOL_DESCRIPTION)
    def first_clinical_interview(
        tenant_id: str,
        channel: str,
        text: str,
        previous_progressive_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return invoke_first_clinical_interview(
            tenant_id=tenant_id,
            channel=channel,
            text=text,
            previous_progressive_context=previous_progressive_context,
        )

    return app


def main() -> None:
    """Run PymIA MCP server over stdio.

    Command:
        python -m pymia.mcp_server.server
    """
    app = build_app()
    result = app.run()
    if asyncio.iscoroutine(result):
        asyncio.run(result)


if __name__ == "__main__":
    main()
