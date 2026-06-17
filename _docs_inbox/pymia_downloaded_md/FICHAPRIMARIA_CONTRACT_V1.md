# FICHAPRIMARIA_CONTRACT_V1

> Pieza 0 de la constitución del kernel PymIA V1.
> Boundary artifact con contrato enforced por el kernel.

---

## Clasificación arquitectónica

La FichaPrimaria **no es kernel puro**: captura hechos del mundo (CUIT, dueño, sector, período, autorización, evidencia inicial).

La FichaPrimaria **no es formulario libre del operador**: el kernel impone estructura, obligatoriedad, sellado, inmutabilidad, `case_id`, scope, período, autorización, operator binding y `pack_versions_at_open`.

La FichaPrimaria es un **boundary artifact con contrato kernel-enforced**. El contenido lo aporta el operador en la interfaz con el dueño; la estructura y las reglas las enforcea el kernel. Una vez sellada, ciertos campos son inmutables.

**Analogía precisa**: la FichaPrimaria es al caso lo que el `case_id` es al sistema de archivos. No es la lógica, pero sin él no hay nada a lo que atar la lógica. Es el *root directory* del caso.

**Principio rector**:

> La FichaPrimaria no diagnostica: funda el caso.
> PymIA no empieza cuando calcula. PymIA empieza cuando sella un caso gobernable.

---

## Regla de existencia

**Sin FichaPrimaria SEALED, no hay diagnóstico asistido. Solo puede existir INTAKE.**

Concretamente:

- No hay `AssertionCandidate` evaluable.
- No hay `OperatorConfirmation` aceptable.
- No hay `EpistemicState` firmable.
- No hay reporte owner-facing.
- No hay `DominantUnknown` computable (no hay blocked candidates sin evidencia evaluada).
- No hay `TensionReport` (no hay evidencia contra qué confrontar).

Esta regla es absoluta. Cualquier atajo —"ya tenemos Excel, abramos caso al vuelo"— está prohibido. El caso nace con el sellado, no antes.

---

## Campos mínimos

La FichaPrimaria se divide en diez bloques. El kernel rechaza el sellado si falta cualquiera de los obligatorios, o si el consentimiento no está firmado.

### Identidad del expediente
- `ficha_id` — UUID de esta FichaPrimaria.
- `case_id` — UUID del caso. Se crea al sellar; antes de sellar, el caso está en `INTAKE` y no tiene id.
- `created_at`, `sealed_at` — timestamps.
- `seal_status: 'DRAFT' | 'SEALED'` — una vez `SEALED`, ciertos campos son inmutables.
- `schema_version` — versión del schema de FichaPrimaria, para evolución futura.

### Identidad de la PyME (inmutable post-sellado)
- `pyme_legal_name: str`
- `pyme_tax_id: str` — CUIT u otro identificador fiscal.
- `pyme_sector: Optional[str]` — declarado por el operador, no asumido.
- `pyme_company_size: 'micro' | 'pequeña' | 'mediana' | 'no_declarada'`
- `pyme_geographic_scope: Optional[str]` — provincia/región principal.
- `pyme_fiscal_regime: Optional[str]` — régimen tributario. Crítico en AR.
- `pyme_data_residency: 'AR' | 'OTHER'` — soberanía de datos.

### Identidad de quien habla (el dueño)
- `owner_legal_name: str`
- `owner_role_in_pyme: 'titular' | 'socio' | 'gerente' | 'apoderado' | 'familiar' | 'otro'`
- `owner_tax_id: Optional[str]`
- `owner_contact_channel: dict` — al menos un canal verificable.
- `owner_authority_level: 'plena' | 'parcial' | 'solo_informativo'` — qué decisiones puede tomar el dueño sobre el caso.
- `owner_consent_signed: bool` — consentimiento personal del firmante.

### Identidad de quien opera (el operador)
- `operator_id`
- `operator_role: 'contador' | 'asesor' | 'consultor' | 'auditor_interno' | 'equipo_smartpyme'`
- `operator_authority_level: 'READ_ONLY' | 'CONFIRM_ROUTINE' | 'CONFIRM_CRITICAL' | 'ARBITRATE_CONTRADICTION'`
- `operator_delegated_by: Optional[operator_id]`
- `operator_org_affiliation: Optional[str]`

### El problema que trae el dueño
- `problem_statement: str` — la pregunta o preocupación en palabras del dueño.
- `problem_category: list[str]` — tags del catálogo (e.g., `['cash_flow', 'cobranza', 'pricing']`).
- `problem_urgency_self_reported: 'low' | 'medium' | 'high'` — a juicio del operador.
- `problem_temporal_horizon: 'ahora' | 'proximos_3_meses' | 'proximos_12_meses' | 'largo_plazo' | 'exploratorio'`
- `problem_scope: 'tema_unico' | 'temas_multiples' | 'relevamiento_completo'`

### Período bajo análisis (inmutable post-sellado, salvo FichaExtension)
- `analysis_period_start: date`
- `analysis_period_end: date`
- `analysis_period_kind: 'historico' | 'corriente' | 'proyeccion' | 'mixto'`
- `analysis_period_basis: 'ejercicio_fiscal' | 'año_calendario' | 'ultimos_12_meses' | 'ultimos_3_meses' | 'custom'`

### Evidencia inicial recibida
- `initial_evidence: list[EvidenceRef]` — referencias a evidencia ya cargada.
- `initial_evidence_provenance: dict[EvidenceRef, str]` — fuente/origen de cada pieza.
- `initial_evidence_sufficiency_self_assessment: 'suficiente' | 'parcial' | 'minima' | 'no_se'`
- `expected_evidence_outstanding: list[EvidenceTypeRef]` — qué se espera conseguir.

### Alcance del caso (inmutable post-sellado)
- `case_scope: list[str]` — áreas que se van a evaluar (e.g., `['liquidez', 'rentabilidad', 'cobranza']`).
- `case_out_of_scope: list[str]` — áreas explícitamente fuera.
- `case_pack_versions_at_open: dict[PackKind, semver]` — snapshot de packs `VALIDATED` al abrir. Es la línea base contra la que se detecta "pack swap mid-case".
- `case_pack_versions_relevant: list[PackRef]` — qué packs van a participar.

### Autorización (dos consentimientos, registrados por separado)

**Consentimiento de la PyME (persona jurídica)**:
- `pyme_consent_signed: bool` — la persona jurídica consintió el análisis.
- `pyme_consent_signed_by: str` — `legal_name` de quien firmó en representación de la PyME.
- `pyme_consent_authority_basis: 'titular' | 'socio' | 'apoderado' | 'representante_legal' | 'otro'` — bajo qué autoridad firmó.
- `pyme_consent_signed_at: Optional[datetime]`
- `pyme_consent_signature_method: 'presencial' | 'electronica' | 'verbal_registrada' | 'pendiente'`

**Consentimiento del dueño (persona física, en su nombre)**:
- `owner_consent_signed: bool` — ya declarado arriba; se reitera acá para claridad.
- `owner_consent_signed_at: Optional[datetime]`
- `owner_consent_signature_method: 'presencial' | 'electronica' | 'verbal_registrada' | 'pendiente'`

**Alcance de la autorización**:
- `authorization_status: 'aprobada' | 'pendiente' | 'limitada' | 'rechazada'`
- `authorization_scope_limitations: list[str]`
- `authorization_data_use: 'solo_diagnostico' | 'diagnostico_y_benchmark' | 'diagnostico_y_agregado' | 'custom'`
- `authorization_third_party_sharing: bool`
- `authorization_expiration: Optional[date]`

**Regla de sellado**: `pyme_consent_signed == true` **y** `owner_consent_signed == true` **y** `authorization_status in {'aprobada', 'limitada'}` son requisitos simultáneos. Sin esto, no se sella. El consentimiento personal del dueño y el consentimiento de la PyME no son intercambiables: ambos deben estar registrados por separado.

### Estado inicial
- `case_status_initial: 'INTAKE' | 'OPEN'` — `INTAKE` antes del sellado, `OPEN` después.
- `expected_first_diagnostic_window: Optional[date]` — cuándo se espera primer avance.
- `internal_notes: Optional[str]` — notas del operador, explícitamente etiquetadas como no diagnósticas.

### Reglas de inmutabilidad post-sellado
- **Inmutables**: identidad PyME, owner binding, período, alcance, autorización, `pack_versions_at_open`, consentimientos firmados.
- **Extensibles vía `FichaExtension` artifact separado**: agregar operator, extender período, modificar scope, actualizar autorización, agregar consentimiento adicional. La extensión es append-only y se referencia desde la FichaPrimaria original.

---

## Errores que evita

La FichaPrimaria es firewall de intake. Evita errores sistémicos que de otra manera aparecerían aguas abajo.

- **E_NO_CASE_GOVERNANCE** — sin Ficha sellada, no hay caso gobernable. No se puede adjuntar evidencia, candidates, o confirmations a una unidad coherente.
- **E_OPERATOR_HIJACK** — sin operator binding explícito, cualquier persona con acceso al sistema podría confirmar candidates.
- **E_CONSENT_VIOLATION** — sin consent firmado y registrado, el sistema opera sobre datos de una PyME sin base legal (Ley 25.326 en AR).
- **E_SCOPE_RUNAWAY** — sin `case_scope` explícito, el caso puede crecer a cubrir todo y nunca terminar.
- **E_PERIOD_MIX** — sin `analysis_period` definido, evidencia de distintos períodos se mezcla.
- **E_AUTHORITY_DRIFT** — sin `operator_authority_level`, un operador junior podría confirmar candidates de alta criticidad.
- **E_PACK_SWAP** — sin `case_pack_versions_at_open` registrado, un admin podría cambiar un pack mid-case y alterar silenciosamente todos los diagnósticos.
- **E_OWNER_MISIDENTIFICATION** — quien habla no siempre es quien decide. Sin rol explícito, el sistema podría tomar instrucciones de un no autorizado.
- **E_DATA_RESIDENCY_BREACH** — sin `pyme_data_residency` y `authorization_third_party_sharing`, los datos podrían terminar en lugares no autorizados.
- **E_INTENT_MISREAD** — el dueño puede llegar preguntando por precios cuando en realidad está preocupado por caja. Sin `problem_statement` explícito, el sistema puede optimizar para la pregunta equivocada.
- **E_DOUBLE_CONSENT_CONFUSION** — sin distinguir consentimiento PyME de consentimiento owner, no se sabe qué acto legal cubre qué uso de datos.
- **E_DUAL_AUTHORITY_GAP** — sin registrar quién firmó el consentimiento PyME y bajo qué autoridad, una revocación o disputa posterior no tiene ancla.

---

## Qué NO debe contener la FichaPrimaria

Esta es la disciplina más fina. La FichaPrimaria no es diagnóstico. Si se le cuela contenido diagnóstico, el caso empieza "contaminado".

**Prohibido**:
- **Scores** — ni "salud: 7/10" ni "riesgo: alto" ni "tracción: media".
- **Statements diagnósticos** — "tiene problemas de liquidez", "el negocio es viable", "el margen está apretado".
- **TensionReports** — "hay contradicción entre lo que dice el dueño y los datos".
- **DominantUnknown** — no se puede computar sin blocked candidates, y no hay blocked candidates sin evidencia evaluada.
- **Recovery questions** — emergen de blocked candidates.
- **Conclusiones del operador** — el juicio del operador se registra en OperatorConfirmation, no en la Ficha.
- **Contenido generado por LLM** — la Ficha es tipeada por humanos y firmada por humanos. El LLM no escribe nada en ella.
- **Forecasts o proyecciones** — son producto del ForecastPack.
- **Benchmarks** — "esta PyME está bajo el promedio del sector" es derivado, no intake.
- **Fórmulas aplicadas** — no hay cálculo en la Ficha. Es data, no derivación.
- **Histórico del dueño** — "el dueño ya tuvo un caso similar en 2023" se registra como OwnerSemanticClaim posterior si surge en conversación, no como campo de Ficha.
- **Intuiciones del operador sobre el caso** — se expresan en `internal_notes` (etiquetadas como no diagnósticas) o como claims propios, no como hechos de la Ficha.

**Test rápido de validación**: si un campo de la FichaPrimaria desaparece y nada en el sistema cambia, ese campo sobra. Si un campo alimenta directamente un output diagnóstico, ese campo es un bug.

---

## Conexiones con las otras piezas

### Con `OwnerSemanticClaim`
- **Owner binding**: solo el `owner_id` registrado puede emitir OwnerSemanticClaim con `claimant_type: 'owner'`. Si habla otro, se registra con `claimant_type: 'third_party_observed'`.
- **Period constraint**: las `OwnerProposition.time_window` deben intersectar con `analysis_period_start..end`.
- **Problem anchor**: el `problem_statement` se registra como la **primera** `OwnerSemanticClaim` del caso, con `claimant_type: 'owner_opening_statement'`. Esta claim es la ancla temática.
- **Authority level**: si `owner_authority_level == 'solo_informativo'`, las claims del dueño se registran pero no pueden pesar en decisiones críticas.

### Con `StructuredEvidence`
- **Case binding**: toda evidencia referencia `case_id`. Evidencia huérfana se rechaza o quarantine.
- **Period filtering**: al cargar evidencia, el kernel valida que `evidence.time_window` intersecte con `analysis_period`. Evidencia fuera se marca `out_of_period: true`.
- **Initial evidence set**: la `initial_evidence` de la Ficha es la línea base. El primer EpistemicState se construye desde ahí.
- **PyME identity anchoring**: `pyme_tax_id` es la clave de cross-reference con evidencia externa (resúmenes bancarios, facturas, declaraciones juradas).
- **Data residency constraint**: `pyme_data_residency` define dónde puede almacenarse la evidencia.
- **Authorization gate**: `authorization_data_use` define para qué puede usarse.

### Con `AssertionCandidate`
- **Scope filtering**: `case_scope` y `case_out_of_scope` definen qué pathologies son elegibles.
- **Pack anchoring**: las primeras candidates se evalúan contra `case_pack_versions_at_open`. Candidate que referencia pack fuera de snapshot se rechaza.
- **Authority gating**: `operator_authority_level` determina qué criticality de candidates el operador puede confirmar.
- **Period alignment**: `proposition.time_window` debe intersectar `analysis_period`.

### Con `OperatorConfirmation`
- **Operator binding**: cada confirmation referencia `operator_id`. El kernel verifica que está registrado en la Ficha (o en una FichaExtension válida).
- **Authority inheritance**: `operator_authority_level` de la Ficha es la base. Una FichaExtension puede elevar autoridad, no reducir.
- **Delegation chain**: `operator_delegated_by` debe apuntar a otro operador registrado.
- **Authorization recency**: si `authorization_expiration` pasó, las OperatorConfirmation se rechazan hasta renovación.

### Con `EpistemicState`
- **Identity inheritance**: el primer EpistemicState lleva los datos de identidad de la Ficha: `pyme_legal_name`, `pyme_tax_id`, `owner_id`, `operator_id`, `analysis_period`.
- **Pack versions baseline**: EpistemicState inicial lleva `pack_versions = case_pack_versions_at_open`. Cambios posteriores disparan re-evaluación.
- **Scope filter**: `case_scope` y `case_out_of_scope` filtran qué propositions entran al EpistemicState.
- **Authorization state**: el EpistemicState registra `authorization_status` al momento de generación.
- **Period anchor**: `analysis_period` viene directo de la Ficha.
- **Initial state transition**: el primer EpistemicState parte de `case_status_initial: 'OPEN'`.

### Con `Pack Governance` (transversal)
- La FichaPrimaria es donde se **congela** la primera versión de `pack_versions_at_open`. Esto crea el anchor contra el cual Pack Governance detecta cambios mid-case.
- Si Pack Governance recall-ea un pack usado en el caso, las candidates producidas con ese pack se re-evalúan; las OperatorConfirmation existentes se flaggean para revisión.
- La FichaPrimaria no es un pack; no se le aplica el lifecycle de pack. Es un artifact de intake, no de conocimiento.

---

## Secuencia correcta de apertura del caso

```
[Owner llega con problema]
        ↓
[Operator hace intake]
        ↓
[FichaPrimaria DRAFT]
        ↓
[Validación de obligatorios + consent firmados (PyME + Owner)]
        ↓
[FichaPrimaria SEALED — inmutables activados]
        ↓
[case_id creado / activado]
        ↓
[OwnerSemanticClaim inicial registrado desde problem_statement]
        ↓
[Evidencia inicial adjunta / estructurada]
        ↓
[Primer formula_evaluated]
        ↓
[Primer AssertionCandidate / TensionReport emitido]
        ↓
[Primer EpistemicState generado]
        ↓
[Caso OPEN con diagnóstico en marcha]
```

**Nota crítica**: la `OwnerSemanticClaim` inicial se registra *antes* de estructurar la evidencia y *antes* del primer `formula_evaluated`. Esto asegura que la voz del dueño quede capturada como punto de partida, no como subproducto del análisis de datos. Si el orden se invierte, el sistema evalúa Excel antes de registrar el relato, y el diagnóstico queda estructuralmente sesgado hacia los datos.

---

## Arquitectura constitucional corregida

La constitución del kernel PymIA V1 tiene **8 piezas en flujo + 1 transversal**:

```
FLUJO (orden lógico de generación):
0. FichaPrimaria                    → funda el caso
1. OwnerSemanticClaim              → voz del dueño
2. StructuredEvidence              → datos crudos
3. TensionReport                   → confrontación dueño-datos
4. AssertionCandidate              → unidades evaluables
5. DominantUnknown + MinEvPath     → qué conviene aprender
6. OperatorConfirmation            → arbitraje humano
7. EpistemicState                  → salida firmable

TRANSVERSAL (gobierna, no fluye):
T. Pack Governance                 → fórmulas, patologías, preguntas, reconciliación, pesos
```

**Lo que el flujo expresa**: la cadena causal de producción de un diagnóstico trazable. Cada pieza nace de la anterior, o la condiciona.

**Lo que la transversalidad expresa**: el conocimiento enchufable no es una pieza final; es la membrana por la que el conocimiento entra y sale en cualquier momento de la cadena, bajo governance.

---

## Frases rectoras

> La FichaPrimaria no diagnostica: funda el caso.

> PymIA no empieza cuando calcula. PymIA empieza cuando sella un caso gobernable.

> Sin FichaPrimaria SEALED no hay diagnóstico asistido. Solo INTAKE.

> El consentimiento de la PyME y el consentimiento del dueño son dos actos distintos. Ambos deben estar firmados.

> La evidencia no entra antes que la voz del dueño. El problem_statement se registra como la primera OwnerSemanticClaim.

> Los packs vigentes al abrir el caso son la línea base. Cambios posteriores disparan re-evaluación; no invalidación silenciosa.

---

## Pie de contrato

Versión: V1
Pieza: 0 (boundary artifact, contrato kernel-enforced)
Estado: borrador corregido
Próximo paso: validación con un caso real antes de promover a rector
