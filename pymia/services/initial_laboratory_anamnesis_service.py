from __future__ import annotations

from pydantic import BaseModel, Field


ESTADO_ESPERANDO_DOCUMENTACION = "esperando_documentacion"


class AnamnesisOriginaria(BaseModel):
    tenant_id: str
    canal: str
    frases_textuales: list[str] = Field(default_factory=list)
    dolores_detectados: list[str] = Field(default_factory=list)
    hipotesis_iniciales: list[str] = Field(default_factory=list)
    taxonomia_inicial: dict[str, str | None] = Field(default_factory=dict)
    documentos_pedidos: list[str] = Field(default_factory=list)
    estado_conversacional: str


class LaboratorioInicialContrato(BaseModel):
    tenant_id: str
    estado_conversacional: str
    hipotesis_a_contrastar: list[str] = Field(default_factory=list)
    evidencia_requerida: list[str] = Field(default_factory=list)
    capability: str
    tipo_documental_esperado: list[str] = Field(default_factory=list)
    campos_esperados: list[str] = Field(default_factory=list)
    nivel_confianza: str
    limite_actual: str


class InitialLaboratoryAnamnesisResult(BaseModel):
    message: str
    anamnesis: AnamnesisOriginaria
    laboratorio: LaboratorioInicialContrato


class InitialLaboratoryAnamnesisService:
    """Recepción clínica-operacional mínima para el primer tiempo lógico.

    Esta capa no diagnostica. Abre hipótesis, pide evidencia y reduce
    incertidumbre antes de derivar al pipeline documental.
    """

    _MARGIN_SIGNALS = (
        "no se si gano",
        "no sé si gano",
        "no se si estoy ganando",
        "no sé si estoy ganando",
        "perdiendo plata",
        "pierdo plata",
        "no me queda plata",
        "vendo pero",
        "vendo mucho",
        "margen",
        "rentabilidad",
        "ganancia",
        "ganando plata",
    )

    _OPERATIONAL_SIGNAL_GROUPS: tuple[tuple[tuple[str, ...], str], ...] = (
        (("operario", "operarios", "personal", "empleado", "empleados", "gente", "mano de obra"), "falta de capacidad humana"),
        (("produccion", "producir", "produzco", "fabricacion", "fabrica", "taller"), "tension de produccion"),
        (("ventas", "vendo menos", "bajaron las ventas", "cayeron las ventas"), "tension comercial"),
        (("pedidos", "entregas", "demoras", "atrasos"), "riesgo de cumplimiento"),
        (("stock", "faltantes", "mercaderia", "inventario"), "tension de stock"),
        (("manual", "carga manual", "excel", "copiar", "pegando", "repetitivo"), "sobrecarga administrativa"),
    )

    def process(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
    ) -> InitialLaboratoryAnamnesisResult | None:
        import uuid
        from pymia.pipeline.admission.v1.pipeline import AdmissionPipelineV1
        from pymia.pipeline.admission.v1.response_formatter import AdmissionResponseFormatterV1

        pipeline = AdmissionPipelineV1()
        pyme_id = uuid.uuid4()
        artifact, _ = pipeline.run(pyme_id=pyme_id, claim=text)

        message: str
        capability: str
        campos_esperados: list[str]
        dolores: list[str]
        limite_actual: str

        if artifact.hypotheses:
            formatter = AdmissionResponseFormatterV1()
            formatted_message = formatter.format_response(artifact)
            documentos = sorted(list(set(e for h in artifact.hypotheses for e in h.evidence_required)))
            hipotesis = [h.description for h in artifact.hypotheses]
            message = formatted_message or self._build_margin_message(documentos)
            dolores = ["incertidumbre de rentabilidad"]
            capability = "laboratorio_inicial_margen_rentabilidad"
            campos_esperados = [
                "producto",
                "fecha",
                "cantidad",
                "precio_venta",
                "costo",
                "proveedor",
                "medio_de_cobro",
            ]
            limite_actual = (
                "No se puede afirmar rentabilidad real sin contrastar ventas "
                "contra costos, precios y caja."
            )
        else:
            normalized = self._normalize(text)
            if any(signal in normalized for signal in self._MARGIN_SIGNALS):
                documentos = [
                    "ventas del período",
                    "costos o facturas de compra",
                    "lista de precios vigente",
                    "extracto/caja si querés revisar si el problema es liquidez",
                ]
                hipotesis = [
                    "margen erosionado",
                    "costos desactualizados",
                    "precios de venta no alineados a costo",
                    "caja o liquidez mezclada con rentabilidad",
                ]
                message = self._build_margin_message(documentos)
                dolores = ["incertidumbre de rentabilidad"]
                capability = "laboratorio_inicial_margen_rentabilidad"
                campos_esperados = [
                    "producto",
                    "fecha",
                    "cantidad",
                    "precio_venta",
                    "costo",
                    "proveedor",
                    "medio_de_cobro",
                ]
                limite_actual = (
                    "No se puede afirmar rentabilidad real sin contrastar ventas "
                    "contra costos, precios y caja."
                )
            else:
                operational_signals = self._extract_operational_signals(normalized)
                if not operational_signals:
                    return None

                documentos = [
                    "evolución de producción del período",
                    "evolución de ventas del mismo período",
                    "dotación de operarios por semana o mes",
                    "pedidos pendientes, rechazados o demorados",
                    "costos laborales y horas trabajadas si están disponibles",
                ]
                hipotesis = self._build_operational_hypotheses(operational_signals)
                message = self._build_operational_message(operational_signals, documentos)
                dolores = operational_signals
                capability = "laboratorio_inicial_operacional"
                campos_esperados = [
                    "periodo",
                    "unidades_producidas",
                    "ventas",
                    "operarios",
                    "horas_trabajadas",
                    "pedidos_pendientes",
                    "pedidos_perdidos",
                    "costo_laboral",
                ]
                limite_actual = (
                    "No se puede confirmar causa ni impacto económico sin contrastar "
                    "producción, ventas, dotación y pedidos del período."
                )

        anamnesis = AnamnesisOriginaria(
            tenant_id=tenant_id,
            canal=channel,
            frases_textuales=[text],
            dolores_detectados=dolores,
            hipotesis_iniciales=hipotesis,
            taxonomia_inicial={
                "rubro": None,
                "tipo_pyme": None,
                "produce_o_revende": None,
                "maneja_stock": None,
            },
            documentos_pedidos=documentos,
            estado_conversacional=ESTADO_ESPERANDO_DOCUMENTACION,
        )
        laboratorio = LaboratorioInicialContrato(
            tenant_id=tenant_id,
            estado_conversacional=ESTADO_ESPERANDO_DOCUMENTACION,
            hipotesis_a_contrastar=hipotesis,
            evidencia_requerida=documentos,
            capability=capability,
            tipo_documental_esperado=["xlsx", "csv", "pdf", "captura"],
            campos_esperados=campos_esperados,
            nivel_confianza="hipotesis_abierta",
            limite_actual=limite_actual,
        )

        return InitialLaboratoryAnamnesisResult(
            message=message,
            anamnesis=anamnesis,
            laboratorio=laboratorio,
        )

    def _extract_operational_signals(self, normalized: str) -> list[str]:
        signals: list[str] = []
        for patterns, signal in self._OPERATIONAL_SIGNAL_GROUPS:
            if any(pattern in normalized for pattern in patterns):
                signals.append(signal)
        return signals

    def _build_operational_hypotheses(self, signals: list[str]) -> list[str]:
        hypotheses = ["cuello de botella operacional"]
        if "falta de capacidad humana" in signals:
            hypotheses.append("pérdida de capacidad por falta de operarios")
        if "tension de produccion" in signals:
            hypotheses.append("caída de producción o throughput")
        if "tension comercial" in signals:
            hypotheses.append("caída de ventas asociada a capacidad operativa")
        if "riesgo de cumplimiento" in signals:
            hypotheses.append("pedidos no cubiertos o entregas demoradas")
        hypotheses.append("posible impacto económico pendiente de evidencia")
        return list(dict.fromkeys(hypotheses))

    def _build_margin_message(self, documentos: list[str]) -> str:
        docs = "\n".join(f"- {documento}" for documento in documentos)
        return (
            "Entiendo el dolor: estás vendiendo o trabajando, pero no tenés "
            "claridad sobre si la empresa realmente gana plata.\n\n"
            "Todavía no voy a diagnosticar. Primero necesito reducir "
            "incertidumbre con evidencia.\n\n"
            "Para abrir el primer laboratorio de rentabilidad/margen, enviame "
            "si podés:\n"
            f"{docs}\n\n"
            "Con eso puedo contrastar ventas contra costos/precios y separar "
            "si el problema parece ser margen, costos desactualizados o caja."
        )

    def _build_operational_message(self, signals: list[str], documentos: list[str]) -> str:
        detected = "\n".join(f"- {signal}" for signal in signals)
        docs = "\n".join(f"- {documento}" for documento in documentos)
        return (
            "Detecto una señal operacional, todavía no un diagnóstico.\n\n"
            "Señales registradas:\n"
            f"{detected}\n\n"
            "Hipótesis inicial: puede haber un cuello de botella operativo con impacto en producción, ventas o cumplimiento.\n\n"
            "Para abrir el primer laboratorio operacional, enviame si podés:\n"
            f"{docs}\n\n"
            "Con eso puedo contrastar si el problema viene de capacidad, dotación, demanda, pedidos demorados o impacto económico."
        )

    def _normalize(self, text: str) -> str:
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
        }
        normalized = text.lower().strip()
        for source, target in replacements.items():
            normalized = normalized.replace(source, target)
        return normalized
