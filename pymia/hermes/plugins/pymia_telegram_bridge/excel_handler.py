# -*- coding: utf-8 -*-
"""
Excel handler for the PymIA Telegram Bridge.

Responsibilities:
- Process Excel analysis requests
- Validate file existence and extension
- Call excel_diagnostic microservice
- Build operational reply with findings
- Fail-safe fallback if microservice unavailable
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pymia.hermes.plugins.pymia_telegram_bridge.config import EXCEL_EXTENSIONS

# Module-level import for test patching (diagnose_excel must exist as a name)
try:
    from pymia.smartpyme.excel_diagnostic import diagnose_excel
except ImportError:
    diagnose_excel = None

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AnalysisReply:
    """
    Result of an Excel analysis request.

    Attributes:
        reply_text: Text to send back to the user
        status: "EXECUTED", "BLOCKED", or "FAILED"
        findings_count: Number of findings (0 if failed)
        file_path: Path to the Excel file
    """
    reply_text: str
    status: str
    findings_count: int
    file_path: Path


def process_excel_analysis_request(
    file_path: str | Path,
    tenant_id: str,
    user_id: str,
    message_text: str,
) -> AnalysisReply:
    """
    Process an Excel analysis request.

    Args:
        file_path: Absolute path to the Excel file
        tenant_id: Tenant identifier (e.g., "telegram:123456")
        user_id: User identifier
        message_text: Original user message (for context, not used in analysis)

    Returns:
        AnalysisReply with:
        - reply_text: Operational text with findings or fallback error
        - status: "EXECUTED", "BLOCKED", or "FAILED"
        - findings_count: Number of findings
        - file_path: Path to the Excel file

    Validation:
        - file_path must exist
        - file_path must have .xlsx, .xls, or .csv extension

    Microservice:
        Calls pymia.smartpyme.excel_diagnostic.diagnose_excel()
        If microservice fails, returns fallback error message.

    Logs:
        [pymia.excel] file_path=... file_exists=... extension=... dispatcher_called=... status=...
    """
    path = Path(file_path)

    # Validate file exists
    if not path.exists():
        logger.error(
            "[pymia.excel] file_path=%s file_exists=false status=BLOCKED reason=file_not_found",
            path,
        )
        return AnalysisReply(
            reply_text=f"Error: el archivo no existe en la ruta esperada: {path.name}",
            status="BLOCKED",
            findings_count=0,
            file_path=path,
        )

    # Validate extension
    if path.suffix.lower() not in EXCEL_EXTENSIONS:
        logger.error(
            "[pymia.excel] file_path=%s file_exists=true extension=%s status=BLOCKED reason=unsupported_extension",
            path,
            path.suffix,
        )
        return AnalysisReply(
            reply_text=f"Error: el archivo debe ser .xlsx, .xls o .csv (recibido: {path.suffix})",
            status="BLOCKED",
            findings_count=0,
            file_path=path,
        )

    # Check microservice availability
    if diagnose_excel is None:
        logger.error(
            "[pymia.excel] file_path=%s dispatcher_called=false status=FAILED reason=import_error",
            path,
        )
        return AnalysisReply(
            reply_text=(
                f"Recibí el Excel `{path.name}`, pero todavía no pude procesarlo "
                f"con el microservicio local: módulo de diagnóstico no disponible."
            ),
            status="FAILED",
            findings_count=0,
            file_path=path,
        )

    # Call microservice
    try:
        logger.info(
            "[pymia.excel] file_path=%s file_exists=true extension=%s dispatcher_called=true",
            path,
            path.suffix,
        )

        result = diagnose_excel(
            excel_path=path,
            tenant_id=tenant_id,
        )

        # Build reply from findings
        if not result.findings:
            reply_text = (
                f"Recibí el Excel `{path.name}` y lo analicé.\n\n"
                f"Sin hallazgos críticos. El archivo tiene {result.evidence.total_rows} filas."
            )
        else:
            findings_summary = _build_findings_summary(result.findings)
            reply_text = (
                f"Recibí el Excel `{path.name}` y lo analicé.\n\n"
                f"**Hallazgos ({len(result.findings)}):**\n"
                f"{findings_summary}\n\n"
                f"Total de filas procesadas: {result.evidence.total_rows}"
            )

        logger.info(
            "[pymia.excel] file_path=%s dispatcher_called=true status=EXECUTED findings_count=%d",
            path,
            len(result.findings),
        )

        return AnalysisReply(
            reply_text=reply_text,
            status="EXECUTED",
            findings_count=len(result.findings),
            file_path=path,
        )

    except ImportError:
        # Microservice import failed (module not available)
        logger.error(
            "[pymia.excel] file_path=%s dispatcher_called=true status=FAILED reason=import_error",
            path,
        )
        return AnalysisReply(
            reply_text=(
                f"Recibí el Excel `{path.name}`, pero todavía no pude procesarlo "
                f"con el microservicio local: módulo de diagnóstico no disponible."
            ),
            status="FAILED",
            findings_count=0,
            file_path=path,
        )
    except Exception as exc:
        # Microservice execution failed
        logger.error(
            "[pymia.excel] file_path=%s dispatcher_called=true status=FAILED reason=execution_error error=%s error_type=%s",
            path,
            exc,
            type(exc).__name__,
        )
        return AnalysisReply(
            reply_text=(
                f"Recibí el Excel `{path.name}`, pero todavía no pude procesarlo "
                f"con el microservicio local: {type(exc).__name__}."
            ),
            status="FAILED",
            findings_count=0,
            file_path=path,
        )


def _build_findings_summary(findings: list) -> str:
    """
    Build a concise summary of findings for the user.

    Args:
        findings: List of Finding objects from excel_diagnostic

    Returns:
        Formatted string with findings summary
    """
    lines = []
    for finding in findings[:5]:  # Limit to top 5 findings
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
            finding.severity, "⚪"
        )
        lines.append(
            f"{severity_icon} **{finding.code}** (x{finding.count}): {finding.message}"
        )

    if len(findings) > 5:
        lines.append(f"... y {len(findings) - 5} hallazgos más.")

    return "\n".join(lines)


__all__ = ["AnalysisReply", "process_excel_analysis_request"]
