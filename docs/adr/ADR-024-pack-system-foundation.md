# ADR-024: Pack System Foundation

## Estado

**Accepted**

**Fecha:** 2026-06-12

## Contexto

La superauditoría PymIA/SmartPyme (Informe 0) determinó que el kernel de PymIA es sólido, determinístico y fail-closed en sus capas críticas (recepción, evidence gate, diagnostic core, orchestration graph). Los contratos de evidencia y decisión del dueño están bien definidos. La interacción PymIA↔dueño tiene traza completa desde recepción hasta reentry.

Sin embargo, la **frontera kernel ↔ conocimiento enchufable no existe como contrato real**. Las fórmulas, patologías, opciones de anamnesis y mapeos semánticos viven dentro del kernel como código Python hardcodeado:

- `pymia/contracts/formula_contract.py`: 17 fórmulas definidas como dict `SUPPORTED_FORMULAS` dentro del kernel.
- `pymia/smartpyme/anamnesis_fsm.py`: opciones de actividad, rubro, dolor, canales, herramientas hardcodeadas como tuplas Python.
- `pymia/diagnostic_core/core.py`: mapeo fórmula → patología con if/elif dentro del core.

Esto viola la decisión arquitectónica obligatoria de la auditoría:

```
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Sin un sistema formal de packs versionados, cada nueva fórmula, patología, vertical o sector requiere modificar código del core, generando inflación del kernel y acoplamiento a dominio específico.

## Problema

PymIA necesita incorporar conocimiento de dominio (fórmulas financieras, patologías operativas, taxonomías sectoriales, síntomas de rubro, benchmarks, tratamientos operativos, variables organizacionales específicas de textil/gastronómico/comercial/etc.) sin que ese conocimiento contamine el kernel.

Actualmente:

- El kernel hardcodea fórmulas, patologías y opciones de anamnesis.
- No existe un contrato formal para conocimiento enchufable.
- No existe un ciclo de vida para conocimiento de dominio.
- No existe un mecanismo de validación/rechazo de conocimiento externo.
- DiscoveryMemory captura demandas reales pero no tiene canal formal hacia packs.
- LearningMemory se confunde conceptualmente con KnowledgePack.

Sin resolver esto, PymIA no puede escalar a múltiples verticales sin inflar el core y violar sus propios guardrails arquitectónicos.

## Decisión

Se establece el **Pack System** como el mecanismo único y formal para incorporar conocimiento de dominio a PymIA.

**Decisión rectora:**

```
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

**Principios:**

- Todo conocimiento de dominio entra como Pack versionado.
- El kernel solo carga, valida, contrasta, versiona, rechaza y falla cerrado.
- Los packs no mutan estados universales.
- Los packs no modifican anamnesis base ni diagnostic core.
- Los packs no confirman hallazgos ni bypasean evidence sufficiency.
- Los packs no escriben LearningMemory.
- DiscoveryMemory genera PackCandidate, no promueve arquitectura automáticamente.
- LearningMemory aprende operación de factoría, no contiene conocimiento PyME.

## Definición de Pack

Un **Pack** es un artefacto versionado, autocontenido y contract-bound que encapsula conocimiento de dominio enchufable al kernel de PymIA.

Un Pack:

- Es inmutable una vez publicado (nueva versión = nuevo pack).
- Declara explícitamente qué evidencia requiere para operar.
- Declara explícitamente qué ítems expone al kernel.
- Declara explícitamente compatibilidad con versiones de schema y kernel.
- Puede ser cargado, validado, contrastado y rechazado por el kernel sin modificar código del core.
- Nunca confirma hallazgos (solo produce candidates).
- Nunca bypasea evidence sufficiency (solo aporta evidencia si el kernel la solicita).
- Nunca muta estados universales (RECEIVED, BLOCKED, NEEDS_EVIDENCE, etc.).

## Tipos de Pack

### DomainPack

Contiene conocimiento de dominio transversal que no encaja en categorías específicas. Ejemplos: variables organizacionales genéricas, taxonomías operativas transversales, conceptos de dominio PyME.

### KnowledgePack

Contiene conocimiento experto estructurado sobre dominios específicos. Ejemplos: modelos de madurez operativa, frameworks de diagnóstico sectorial, taxonomías de capacidad organizacional.

### FormulaPack

Contiene fórmulas financieras u operativas específicas. Ejemplos: `REN_001` (margen neto), `LIQ_001` (vendido cobrado), `ROT_001` (rotación de stock). Cada fórmula declara inputs requeridos, lógica de cálculo, outputs producidos y patología asociada.

### PathologyPack

Contiene definiciones de patologías operativas. Ejemplos: "margen neto insuficiente", "vendido no cobrado", "rotación anormal". Cada patología declara umbrales, síntomas asociados, fórmulas trigger y tratamientos sugeridos.

### SectorPack

Contiene conocimiento específico de una vertical o rubro. Ejemplos: taxonomía de actividades textiles, síntomas comunes en gastronomía, benchmarks sectoriales, canales de venta típicos por rubro.

### CatalogPack

Contiene catálogos de opciones, mapeos y taxonomías que alimentan la anamnesis base. Ejemplos: opciones de actividad económica, opciones de rubro, opciones de dolor operativo, mapeos texto → taxonomía.

## Responsabilidad del kernel

El kernel de PymIA es responsable de:

### Cargar

- Descubrir packs disponibles en ubicaciones configurables (no hardcoded a `docs/`).
- Cargar metadata de cada pack sin ejecutar lógica del pack.
- Registrar packs cargados en un registry interno.

### Validar

- Verificar que cada pack cumple el contrato de schema (anatomía mínima).
- Verificar que `schema_version` es compatible con la versión del kernel.
- Verificar que `required_evidence` es satisfactible por el evidence chain actual.
- Verificar que `exposed_items` no colisionan con ítems de otros packs activos.
- Rechazar packs que no cumplan validación, sin ejecutarlos.

### Contrastar

- Verificar que los ítems expuestos por un pack no contradicen evidencia existente.
- Verificar que las fórmulas de un FormulaPack no producen resultados inconsistentes con evidencia aportada.
- Verificar que las patologías de un PathologyPack no se confirman sin evidencia suficiente.

### Versionar

- Mantener registro de versiones de packs cargados.
- Permitir coexistencia de múltiples versiones si son compatibles.
- Detectar conflictos de versión entre packs.

### Rechazar

- Rechazar packs que no cumplen contrato de schema.
- Rechazar packs con `schema_version` incompatible.
- Rechazar packs con `status` != ACTIVE.
- Rechazar packs con `required_evidence` insatisfactible.
- Rechazar packs que colisionan con packs activos.
- Loguear motivo de rechazo sin ejecutar lógica del pack.

### Fallar cerrado

- Si un pack falla validación, el kernel continúa operando sin ese pack.
- Si un pack produce output inconsistente durante contraste, el kernel descarta ese output y continúa.
- Si un pack requiere evidencia no disponible, el kernel no ejecuta ese pack y continúa.
- Nunca el kernel adopta lógica de un pack como propia.

## Prohibiciones

Un Pack **NO PUEDE**:

### Mutar estados universales

- No puede cambiar el estado de un `ReceptionRecord` (RECEIVED, BLOCKED, NEEDS_EVIDENCE, etc.).
- No puede alterar el flujo de estados de la anamnesis FSM.
- No puede modificar el estado de evidencia (SATISFIED, NEEDS_MORE_EVIDENCE, BLOCKED).

### Modificar anamnesis base

- No puede agregar, quitar o modificar estados de `anamnesis_fsm.py`.
- No puede alterar las transiciones de la FSM.
- Solo puede aportar opciones (vía CatalogPack) que la anamnesis base consume como parámetro inyectable.

### Modificar diagnostic_core

- No puede agregar, quitar o modificar fórmulas hardcodeadas en `diagnostic_core/core.py`.
- No puede alterar la lógica de ejecución de fórmulas.
- Solo puede aportar fórmulas (vía FormulaPack) que el core ejecuta como función inyectable.

### Confirmar hallazgos

- No puede cambiar el status de un `CoreFinding` de CANDIDATE a CONFIRMED.
- No puede producir hallazgos confirmados.
- Solo puede producir candidatos que el kernel evalúa contra evidencia.

### Bypass-ear evidence sufficiency

- No puede saltarse la evaluación de `evidence_gate.py`.
- No puede marcar evidencia como SATISFIED sin pasar por el gate.
- No puede inyectar evidencia falsa o no solicitada.

### Escribir LearningMemory

- No puede promover candidatos a LearningMemory.
- No puede registrar aprendizajes operativos automáticamente.
- Solo puede sugerir candidatos que un humano evalúa.

## Relación con DiscoveryMemory

`DiscoveryMemory` captura demandas reales del dueño PyME. Su relación con el Pack System es:

```
Dueño expresa demanda real
  → DiscoveryMemory registra demanda
  → DiscoveryMemory detecta repetición / patrón
  → DiscoveryMemory genera PackCandidate (no promueve automáticamente)
  → Humano evalúa PackCandidate
  → Si aprobado, se crea Pack con status DRAFT
  → Pack sigue ciclo de vida formal
```

**DiscoveryMemory NO:**

- Promueve candidatos a arquitectura automáticamente.
- Crea packs sin aprobación humana.
- Modifica el kernel directamente.
- Convierte demanda real en código operativo.

**DiscoveryMemory SÍ:**

- Registra demandas reales con contexto (tenant_id, timestamp, evidencia asociada).
- Detecta patrones de repetición.
- Genera PackCandidate con metadata (demanda, frecuencia, contexto, evidencia).
- Sugiere candidatos para evaluación humana.

## Relación con LearningMemory

`LearningMemory` almacena aprendizajes operativos de factoría (cómo PymIA opera, no conocimiento PyME). Su relación con el Pack System es:

```
PymIA ejecuta proceso (anamnesis, evidence gate, diagnostic core, etc.)
  → LearningMemory registra aprendizaje operativo
  → Ejemplo: "cuando evidencia X falta, gate bloquea con motivo Y"
  → Ejemplo: "cuando dueño responde Z, reentry consume respuesta"
```

**LearningMemory NO:**

- Contiene conocimiento PyME (fórmulas, patologías, rubros).
- Almacena taxonomías sectoriales.
- Guarda benchmarks de dominio.
- Registra tratamientos operativos específicos.

**LearningMemory SÍ:**

- Aprende patrones de operación del kernel.
- Registra cómo evidence gate evalúa suficiencia.
- Registra cómo diagnostic core ejecuta fórmulas.
- Registra cómo orchestration graph maneja reentry.
- Aprende de ejecuciones pasadas para mejorar operación (no dominio).

## Anatomía mínima de pack

Todo pack debe cumplir este schema mínimo:

```yaml
pack_id: string          # Identificador único (ej: "formula-pack-arg-pyme-v1")
pack_type: enum          # DOMAIN | KNOWLEDGE | FORMULA | PATHOLOGY | SECTOR | CATALOG
version: semver          # Versión del pack (ej: "1.0.0")
schema_version: semver   # Versión del schema de pack que cumple (ej: "1.0.0")
domain_scope: string     # Alcance de dominio (ej: "argentina-pyme-financiero")
required_evidence:       # Lista de tipos de evidencia requeridos
  - evidence_type: string
    required: boolean
    description: string
exposed_items:           # Lista de ítems que el pack expone al kernel
  - item_id: string
    item_type: enum      # FORMULA | PATHOLOGY | TAXONOMY | MAPPING | BENCHMARK
    description: string
compatibility:           # Compatibilidad con kernel y otros packs
  - kernel_version: semver
  - requires_packs:      # Packs que deben estar activos
    - pack_id: string
      version_constraint: semver
status: enum             # DRAFT | CANDIDATE | VALIDATED | ACTIVE | DEPRECATED | REJECTED
metadata:                # Metadata adicional
  author: string
  created_at: datetime
  updated_at: datetime
  changelog: string
```

### Validación de anatomía mínima

El kernel valida:

- `pack_id` es único en el registry.
- `pack_type` es uno de los tipos permitidos.
- `version` es semver válido.
- `schema_version` es compatible con la versión del kernel.
- `domain_scope` no está vacío.
- `required_evidence` es una lista no vacía.
- `exposed_items` es una lista no vacía.
- `compatibility.kernel_version` es compatible con la versión actual del kernel.
- `compatibility.requires_packs` están activos en el registry.
- `status` es ACTIVE (para packs en producción).

## Ciclo de vida

Un pack sigue este ciclo de vida:

```
DRAFT
  → Pack creado por humano o sugerido por DiscoveryMemory.
  → No puede ser cargado por el kernel.
  → Requiere revisión y aprobación.

CANDIDATE
  → Pack aprobado para evaluación.
  → Puede ser cargado en entorno de prueba.
  → Kernel valida schema y compatibilidad.
  → Si falla validación, vuelve a DRAFT o se rechaza.

VALIDATED
  → Pack pasó validación de schema y compatibilidad.
  → Pack pasó pruebas de contraste con evidencia real.
  → Pack no produce outputs inconsistentes.
  → Aprobado para activación.

ACTIVE
  → Pack cargado en producción.
  → Kernel usa pack para procesar casos reales.
  → Pack puede ser versionado (nueva versión = nuevo pack).
  → Pack puede ser deprecado si se encuentra problema.

DEPRECATED
  → Pack marcado como obsoleto.
  → Kernel deja de cargar pack en nuevos casos.
  → Casos en curso pueden seguir usando pack.
  → Pack puede ser reemplazado por nueva versión.

REJECTED
  → Pack no cumple contrato de schema.
  → Pack incompatible con kernel.
  → Pack produce outputs inconsistentes.
  → Pack no puede ser activado.
  → Pack archivado con motivo de rechazo.
```

### Transiciones de estado

```
DRAFT → CANDIDATE       (humano aprueba evaluación)
CANDIDATE → VALIDATED   (kernel valida + pruebas pasan)
CANDIDATE → REJECTED    (kernel rechaza por schema/compatibilidad)
VALIDATED → ACTIVE      (humano aprueba activación)
ACTIVE → DEPRECATED     (humano marca como obsoleto)
DEPRECATED → ACTIVE     (humano reactiva si es necesario)
Cualquier estado → REJECTED (si se detecta problema crítico)
```

## Criterios fail-closed

El kernel aplica fail-closed en estas situaciones:

### Pack no cumple schema

- Kernel rechaza pack.
- Kernel loguea motivo de rechazo.
- Kernel continúa operando sin ese pack.
- No se ejecuta lógica del pack.

### Pack incompatible con kernel

- Kernel rechaza pack.
- Kernel loguea incompatibilidad de versión.
- Kernel continúa operando sin ese pack.
- No se ejecuta lógica del pack.

### Pack requiere evidencia no disponible

- Kernel no ejecuta pack.
- Kernel loguea evidencia faltante.
- Kernel continúa operando sin ese pack.
- No se producen outputs del pack.

### Pack produce output inconsistente

- Kernel descarta output del pack.
- Kernel loguea inconsistencia.
- Kernel continúa operando sin output del pack.
- No se adopta output del pack.

### Pack colisiona con pack activo

- Kernel rechaza pack.
- Kernel loguea colisión de ítems expuestos.
- Kernel continúa operando con pack activo.
- No se carga pack que colisiona.

### Pack intenta mutar estado universal

- Kernel detecta intento de mutación.
- Kernel rechaza operación.
- Kernel loguea intento de violación de contrato.
- Kernel continúa operando sin aplicar mutación.

### Pack intenta confirmar hallazgo

- Kernel detecta intento de confirmación.
- Kernel rechaza confirmación.
- Kernel loguea intento de violación de contrato.
- Hallazgo permanece como CANDIDATE.

### Pack intenta bypasear evidence sufficiency

- Kernel detecta intento de bypass.
- Kernel rechaza bypass.
- Kernel loguea intento de violación de contrato.
- Evidence gate continúa evaluando normalmente.

## Consecuencias

### Positivas

- **Kernel estable:** El core de PymIA no se modifica al agregar conocimiento de dominio.
- **Escalabilidad:** Nuevas verticales, rubros y sectores se agregan como packs, no como código.
- **Versionado:** Cada pack tiene ciclo de vida independiente del kernel.
- **Validación:** Packs se validan contra contrato antes de activarse.
- **Rechazo:** Packs problemáticos se rechazan sin afectar operación.
- **Fail-closed:** Kernel continúa operando aunque un pack falle.
- **Claridad:** Frontera kernel ↔ dominio está definida formalmente.
- **Gobernanza:** DiscoveryMemory sugiere packs, humano decide.
- **Separación:** LearningMemory y KnowledgePack son conceptos distintos.

### Negativas

- **Complejidad:** Sistema de packs agrega capa de abstracción.
- **Overhead:** Validación y contraste de packs consume recursos.
- **Curva de aprendizaje:** Desarrolladores deben entender contrato de packs.
- **Migración:** Conocimiento hardcodeado debe migrarse a packs (trabajo futuro).

### Neutrales

- **Documentación:** Requiere documentar cada pack creado.
- **Testing:** Requiere tests de validación y contraste de packs.
- **Registry:** Requiere mantener registry de packs activos.

## Migraciones futuras

Este ADR no ejecuta migraciones. Solo las define como trabajo futuro autorizado:

### Migración 1: Fórmulas desde `formula_contract.py`

- **Origen:** `pymia/contracts/formula_contract.py` (dict `SUPPORTED_FORMULAS` hardcodeado).
- **Destino:** FormulaPack externo cargado vía `catalog_loader_v1` (o equivalente).
- **Contrato:** FormulaPack debe cumplir anatomía mínima y schema de pack.
- **Validación:** Kernel valida pack contra contrato antes de cargar.
- **Ejecución:** `diagnostic_core/core.py` ejecuta fórmulas del pack como función inyectable.
- **Riesgo:** Si pack falla validación, core no tiene fórmulas. Requiere pack de fallback o rechazo explícito.

### Migración 2: Pathology mapping desde `diagnostic_core/core.py`

- **Origen:** `pymia/diagnostic_core/core.py` (método `_pathology_for_formula` con if/elif).
- **Destino:** PathologyPack externo con mapping formula_id → pathology_code.
- **Contrato:** PathologyPack debe cumplir anatomía mínima y schema de pack.
- **Validación:** Kernel valida pack contra contrato antes de cargar.
- **Ejecución:** `diagnostic_core/core.py` consulta pathology_code del pack.
- **Riesgo:** Si pack no tiene mapping para fórmula, core no puede vincular patología. Requiere validación de cobertura.

### Migración 3: Opciones y mapeos desde `anamnesis_fsm.py`

- **Origen:** `pymia/smartpyme/anamnesis_fsm.py` (tuplas hardcodeadas de opciones + métodos `_map_activity_type`, `_map_primary_pain`).
- **Destino:** CatalogPack (opciones) + DomainPack (mapeos) inyectables a FSM.
- **Contrato:** CatalogPack y DomainPack deben cumplir anatomía mínima y schema de pack.
- **Validación:** Kernel valida packs contra contrato antes de cargar.
- **Ejecución:** `anamnesis_fsm.py` recibe opciones y mapeos como parámetros inyectables.
- **Riesgo:** Si pack no tiene opciones para contexto, FSM no puede avanzar. Requiere opciones de fallback o rechazo explícito.

### Migración 4: Catálogos desde `docs/`

- **Origen:** `pymia/services/catalog_loader_v1.py` (ruta hardcoded `_DOCS_DIR = _REPO_ROOT / "docs"`).
- **Destino:** Registry de packs con ubicaciones configurables.
- **Contrato:** Registry debe aceptar paths inyectables o URLs de packs.
- **Validación:** Kernel valida packs contra contrato antes de cargar.
- **Ejecución:** `catalog_loader_v1.py` consulta registry de packs.
- **Riesgo:** Si registry no tiene packs configurados, loader no encuentra catálogos. Requiere configuración explícita.

## Referencias

- [Informe 0 de Superauditoría PymIA/SmartPyme](../pymia/SUPERAUDITORIA_INFORME_0.md)
- [AGENTS.md](../../AGENTS.md) — Cadena obligatoria ADR→Spec→Test→Code
- [ARCHITECTURE_GUARDRAILS.md](../ARCHITECTURE_GUARDRAILS.md) — Invariantes arquitectónicos
- [evidence-chain-v1.md](../contratos/evidence-chain-v1.md) — Contrato cadena evidencia
- [owner-decision-v1.md](../contratos/owner-decision-v1.md) — Contrato decisión dueño

---

**Este ADR es la base para todo trabajo futuro de desacople kernel ↔ dominio. Sin este ADR, ninguna migración de fórmulas, patologías, anamnesis o catálogos tiene autoridad arquitectónica.**
