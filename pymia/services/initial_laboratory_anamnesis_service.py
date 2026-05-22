from __future__ import annotations

from pydantic import BaseModel, Field

from pymia.contracts.attachment_lifecycle_v1 import EvidenceBundle


ESTADO_ESPERANDO_DOCUMENTACION = "esperando_documentacion"
ESTADO_ADJUNTO_FALLIDO = "adjunto_parse_failed"
ESTADO_ADJUNTO_PENDIENTE = "adjunto_parse_pending"


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
        evidence: object | None = None,
        bundle: EvidenceBundle | None = None,
    ) -> InitialLaboratoryAnamnesisResult | None:
        from pymia.contracts.attachment_lifecycle_v1 import EvidenceBundle, AttachmentParseStatus, AttachmentLifecycleState

        if bundle is not None and bundle.attachments:
            # First, check for failures or pending status
            for att in bundle.attachments:
                if (att.parse_status == AttachmentParseStatus.FAILED or 
                    att.lifecycle_state == AttachmentLifecycleState.PARSE_FAILED or
                    att.parse_status == "FAILED" or
                    att.lifecycle_state == "PARSE_FAILED"):
                    
                    error_msg = f"Recibí el Excel, pero no pude procesarlo correctamente. Causa: {att.user_message or 'Error de análisis.'}"
                    anamnesis = AnamnesisOriginaria(
                        tenant_id=tenant_id,
                        canal=channel,
                        frases_textuales=[text],
                        dolores_detectados=[],
                        hipotesis_iniciales=[],
                        taxonomia_inicial={
                            "rubro": None,
                            "tipo_pyme": None,
                            "produce_o_revende": None,
                            "maneja_stock": None,
                        },
                        documentos_pedidos=[],
                        estado_conversacional="error_procesamiento_evidencia",
                    )
                    laboratorio = LaboratorioInicialContrato(
                        tenant_id=tenant_id,
                        estado_conversacional="error_procesamiento_evidencia",
                        hipotesis_a_contrastar=[],
                        evidencia_requerida=[],
                        capability="error_procesamiento_evidencia",
                        tipo_documental_esperado=["xlsx", "csv", "pdf", "captura"],
                        campos_esperados=[],
                        nivel_confianza="error",
                        limite_actual="Error al procesar la evidencia cargada.",
                    )
                    return InitialLaboratoryAnamnesisResult(
                        message=error_msg,
                        anamnesis=anamnesis,
                        laboratorio=laboratorio,
                    )
                
                elif (att.lifecycle_state in {AttachmentLifecycleState.RECEIVED, AttachmentLifecycleState.DOWNLOADED} or
                      att.lifecycle_state in {"RECEIVED", "DOWNLOADED"}):
                    
                    error_msg = "Recibí el archivo, pero todavía no fue procesado."
                    anamnesis = AnamnesisOriginaria(
                        tenant_id=tenant_id,
                        canal=channel,
                        frases_textuales=[text],
                        dolores_detectados=[],
                        hipotesis_iniciales=[],
                        taxonomia_inicial={
                            "rubro": None,
                            "tipo_pyme": None,
                            "produce_o_revende": None,
                            "maneja_stock": None,
                        },
                        documentos_pedidos=[],
                        estado_conversacional="procesamiento_pendiente",
                    )
                    laboratorio = LaboratorioInicialContrato(
                        tenant_id=tenant_id,
                        estado_conversacional="procesamiento_pendiente",
                        hipotesis_a_contrastar=[],
                        evidencia_requerida=[],
                        capability="procesamiento_pendiente",
                        tipo_documental_esperado=["xlsx", "csv", "pdf", "captura"],
                        campos_esperados=[],
                        nivel_confianza="pendiente",
                        limite_actual="El archivo todavía no fue procesado.",
                    )
                    return InitialLaboratoryAnamnesisResult(
                        message=error_msg,
                        anamnesis=anamnesis,
                        laboratorio=laboratorio,
                    )
            
            # If no failures, extract the first valid evidence to use
            for att in bundle.attachments:
                if att.evidence is not None:
                    evidence = att.evidence
                    break

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
            documentos = self._filter_requested_documents_by_evidence(documentos, evidence)
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
            if any(signal in normalized for signal in self._MARGIN_SIGNALS) or (evidence is not None):
                documentos = [
                    "ventas del período",
                    "costos o facturas de compra",
                    "lista de precios vigente",
                    "extracto/caja si querés revisar si el problema es liquidez",
                ]
                documentos = self._filter_requested_documents_by_evidence(documentos, evidence)
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

    def _result_from_attachment_lifecycle(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
        evidence_bundle: EvidenceBundle | None,
    ) -> InitialLaboratoryAnamnesisResult | None:
        if evidence_bundle is None or not evidence_bundle.has_attachments:
            return None

        failed = evidence_bundle.failed_attachments()
        if failed:
            message = failed[0].safe_user_message()
            return self._attachment_lifecycle_result(
                tenant_id=tenant_id,
                channel=channel,
                text=text,
                message=message,
                estado=ESTADO_ADJUNTO_FALLIDO,
                limite_actual="El documento fue recibido, pero no pudo convertirse en evidencia computable segura.",
            )

        pending = evidence_bundle.pending_attachments()
        if pending and not evidence_bundle.succeeded_attachments():
            message = pending[0].safe_user_message()
            return self._attachment_lifecycle_result(
                tenant_id=tenant_id,
                channel=channel,
                text=text,
                message=message,
                estado=ESTADO_ADJUNTO_PENDIENTE,
                limite_actual="El documento fue recibido, pero aún no existe evidencia computable para contrastar.",
            )

        return None

    def _attachment_lifecycle_result(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
        message: str,
        estado: str,
        limite_actual: str,
    ) -> InitialLaboratoryAnamnesisResult:
        anamnesis = AnamnesisOriginaria(
            tenant_id=tenant_id,
            canal=channel,
            frases_textuales=[text],
            dolores_detectados=["adjunto recibido sin evidencia computable disponible"],
            hipotesis_iniciales=[],
            taxonomia_inicial={
                "rubro": None,
                "tipo_pyme": None,
                "produce_o_revende": None,
                "maneja_stock": None,
            },
            documentos_pedidos=[],
            estado_conversacional=estado,
        )
        laboratorio = LaboratorioInicialContrato(
            tenant_id=tenant_id,
            estado_conversacional=estado,
            hipotesis_a_contrastar=[],
            evidencia_requerida=[],
            capability="attachment_evidence_lifecycle_ack",
            tipo_documental_esperado=[],
            campos_esperados=[],
            nivel_confianza="sin_evidencia_computable",
            limite_actual=limite_actual,
        )
        return InitialLaboratoryAnamnesisResult(
            message=message,
            anamnesis=anamnesis,
            laboratorio=laboratorio,
        )

    def _filter_requested_documents_by_evidence(self, documentos: list[str], evidence: object | None) -> list[str]:
        if evidence is None:
            return documentos

        computed = getattr(evidence, "computed_variables", None) or {}
        has_sales = any(key in computed for key in ("ventas_total", "sales", "sold_amount"))
        has_costs = any(key in computed for key in ("costos_total", "costs", "cost_of_goods_sold"))

        filtered: list[str] = []
        for documento in documentos:
            normalized = self._normalize(documento)
            if has_sales and "venta" in normalized:
                continue
            if has_costs and ("costo" in normalized or "factura" in normalized):
                continue
            filtered.append(documento)
        return filtered

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
            "Señal económico-operacional registrada: incertidumbre de rentabilidad.\n\n"
            "Estado: hipótesis abierta, sin diagnóstico confirmado.\n\n"
            "Ya recibí evidencia estructurada operacional y puedo empezar el contraste inicial.\n\n"
            "Laboratorio inicial de rentabilidad/margen — evidencia requerida:\n"
            f"{docs}\n\n"
            "Objetivo del contraste: separar margen erosionado, costos desactualizados, precios no alineados o tensión de caja."
        )

    def _build_operational_message(self, signals: list[str], documentos: list[str]) -> str:
        detected = "\n".join(f"- {signal}" for signal in signals)
        docs = "\n".join(f"- {documento}" for documento in documentos)
        return (
            "Señal operacional registrada, todavía sin diagnóstico confirmado.\n\n"
            "Señales registradas:\n"
            f"{detected}\n\n"
            "Hipótesis inicial: posible cuello de botella operativo con impacto en producción, ventas o cumplimiento.\n\n"
            "Laboratorio inicial operacional — evidencia requerida:\n"
            f"{docs}\n\n"
            "Objetivo del contraste: distinguir capacidad, dotación, demanda, pedidos demorados e impacto económico."
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
