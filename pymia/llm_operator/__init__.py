"""LLM Operator — operador externo offline sobre PymIA OS Tool Registry.

No usa LLM real. Diseñado para que un proveedor real (OpenAI, Anthropic, etc.)
pueda sustituir al MockProvider sin cambiar la interfaz del operador.
"""

from pymia.llm_operator.operator import LLMOperator, OperatorResult
from pymia.llm_operator.providers import AbstractProvider, MockProvider, ToolDecision

__all__ = [
    "LLMOperator",
    "OperatorResult",
    "AbstractProvider",
    "MockProvider",
    "ToolDecision",
]
