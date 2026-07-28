from __future__ import annotations


class DummyContent:
    def __init__(self, text: str):
        self.text = text


class DummyMessageResponse:
    """Mimic Anthropic Message response."""

    def __init__(self, text: str):
        self.content = [DummyContent(text)]


class DummyMessages:
    """Mimic anthropic.resources.Messages."""

    def __init__(self, dummy: DummyLLM):
        self._dummy = dummy

    def create(self, *, model: str, system: str, max_tokens: int, messages: list[dict]) -> DummyMessageResponse:
        last = messages[-1]["content"]
        answer = self._dummy._build_dummy_answer(last)
        return DummyMessageResponse(answer)


class DummyLLM:
    """Fallback dummy when ANTHROPIC_API_KEY is not set.

    Returns keyword-based canned responses so the Playwright flow
    can still be exercised without a real LLM call.
    """

    def __init__(self):
        self.messages = DummyMessages(self)

    def _build_dummy_answer(self, question: str) -> str:
        q = question.lower()

        if "quÉ representa" in q or "representa este archivo" in q:
            return "Son las ventas del mes"
        if "perÍodo" in q or "periodo" in q or "cubre" in q:
            return "Enero a marzo 2026"
        if "hoja" in q and ("principal" in q or "revisar primero" in q):
            return "Ventas"
        if "contiene esta hoja" in q:
            return "Los registros de ventas diarias"
        if "encabezado" in q or "significa cada" in q:
            return "La columna A es la fecha, la B es el importe"
        if "dÓnde empiezan" in q or "sin_encabezado" in q or "bloque" in q:
            return "Los datos empiezan en la fila 3"
        if "objetivo" in q or "revisiÓN" in q or "revision" in q:
            return "Quiero verificar que los totales estén bien"
        if "duda" in q or "columnas" in q or "valor" in q:
            return "La columna de IVA me genera duda"
        if "evidencia" in q or "otro archivo" in q or "faltante" in q:
            return "Sí, tengo un libro de IVA compras"
        return "No sé / requiere revisión humana"
