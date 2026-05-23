"""MCP server surface for PymIA clinical tools.

This package hosts the minimal stdio-compatible MCP server used by Hermes.
"""

from pymia.mcp_server.first_clinical_interview import invoke_first_clinical_interview

__all__ = ["invoke_first_clinical_interview"]
