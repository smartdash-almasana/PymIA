from __future__ import annotations

from pydantic import BaseModel, Field
from pymia.document_intelligence import TenantClinicalContext
from tests.fixtures.owner_claims import RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY


ESTADO_ESPERANDO_DOCUMENTACION = "esperando_documentacion"
ESTADO_ENCUADRE_TAXONOMICO = "encuadre_taxonomico_inicial"


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


class ProgressiveBusinessIdentity(BaseModel):
    """Progressive identity draft captured during initial anamnesis."""

    display_name: str | None = None
    country_code: str | None = None
    industry_hint: str | None = None
    # taxonomy_phase tracks whether FASE_0_IDENTIDAD was completed.
    # None = not started; "FASE_0_IDENTIDAD" = completed.
    taxonomy_phase: str | None = None


class ProgressiveTenantClinicalContext(BaseModel):
    """Internal progressive context scaffold before minimum validation is met."""

    tenant_id: str
    channel: str
    business_identity: ProgressiveBusinessIdentity
    symptom_summary: list[str] = Field(default_factory=list)
    documents_requested: list[str] = Field(default_factory=list)

    @property
    def is_minimum_valid(self) -> bool:
        """Minimum valid context requires both display name and country code."""
        return bool(
            self.business_identity.display_name
            and self.business_identity.country_code
        )

    @property
    def has_taxonomic_identity(self) -> bool:
        """Returns True only when basic industry/organism taxonomy has been established.

        taxonomy_phase must be explicitly set to "FASE_0_IDENTIDAD" by an external
        caller (e.g. a turn where the owner confirms their organism type).
        Mere heuristic inference from text is NOT sufficient.
        """
        return (
            self.business_identity.industry_hint is not None
            and self.business_identity.taxonomy_phase == "FASE_0_IDENTIDAD"
        )


class InitialLaboratoryAnamnesisResult(BaseModel):
    message: str
    anamnesis: AnamnesisOriginaria
    laboratorio: LaboratorioInicialContrato
    progressive_context: ProgressiveTenantClinicalContext | None = None


class InitialLaboratoryAnamnesisService:
    """Recepción clínica-operacional mínima para el primer tiempo lógico.

    Esta capa no diagnostica. Abre hipótesis, pide evidencia y reduce
    incertidumbre antes de derivar al pipeline documental.

    Orden de ejecución obligatorio (según CONTRATO_PRIMER_ENCUENTRO_TAXONOMICO):
    1. FASE_0_IDENTIDAD — encuadre taxonómico del organismo.
    2. Contexto clínico formal (TenantClinicalContext) si ya existe.
    3. Pipeline de hipótesis y evidencia (AdmissionPipelineV1).
    """

    _MARGIN_SIGNALS = (
        RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
        RAW_OWNER_CLAIM_MARGIN_UNCERTAINTY,
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
        bundle: object | None = None,
        tenant_context: TenantClinicalContext | None = None,
        previous_progressive_context: ProgressiveTenantClinicalContext | None = None,
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
                    # Build progressive context here
                    progressive_context = self._merge_progressive_context(
                        tenant_id=tenant_id,
                        previous=previous_progressive_context,
                        current=self._build_progressive_tenant_context(
                            tenant_id=tenant_id,
                            channel=channel,
                            text=text,
                            evidence=None,
                        )
                    )
                    return InitialLaboratoryAnamnesisResult(
                        message=error_msg,
                        anamnesis=anamnesis,
                        laboratorio=laboratorio,
                        progressive_context=progressive_context,
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
                    # Build progressive context here
                    progressive_context = self._merge_progressive_context(
                        tenant_id=tenant_id,
                        previous=previous_progressive_context,
                        current=self._build_progressive_tenant_context(
                            tenant_id=tenant_id,
                            channel=channel,
                            text=text,
                            evidence=None,
                        )
                    )
                    return InitialLaboratoryAnamnesisResult(
                        message=error_msg,
                        anamnesis=anamnesis,
                        laboratorio=laboratorio,
                        progressive_context=progressive_context,
                    )

            # If no failures, extract the first valid evidence to use
            for att in bundle.attachments:
                if att.evidence is not None:
                    evidence = att.evidence
                    break

        progressive_context: ProgressiveTenantClinicalContext | None = None
        if tenant_context is None:
            current_progressive_context = self._build_progressive_tenant_context(
                tenant_id=tenant_id,
                channel=channel,
                text=text,
                evidence=evidence,
            )
            progressive_context = self._merge_progressive_context(
                tenant_id=tenant_id,
                previous=previous_progressive_context,
                current=current_progressive_context,
            )

        # ── FASE_0_IDENTIDAD ──────────────────────────────────────────────────
        # Antes de correr cualquier pipeline clínico, se establece qué tipo de
        # organismo es la PyME. Si no hay TenantClinicalContext formal Y no hay
        # identidad taxonómica previa confirmada, se responde con encuadre
        # taxonómico. Sin hipótesis, sin pedido de documentos.
        if tenant_context is None and self._needs_taxonomic_framing(progressive_context):
            return self._build_taxonomic_framing_result(
                tenant_id=tenant_id,
                channel=channel,
                text=text,
                progressive_context=progressive_context,
            )
        # ── FIN FASE_0_IDENTIDAD ──────────────────────────────────────────────

        if tenant_context is not None and not self._tenant_context_is_minimum_valid(tenant_context):
            message = (
                "Contexto clínico insuficiente para habilitar inferencia documental. "
                "Podemos continuar la conversación inicial y completar identidad operativa."
            )
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
                estado_conversacional="contexto_clinico_insuficiente",
            )
            laboratorio = LaboratorioInicialContrato(
                tenant_id=tenant_id,
                estado_conversacional="contexto_clinico_insuficiente",
                hipotesis_a_contrastar=[],
                evidencia_requerida=[],
                capability="contexto_clinico_insuficiente",
                tipo_documental_esperado=["xlsx", "csv", "pdf", "captura"],
                campos_esperados=[],
                nivel_confianza="contexto_insuficiente",
                limite_actual="Falta contexto clínico mínimo validado.",
            )
            return InitialLaboratoryAnamnesisResult(
                message=message,
                anamnesis=anamnesis,
                laboratorio=laboratorio,
                progressive_context=progressive_context,
            )

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
            progressive_context=progressive_context,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # FASE_0_IDENTIDAD helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _needs_taxonomic_framing(
        self,
        progressive_context: ProgressiveTenantClinicalContext | None,
    ) -> bool:
        """Returns True when no basic taxonomic identity has been established.

        Gate for FASE_0_IDENTIDAD: if the progressive context does not carry
        a confirmed industry/organism type (taxonomy_phase == "FASE_0_IDENTIDAD"),
        the system must ask first, before running any clinical pipeline.
        """
        if progressive_context is None:
            return True
        return not progressive_context.has_taxonomic_identity

    def _build_taxonomic_framing_message(self) -> str:
        """Builds the canonical FASE_0_IDENTIDAD response.

        Sober, premium, human. Goes from general (organism type) to specific
        (operational nature → scale). Does NOT diagnose, request documents,
        emit hypotheses, or ask confidential/financial questions.
        """
        return (
            "Antes de analizar números o sacar conclusiones, necesito ubicar "
            "qué tipo de negocio estamos mirando.\n\n"
            "Para empezar, contame:\n"
            "¿Es un comercio, una fábrica / industria, una empresa de servicios, "
            "logística / distribución, gastronomía, construcción, agro, salud, "
            "educación u otro tipo de organización?\n\n"
            "Y si podés agregar:\n"
            "¿Fabricás, revendés, distribuís o prestás servicios?\n"
            "¿Vendés al público, a empresas, por local, online, por WhatsApp, "
            "por Mercado Libre u otro canal?\n"
            "¿Tenés empleados? Aproximadamente, ¿cuántos?\n\n"
            "Con eso puedo armar el contexto base antes de pedirte datos o documentos."
        )

    def _build_taxonomic_framing_result(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
        progressive_context: ProgressiveTenantClinicalContext | None,
    ) -> InitialLaboratoryAnamnesisResult:
        """Returns the structured result for FASE_0_IDENTIDAD.

        No hypotheses, no documents requested, no clinical diagnosis.
        Estado conversacional: encuadre_taxonomico_inicial.
        """
        message = self._build_taxonomic_framing_message()
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
            estado_conversacional=ESTADO_ENCUADRE_TAXONOMICO,
        )
        laboratorio = LaboratorioInicialContrato(
            tenant_id=tenant_id,
            estado_conversacional=ESTADO_ENCUADRE_TAXONOMICO,
            hipotesis_a_contrastar=[],
            evidencia_requerida=[],
            capability="encuadre_taxonomico",
            tipo_documental_esperado=[],
            campos_esperados=[],
            nivel_confianza="sin_contexto_taxonomico",
            limite_actual="No se puede iniciar análisis sin conocer el tipo de organismo.",
        )
        return InitialLaboratoryAnamnesisResult(
            message=message,
            anamnesis=anamnesis,
            laboratorio=laboratorio,
            progressive_context=progressive_context,
        )

    # ─────────────────────────────────────────────────────────────────────────
    # Supporting helpers
    # ─────────────────────────────────────────────────────────────────────────

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

    def _tenant_context_is_minimum_valid(self, tenant_context: TenantClinicalContext) -> bool:
        validator = getattr(tenant_context, "is_minimum_valid", None)
        if callable(validator):
            return bool(validator())
        if isinstance(validator, bool):
            return validator
        return bool(tenant_context.has_minimum_context())

    def _build_progressive_tenant_context(
        self,
        *,
        tenant_id: str,
        channel: str,
        text: str,
        evidence: object | None,
    ) -> ProgressiveTenantClinicalContext:
        normalized = self._normalize(text)
        symptom_summary = self._extract_operational_signals(normalized)
        if any(signal in normalized for signal in self._MARGIN_SIGNALS):
            symptom_summary = list(dict.fromkeys(symptom_summary + ["incertidumbre de rentabilidad"]))

        taxonomic_identity = self._classify_taxonomic_response(normalized)

        documents_requested: list[str] = []
        if evidence is None:
            documents_requested = ["ventas", "costos", "precios", "caja"]

        return ProgressiveTenantClinicalContext(
            tenant_id=tenant_id,
            channel=channel,
            business_identity=ProgressiveBusinessIdentity(
                display_name=taxonomic_identity.display_name,
                country_code=taxonomic_identity.country_code,
                industry_hint=taxonomic_identity.industry_hint,
                taxonomy_phase=taxonomic_identity.taxonomy_phase,
            ),
            symptom_summary=symptom_summary,
            documents_requested=documents_requested,
        )

    def _classify_taxonomic_response(self, normalized: str) -> ProgressiveBusinessIdentity:
        organism_patterns: tuple[tuple[tuple[str, ...], str], ...] = (
            (("distribuidora", "distribucion", "distribuimos", "logistica", "ruta", "reparto"), "logistica/distribucion"),
            (("comercio", "local", "minorista", "mayorista", "tienda", "negocio a la calle"), "comercio"),
            (("fabrica", "industria", "fabricamos", "produccion", "taller"), "industria/fabrica"),
            (("servicio", "servicios", "prestamos servicios"), "servicios"),
            (("gastronomia", "restaurant", "restaurante", "bar", "cafeteria"), "gastronomia"),
            (("construccion", "obra", "obras"), "construccion"),
            (("agro", "campo", "agricola", "ganader"), "agro"),
            (("salud", "clinica", "consultorio", "farmacia"), "salud"),
            (("educacion", "escuela", "instituto", "capacitacion"), "educacion"),
        )

        industry_hint: str | None = None
        for patterns, candidate in organism_patterns:
            if any(pattern in normalized for pattern in patterns):
                industry_hint = candidate
                break

        taxonomy_phase = "FASE_0_IDENTIDAD" if industry_hint is not None else None
        country_code = "AR" if taxonomy_phase == "FASE_0_IDENTIDAD" else None

        return ProgressiveBusinessIdentity(
            display_name=self._extract_declared_business_name(normalized),
            country_code=country_code,
            industry_hint=industry_hint,
            taxonomy_phase=taxonomy_phase,
        )

    def _extract_declared_business_name(self, normalized: str) -> str | None:
        markers = ("se llama ", "nos llamamos ", "mi negocio es ", "la empresa es ")
        for marker in markers:
            if marker in normalized:
                candidate = normalized.split(marker, 1)[1].strip()
                if candidate:
                    return candidate.split(",", 1)[0].split(".", 1)[0].strip() or None
        return None

    def _merge_progressive_context(
        self,
        *,
        tenant_id: str,
        previous: ProgressiveTenantClinicalContext | None,
        current: ProgressiveTenantClinicalContext,
    ) -> ProgressiveTenantClinicalContext:
        if previous is None or previous.tenant_id != tenant_id:
            return current

        merged_symptoms = list(dict.fromkeys(previous.symptom_summary + current.symptom_summary))
        merged_documents = list(dict.fromkeys(previous.documents_requested + current.documents_requested))

        prev_identity = previous.business_identity
        curr_identity = current.business_identity
        merged_identity = ProgressiveBusinessIdentity(
            display_name=prev_identity.display_name or curr_identity.display_name,
            country_code=prev_identity.country_code or curr_identity.country_code,
            industry_hint=prev_identity.industry_hint or curr_identity.industry_hint,
            # taxonomy_phase is preserved across turns once established.
            taxonomy_phase=prev_identity.taxonomy_phase or curr_identity.taxonomy_phase,
        )

        return ProgressiveTenantClinicalContext(
            tenant_id=current.tenant_id,
            channel=current.channel,
            business_identity=merged_identity,
            symptom_summary=merged_symptoms,
            documents_requested=merged_documents,
        )
