# PymIA — FichaPrimaria V1: síntesis útil de Minimax

## Veredicto

La respuesta de Minimax es correcta y corrige el mapa conceptual.

Las seis piezas anteriores describen lo que PymIA hace durante el diagnóstico asistido.

La FichaPrimaria describe lo que el caso es antes de que el sistema empiece a diagnosticar.

Sin FichaPrimaria sellada no hay caso gobernable.

Hay:

```text
un Excel suelto
un dueño hablando
un operador interpretando
```

Con FichaPrimaria hay:

```text
un expediente inicial mínimo
un case_id gobernable
un alcance explícito
un período definido
una autorización registrada
un operador vinculado
una PyME identificada
una primera verdad auditable
```

## Clasificación correcta

La FichaPrimaria no es kernel puro.

Tampoco es tooling del operador.

Clasificación correcta:

```text
boundary artifact con contrato enforced por el kernel
```

Traducción:

```text
El contenido lo captura el operador.
El contrato lo exige el kernel.
El sellado vuelve la ficha ancla del caso.
```

## Decisión central

```text
Sin FichaPrimaria sellada, PymIA no debe crear un caso diagnóstico pleno.
```

Antes del sellado, el estado correcto es:

```text
INTAKE
```

Después del sellado:

```text
OPEN
```

## Cadena corregida

```text
Owner llega con problema
  -> Operator hace intake
  -> FichaPrimaria DRAFT
  -> validación de obligatorios + consentimiento
  -> FichaPrimaria SEALED
  -> case_id creado
  -> evidencia inicial adjunta
  -> OwnerSemanticClaim inicial
  -> StructuredEvidence
  -> TensionReport
  -> AssertionCandidate
  -> DominantUnknown
  -> OperatorConfirmation
  -> EpistemicState
  -> Reporte
```

## Regla nuclear

```text
La FichaPrimaria convierte una conversación y un Excel en un caso gobernable.
```

## Campos mínimos rescatables

### Identidad del expediente

```yaml
ficha_id: string
case_id: string
created_at: datetime
sealed_at: optional[datetime]
seal_status: DRAFT | SEALED
schema_version: string
```

### Identidad de la PyME

```yaml
pyme_legal_name: string
pyme_tax_id: string
pyme_sector: optional[string]
pyme_company_size: micro | pequeña | mediana | no_declarada
pyme_geographic_scope: optional[string]
pyme_fiscal_regime: optional[string]
pyme_data_residency: AR | OTHER
```

### Identidad de quien habla

```yaml
owner_legal_name: string
owner_role_in_pyme:
  - titular
  - socio
  - gerente
  - apoderado
  - familiar
  - otro
owner_tax_id: optional[string]
owner_contact_channel: dict
owner_authority_level:
  - plena
  - parcial
  - solo_informativo
owner_consent_signed: bool
```

### Identidad de quien opera

```yaml
operator_id: string
operator_role:
  - contador
  - asesor
  - consultor
  - auditor_interno
  - equipo_smartpyme
operator_authority_level:
  - READ_ONLY
  - CONFIRM_ROUTINE
  - CONFIRM_CRITICAL
  - ARBITRATE_CONTRADICTION
operator_delegated_by: optional[string]
operator_org_affiliation: optional[string]
```

### Problema inicial

```yaml
problem_statement: string
problem_category: list[string]
problem_urgency_self_reported:
  - low
  - medium
  - high
problem_temporal_horizon:
  - ahora
  - proximos_3_meses
  - proximos_12_meses
  - largo_plazo
  - exploratorio
problem_scope:
  - tema_unico
  - temas_multiples
  - relevamiento_completo
```

### Período bajo análisis

```yaml
analysis_period_start: date
analysis_period_end: date
analysis_period_kind:
  - historico
  - corriente
  - proyeccion
  - mixto
analysis_period_basis:
  - ejercicio_fiscal
  - año_calendario
  - ultimos_12_meses
  - ultimos_3_meses
  - custom
```

### Evidencia inicial

```yaml
initial_evidence: list[EvidenceRef]
initial_evidence_provenance: dict[EvidenceRef, string]
initial_evidence_sufficiency_self_assessment:
  - suficiente
  - parcial
  - minima
  - no_se
expected_evidence_outstanding: list[EvidenceTypeRef]
```

### Alcance

```yaml
case_scope: list[string]
case_out_of_scope: list[string]
case_pack_versions_at_open: dict[PackKind, semver]
case_pack_versions_relevant: list[PackRef]
```

### Autorización

```yaml
authorization_status:
  - aprobada
  - pendiente
  - limitada
  - rechazada
authorization_scope_limitations: list[string]
authorization_data_use:
  - solo_diagnostico
  - diagnostico_y_benchmark
  - diagnostico_y_agregado
  - custom
authorization_third_party_sharing: bool
authorization_expiration: optional[date]
authorization_signed_at: optional[datetime]
authorization_signature_method:
  - presencial
  - electronica
  - verbal_registrada
  - pendiente
```

### Estado inicial

```yaml
case_status_initial: INTAKE | OPEN
expected_first_diagnostic_window: optional[date]
internal_notes: optional[string]
```

## Inmutabilidad post-sellado

Inmutables después de `SEALED`:

```text
identidad PyME
owner binding
período
alcance
autorización
pack_versions_at_open
```

Extensiones posibles vía artifact separado:

```text
FichaExtension
```

Ejemplos:

```text
agregar operador
extender período
modificar scope
renovar autorización
```

Regla:

```text
No se edita silenciosamente la FichaPrimaria sellada.
Se agrega extensión append-only.
```

## Qué errores evita

```text
E_NO_CASE_GOVERNANCE
E_OPERATOR_HIJACK
E_CONSENT_VIOLATION
E_SCOPE_RUNAWAY
E_PERIOD_MIX
E_AUTHORITY_DRIFT
E_PACK_SWAP
E_OWNER_MISIDENTIFICATION
E_DATA_RESIDENCY_BREACH
E_INTENT_MISREAD
E_OWNER_REPLACEMENT
```

## Conexión con OwnerSemanticClaim

La FichaPrimaria define:

```text
quién puede hablar como dueño
qué autoridad tiene
qué período se está mirando
cuál es el problema inicial
qué claims quedan dentro o fuera de alcance
```

El `problem_statement` de la ficha puede convertirse en el primer `OwnerSemanticClaim` del caso:

```text
owner_opening_statement
```

## Conexión con StructuredEvidence

La ficha define:

```text
case_id
período
identidad PyME
evidencia inicial
autorización de uso
residencia de datos
```

Toda evidencia sin case_id queda:

```text
huérfana o en quarantine
```

## Conexión con AssertionCandidate

La ficha filtra candidates por:

```text
scope
period
pack_versions_at_open
operator authority
case status
```

Una candidate fuera del alcance pactado no debería entrar silenciosamente.

Debe:

```text
filtrarse
o flaggearse para ampliar scope mediante FichaExtension
```

## Conexión con OperatorConfirmation

La ficha valida:

```text
operator_id
operator_authority_level
delegation chain
authorization vigente
case abierto
```

Sin ficha no hay autoridad verificable para confirmar.

## Conexión con EpistemicState

La ficha es cabecera del EpistemicState:

```text
case_id
pyme identity
owner identity
operator identity
analysis_period
authorization_status
pack_versions_at_open
case_scope
```

Dos EpistemicStates con distinta ficha o distinta extensión no son exactamente el mismo artefacto.

## Qué NO debe contener

La FichaPrimaria no debe contener:

```text
scores
diagnostic statements
tension reports
dominant unknown
recovery questions
operator conclusions
LLM-generated content
forecasts
benchmarks
fórmulas aplicadas
intuición diagnóstica del operador
```

Regla:

```text
La FichaPrimaria abre el caso.
No diagnostica el caso.
```

## Test rápido

```text
Si un campo alimenta directamente un output diagnóstico, no pertenece a la FichaPrimaria.
Si un campo no gobierna identidad, alcance, autorización, período, actor o evidencia inicial, probablemente sobra.
```

## Riesgos de no tener FichaPrimaria

```text
identidad de caso a la deriva
vacío de autoridad
violación de consentimiento
explosión de scope
confusión de períodos
pack swap silencioso
owner mal identificado
errores repetidos de intake
imposibilidad de auditoría
exposición ética/legal
pérdida de primera verdad
drift de operador
```

## Constitución corregida

La constitución conceptual de PymIA V1 queda:

```text
0. FichaPrimaria / PrimaryCaseFile
1. EpistemicState
2. AssertionCandidate
3. OperatorConfirmation
4. OwnerSemanticClaim + TensionReport
5. DominantUnknown + MinimumEvidencePath
6. Pack Governance
```

Pero la pieza cero no es “otra feature”.

Es el contenedor raíz del caso.

## Decisión candidata para repo

```text
PrimaryCaseFile es un boundary artifact kernel-enforced.
Sin PrimaryCaseFile SEALED no hay case_id diagnóstico pleno.
La FichaPrimaria es inmutable en sus campos críticos.
Cambios posteriores requieren FichaExtension append-only.
```

## Frase de cierre

```text
La FichaPrimaria es el parto del caso.
Sin ella, PymIA no tiene caso: tiene insumos sueltos.
```
