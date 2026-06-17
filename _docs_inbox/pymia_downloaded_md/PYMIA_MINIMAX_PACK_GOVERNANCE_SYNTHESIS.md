# PymIA — Pack Governance V1: síntesis útil de Minimax

## Veredicto

La sexta respuesta de Minimax es estructuralmente fuerte.

Cierra la base que sostiene las cinco piezas previas:

```text
1. EpistemicState
2. AssertionCandidate
3. OperatorConfirmation
4. OwnerSemanticClaim + TensionReport
5. DominantUnknown + MinimumEvidencePath
6. Pack Governance
```

Sin governance de packs, el resto del kernel queda expuesto a conocimiento no auditado, cambios silenciosos y packs zombies.

## Decisión central

Un pack no es código runtime.

Un pack es un artefacto de conocimiento versionado, auditado y gobernado.

```text
El kernel no contiene conocimiento duro.
El kernel carga, valida, rechaza y usa packs gobernados.
```

## Regla nuclear

```text
Un pack no auditado no puede participar en diagnóstico asistido.
```

Esto no es una regla administrativa.

Es una regla ontológica del sistema:

```text
si el pack no está VALIDATED, no existe para diagnóstico.
```

## Principios rectores aprovechables

```text
1. Pack no es código; es conocimiento gobernado.
2. Kernel no contiene conocimiento duro.
3. Pack no auditado no participa en diagnóstico.
4. Packs no se borran; transicionan.
5. Cambio de pack no invalida silenciosamente trabajo confirmado.
```

## Metadata obligatoria

Todo pack debe declarar:

```yaml
PackMetadata:
  pack_id: string
  pack_kind:
    - formula
    - pathology
    - evidence_type
    - question_template
    - sector
    - macro_context
    - regulatory
    - reconciliation_rules
  pack_version: semver
  format_version: string

  author_id: string
  organization: optional[string]
  created_at: datetime
  last_modified_at: datetime
  modification_history: list[ModificationEntry]
  source_evidence: list[SourceRef]

  scope: dict
  applies_to_pathologies: list[PathologyRef]
  applies_to_evidence_types: list[EvidenceTypeRef]
  applies_to_question_topics: list[string]

  valid_from: optional[date]
  valid_until: optional[date]
  audit_status: PackState
  audit_validity_period: duration
  audit_history: list[AuditEntry]
  owner_id: string
  contact: optional[string]

  content_hash: string
  signature: optional[Signature]
  dependencies: list[PackRef]
  conflicts_with: list[PackRef]
  schema_uri: string
```

## Estados del pack

Sólo un estado participa en diagnóstico:

```text
VALIDATED
```

Estados útiles:

```text
DRAFT
CANDIDATE
VALIDATED
DEPRECATED
SUPERSEDED
REJECTED
RECALLED
ORPHANED
STALE_AUDIT
ARCHIVED
```

Regla:

```text
El kernel sólo usa packs VALIDATED para producir nuevas candidates diagnósticas.
```

## Transiciones

Las transiciones deben ser eventos append-only:

```text
DRAFT -> CANDIDATE
CANDIDATE -> VALIDATED
CANDIDATE -> REJECTED
VALIDATED -> DEPRECATED
VALIDATED -> SUPERSEDED
VALIDATED -> RECALLED
VALIDATED -> STALE_AUDIT
VALIDATED -> ORPHANED
cualquier estado -> ARCHIVED
```

No hay borrado silencioso.

## Versionado

Semver con semántica PymIA:

```text
MAJOR = cambio incompatible.
MINOR = adición backward-compatible.
PATCH = fix sin cambio semántico.
```

### MAJOR

Puede afectar:

```text
precondiciones de fórmulas
reglas de reconciliación
evidence types
question template slots
patrones de patologías
```

Consecuencia:

```text
candidates existentes se marcan para re-evaluación
confirmations existentes se flaggean para revisión humana
```

### MINOR

Agrega conocimiento sin romper lo anterior.

```text
nuevas fórmulas
nuevas patologías
nuevas preguntas
```

### PATCH

No cambia comportamiento.

```text
typos
comentarios
formato
metadatos no semánticos
```

## Cinco capas de validación

### L1 — Estructural

Valida:

```text
metadata obligatoria
pack_id namespaced
semver válido
schema compatible
content_hash
dependencies conocidas
DAG sin ciclos
```

### L2 — Integridad referencial

Valida:

```text
pathologies referenciadas existen
evidence types existen
fórmulas declaran precondiciones conocidas
question templates referencian variables existentes
```

### L3 — Semántica

Valida:

```text
toda fórmula tiene precondiciones
toda pathology tiene peso válido
todo template tiene slot y expected_response_type
no hay duplicados
no hay firmas patológicas duplicadas
sanity checks de valores extremos
```

### L4 — Dominio

Valida:

```text
ejecución sobre evidencia sintética
salidas plausibles
consistencia cross-pack
distribución razonable de weights
```

### L5 — Auditoría humana

Un auditor humano firma:

```text
corrección semántica
base empírica
calidad de templates
procedencia de fuentes
sign_off
```

Regla de promoción:

```text
DRAFT -> CANDIDATE requiere L1 + L2
CANDIDATE -> VALIDATED requiere L3 + L4 + L5
```

## Condiciones de rechazo

Un pack se rechaza si:

```text
RJ1 falla L1
RJ2 falla L2
RJ3 falla L3
RJ4 falla L4
RJ5 falla L5
RJ6 provenance ausente o débil
RJ7 conflicto con pack VALIDATED sin reconciliación
RJ8 envejecido antes de uso sin re-auditoría
```

Pack rechazado:

```text
permanece en registry
no se carga
conserva rejection_reason
puede reenviarse como nueva versión
```

## Deprecación

Deprecación = fin de vida planificado.

```text
DEPRECATED no debe crear nuevas candidates si existe sucesor VALIDATED.
Candidates existentes no se invalidan.
Kernel emite warning.
```

Después de grace period:

```text
DEPRECATED -> SUPERSEDED
```

## Recall

Recall = retiro por error descubierto.

Severidades:

```text
low
medium
high
critical
```

Efectos:

```text
low = log only
medium = affected candidates -> STALE en próxima vista
high = candidates -> STALE + re-evaluación + reconfirmación
critical = invalidar candidates/confirmations afectadas y rebuild explícito
```

Regla:

```text
Recall nunca se resuelve silenciosamente.
```

## Packs zombies

Zombie pack:

```text
pack técnicamente cargable,
sin owner,
sin auditoría vigente,
sin mantenimiento,
pero todavía influyendo diagnósticos.
```

Defensas:

```text
1. re-auditoría periódica obligatoria
2. owner chain
3. valid_until / audit_validity_period
4. registry scrubbing
5. linter en cada load
6. audit_history visible
7. no updates in-place
8. warnings explícitos para DEPRECATED / STALE_AUDIT / ORPHANED
```

## Conexión con AssertionCandidate

Toda candidate debe registrar:

```text
formula_id
pack_id
pack_version
```

Si el pack cambia:

```text
MAJOR -> candidate STALE / re-evaluation required
MINOR -> candidate puede seguir si compatible
PATCH -> no cambia semántica
RECALLED -> candidate afectada se flaggea según severidad
```

## Conexión con TensionReport

Las reglas de reconciliación vienen de packs:

```text
PathologyPack
ReconciliationRulesPack
```

Todo TensionReport debe registrar:

```text
pathology_id
pack_id
pack_version
rules_applied
evaluation_trace
```

## Conexión con DominantUnknown

DominantUnknown depende de packs para:

```text
pathology_weight
question_uplift
evidence_type linkage
reconciliation rules
```

Si cambia el pack:

```text
DominantUnknown y MinimumEvidencePath deben recomputarse.
```

## Conexión con OwnerSemanticClaim

Los vocabularios de tags vienen de packs:

```text
subject_tags
pathology_tags
question_topics
```

Si cambia vocabulario:

```text
claims existentes no se invalidan automáticamente
operador puede re-taggear
```

## Conexión con EpistemicState

EpistemicState debe registrar snapshot de:

```text
pack_versions
pack_states
kernel_version
```

Regla:

```text
Dos EpistemicStates con pack_versions distintas son artefactos distintos.
```

## Qué pasa si cambia un pack después de producir candidates o confirmations

### MINOR

```text
candidates existentes siguen funcionando
nuevas candidates pueden usar nuevos recursos
```

### MAJOR

```text
viejo pack -> SUPERSEDED
candidates viejas -> re-evaluation required
confirmations previas -> flag para revisión del operador
no invalidación silenciosa
```

### DEPRECATED con sucesor

```text
nuevas candidates prefieren sucesor
viejas siguen con warning
migración requiere path declarado
```

### RECALLED medium/high

```text
pack se descarga
candidates afectadas -> STALE
confirmations afectadas -> flag
operador debe revisar
```

### RECALLED critical

```text
candidates y confirmations afectadas se invalidan
EpistemicState debe reconstruirse
operador debe re-confirmar explícitamente
```

### Pack desaparecido

Esto es violación de política.

```text
packs no se eliminan
se deprecatean, supersedean o recallean
```

Si falta del registry:

```text
caso -> STALE_PACK_MISSING
kernel refuses to load referencias afectadas
```

## Decisiones candidatas para repo

```text
1. Pack es artefacto de conocimiento, no código runtime.
2. Kernel no contiene conocimiento duro.
3. Sólo packs VALIDATED participan en diagnóstico asistido.
4. Packs no se borran: transicionan.
5. Todo pack tiene metadata, owner, hash, versionado y audit history.
6. DRAFT -> CANDIDATE requiere L1+L2.
7. CANDIDATE -> VALIDATED requiere L3+L4+L5.
8. MAJOR fuerza re-evaluación de candidates.
9. Recall high/critical fuerza revisión explícita del operador.
10. No hay updates silenciosos ni cuerpo mutable in-place.
11. Zombie packs se bloquean por auditoría, owner y registry scrubbing.
12. EpistemicState registra snapshot de pack_versions.
13. Confirmations previas no se invalidan silenciosamente por cambio de pack.
14. Linter corre en cada load, no sólo en alta inicial.
```

## Constitución conceptual cerrada

Con esta sexta pieza, el kernel epistémico V1 queda conceptualmente cerrado:

```text
EpistemicState
AssertionCandidate
OperatorConfirmation
OwnerSemanticClaim + TensionReport
DominantUnknown + MinimumEvidencePath
Pack Governance
```

## Advertencia estratégica

No conviene seguir agregando contratos conceptuales.

El próximo trabajo debería ser de consolidación:

```text
reducir las seis piezas a una decisión compacta
separar kernel vs boundary vs tooling
definir qué ya existe en repo
definir qué falta
evitar implementación prematura
```

## Frase de cierre

```text
El conocimiento de dominio es enchufable, pero no descartable.
Debe ser versionado, auditado, trazable y revocable.
```
