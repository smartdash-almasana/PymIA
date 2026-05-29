# PYMIA_DOCTRINAL_INDEX

## Estado del documento

**Estado:** DRAFT_CANONICAL_CANDIDATE

**Nivel:** Índice doctrinal mínimo

**No es V1 oficial.** Este documento es una capa de navegación que conecta la auditoría doctrinal con el Lote 1 de teoría organizacional. No declara doctrina canónica.

**No reemplaza a `DOCUMENTATION_INDEX.md`.** Ese índice es técnico-operativo. Este es doctrinal-conceptual.

**Rige:** `ARCHITECTURE_GUARDRAILS.md`

---

## 1. Propósito

Este índice es la **capa de navegación mínima** que conecta:

- La auditoría doctrinal (`PYMIA_DOCTRINAL_AUDIT.md`) — fotografía del estado inicial
- Los tres documentos del Lote 1 de teoría organizacional (MODEL, IDENTITY, HEALTH)

Su función no es definir doctrina. Es:

1. Establecer orden de lectura recomendado
2. Proveer glosario mínimo de conceptos compartidos
3. Hacer explícito el mapa de dependencias entre documentos
4. Señalar conceptos huérfanos que vivirán en lotes posteriores
5. Servir de puente entre la auditoría inicial y la doctrina emergente

---

## 2. Orden de lectura recomendado

```
1. PYMIA_DOCTRINAL_AUDIT.md
   Fotografía inicial del repositorio.
   Clasifica ~190 documentos en 7 capas.
   Identifica fuentes para MODEL, IDENTITY, HEALTH.
   Lectura: 15-20 min.

2. PYMIA_ORGANIZATIONAL_MODEL_THEORY.md
   Responde: ¿Qué es una organización PyME para PymIA?
   Define ontología base (compromiso de intercambio, 5 dimensiones, 8 invariantes).
   Es la base sobre la que se construyen los otros dos.
   Lectura: 25-30 min.

3. PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md
   Responde: ¿Qué hace que siga siendo la misma organización?
   Define persistencia (4 identidades, 3 capas, evolución coherente, muerte ontológica).
   Usa la ontología de MODEL como sustrato.
   Lectura: 30-35 min.

4. PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md
   Responde: ¿Cuándo funciona sanamente?
   Define salud (7 dimensiones, 7 órganos, fragilidad vs enfermedad, resiliencia).
   Usa ontología de MODEL + identidad de IDENTITY como contexto.
   Lectura: 30-35 min.

5. [Lote 2 — pendiente]
   Aprendizaje, calidad decisional, capacidad decisional.
```

**Justificación del orden:**

- La **auditoría** da contexto de masa documental real.
- **MODEL** establece el sustrato ontológico (qué es una organización). Sin él, los otros dos carecen de base.
- **IDENTITY** requiere ontología previa para definir persistencia (¿qué persiste? los compromisos de intercambio definidos en MODEL).
- **HEALTH** requiere ambos: usa restricciones (MODEL) y coherencia identitaria (IDENTITY) como insumos de evaluación.

---

## 3. Glosario mínimo de conceptos compartidos

Cinco conceptos aparecen en los tres documentos del Lote 1 con matices distintos. Este glosario fija el significado canónico para evitar deriva.

### 3.1 Compromiso de intercambio

**Definición canónica (MODEL §3):**
Acuerdo (explícito o implícito) por el cual la organización entrega algo a cambio de algo bajo condiciones determinadas. Es la **unidad mínima** de análisis organizacional.

**Uso en IDENTITY:**
Los compromisos de intercambio persistentes forman parte del **núcleo persistente** de identidad. Cuando un compromiso crítico se rompe, puede haber muerte ontológica.

**Uso en HEALTH:**
La **viabilidad financiera** (dimensión 1 de salud) se define como capacidad de cumplir compromisos de intercambio en el horizonte visible.

### 3.2 Restricciones

**Definición canónica (MODEL §7):**
Límites reales dentro de los cuales la organización opera. Son 8 tipos: caja, tiempo, capacidad, atención, información, regulación, mercado, crédito.

**Propiedad clave:** Las restricciones no se eliminan, se navegan.

**Uso en IDENTITY:**
Las restricciones forman parte de la **capa adaptable**. Identidad debe evolucionar cuando restricciones cambian estructuralmente.

**Uso en HEALTH:**
La salud no es ausencia de restricciones. Es **conciencia y gestión** de ellas. Fragilidad aparece cuando restricciones se acumulan sin reservas.

### 3.3 Tensiones estructurales

**Definición canónica (MODEL §8):**
Trade-offs permanentes que la organización debe navegar sin resolver. Son 10 tipos universales PyME (crecer/caja, volumen/rentabilidad, velocidad/orden, etc.).

**Propiedad clave:** Las tensiones no se resuelven, se equilibran.

**Uso en IDENTITY:**
Tensiones no gestionadas pueden derivar en **crisis de identidad** (cuando la organización intenta eliminar tensión y crea otra peor).

**Uso en HEALTH:**
Tensiones mal navegadas son fuente de **enfermedad crónica** (el sistema se adapta a estar enfermo).

### 3.4 Modelo organizacional

**Definición canónica (MODEL §11):**
Representación viva que PymIA mantiene de una organización. Incluye identidad, estructura de intercambio, flujo económico, restricciones, tensiones, capacidades, dependencias.

**Propiedad clave:** El modelo no es la organización. Es la mejor hipótesis sostenida con evidencia disponible.

**Uso en IDENTITY:**
El modelo incluye las **4 identidades** (declarada, observada, deseada, percibida). Cuando divergen severamente, el modelo registra crisis.

**Uso en HEALTH:**
El modelo es el **sustrato sobre el cual se evalúa salud**. Sin modelo vivo, no hay evaluación posible.

### 3.5 Identidad declarada / observada

**Definición canónica (IDENTITY §2):**

- **Identidad declarada:** Lo que la organización dice que es. Fuentes: ficha, web, discurso, materiales.
- **Identidad observada:** Lo que la evidencia muestra que realmente es. Fuentes: patrones de ventas, comportamiento operativo, decisiones documentadas.

**MODEL las introduce de forma mínima** (§4.1): declarada, observada, operativa (reconciliación).

**IDENTITY las desarrolla en profundidad** añadiendo deseada y percibida.

**HEALTH las usa como criterio** (§1.2): coherencia estructural = identidad declarada ≈ identidad observada. Divergencia severa = enfermedad.

---

## 4. Mapa de dependencias del Lote 1

```
┌─────────────────────────────────────────────────────────┐
│         PYMIA_ORGANIZATIONAL_MODEL_THEORY.md            │
│                                                         │
│  Responde: ¿Qué es una organización?                    │
│                                                         │
│  Provee:                                                │
│  • Unidad mínima: compromiso de intercambio             │
│  • 5 dimensiones estructurales                          │
│  • 8 invariantes PyME                                   │
│  • Restricciones, tensiones, capacidades, dependencias  │
│  • Modelo organizacional vivo                           │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ usa ontología como sustrato
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│       PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md           │
│                                                         │
│  Responde: ¿Qué persiste a través del tiempo?           │
│                                                         │
│  Provee:                                                │
│  • 4 identidades (declarada, observada, deseada,        │
│    percibida)                                           │
│  • 3 capas (núcleo persistente, adaptable, periférica)  │
│  • Crisis de identidad (4 tipos)                        │
│  • Muerte ontológica                                    │
│  • Evolución coherente                                  │
└────────────────────────┬────────────────────────────────┘
                         │
                         │ usa ontología + identidad
                         │ como contexto de evaluación
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│        PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md             │
│                                                         │
│  Responde: ¿Cuándo funciona sanamente?                  │
│                                                         │
│  Provee:                                                │
│  • 7 dimensiones de salud                               │
│  • 7 órganos funcionales                                │
│  • Fragilidad vs enfermedad (4 combinaciones)           │
│  • Resiliencia con umbral de shock                      │
│  • Signos tempranos de deterioro                        │
│  • Equivalentes médicos                                 │
└─────────────────────────────────────────────────────────┘
```

**Lectura del diagrama:**

- MODEL es **independiente**. No requiere los otros dos para tener sentido.
- IDENTITY **depende de MODEL** (usa compromisos de intercambio como sustrato de persistencia).
- HEALTH **depende de MODEL e IDENTITY** (usa restricciones + identidad como insumos de evaluación).

**Regla de navegación:**
Leer en orden MODEL → IDENTITY → HEALTH. Saltarse MODEL hace incomprensibles los otros dos.

---

## 5. Relación con PYMIA_DOCTRINAL_AUDIT.md

La auditoría (`PYMIA_DOCTRINAL_AUDIT.md`) identificó tres cosas críticas que este índice hereda:

1. **Masa documental real:** ~190 documentos dispersos en 7 capas. Los 3 documentos del Lote 1 no reemplazan esa masa. **Conviven con ella.**

2. **Fuentes conceptuales:** Los 3 documentos del Lote 1 se apoyan en documentos existentes:
   - `fundamentos/organismo-pyme.md` (analogía biológica)
   - `fundamentos/cosmovision-clinico-operacional.md` (topología operacional)
   - `fundamentos/metodo-hipotetico-deductivo.md` (método clínico)
   - `epistemologia/modelo-verdad-soberania.md` (verdad soberana)

3. **Ubicación canónica:** La auditoría recomendó crear `docs/doctrina/organizacional/` para evitar dispersión. El Lote 1 vive allí.

Este índice es el **primer documento** que vive en `docs/doctrina/` (fuera de `organizacional/`), cumpliendo función de navegación transversal.

---

## 6. Estado actual

```
FASE 0: Auditoría doctrinal inicial         ✅ COMPLETADA
        → PYMIA_DOCTRINAL_AUDIT.md

ÍNDICE: Capa de navegación mínima           ✅ COMPLETADA (este documento)
        → PYMIA_DOCTRINAL_INDEX.md

LOTE 1: Teoría organizacional fundacional   ✅ COMPLETADO
        → PYMIA_ORGANIZATIONAL_MODEL_THEORY.md
        → PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md
        → PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md

LOTE 2: Aprendizaje y decisión              ⏳ PENDIENTE
        → PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md
        → PYMIA_ORGANIZATIONAL_DECISION_QUALITY_THEORY.md
        → PYMIA_DECISION_CAPABILITY_THEORY.md

LOTE 3: Intervención y gobernanza           ⏳ PENDIENTE
        → PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
        → PYMIA_ORGANIZATIONAL_INTERVENTION_THEORY.md
        → PYMIA_ORGANIZATIONAL_PROGNOSIS_THEORY.md
        → PYMIA_ORGANIZATIONAL_GOVERNANCE_THEORY.md
```

**Nota:** Lote 2 y Lote 3 son tentativo. Puede reorganizarse tras validación cruzada del Lote 1.

---

## 7. Conceptos huérfanos que vivirán en Lote 2

Tres conceptos aparecen mencionados en los documentos del Lote 1 pero **no son desarrollados**. Son huérfanos intencionales: deben vivir en documentos posteriores para respetar el principio de responsabilidad única.

### 7.1 Aprendizaje organizacional

**Aparece en:**
- MODEL §5.8 (invariante 8: "aprendizaje implícito")
- HEALTH §1.7 (dimensión 7: "aprendizaje adaptativo")
- HEALTH §2.7 (órgano reproductivo: "aprendizaje/innovación")

**No desarrolla:**
- Cómo se produce el aprendizaje
- Cómo se registra
- Cómo se transfiere
- Cómo se diferencia de memoria

**Vivirá en:** `PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md` (Lote 2)

### 7.2 Decisión

**Aparece en:**
- MODEL §4.5 (dimensión 5: "decisión")
- HEALTH §2.4 (órgano nervioso: "decisión/dueño")
- HEALTH §1.5 (dimensión 5: "capacidad correctiva")

**No desarrolla:**
- Calidad decisional
- Capacidad decisional como sistema
- Patologías decisionales
- Deuda decisional

**Vivirá en:**
- `PYMIA_ORGANIZATIONAL_DECISION_QUALITY_THEORY.md` (Lote 2)
- `PYMIA_DECISION_CAPABILITY_THEORY.md` (Lote 2)

### 7.3 Patologías

**Aparece en:**
- HEALTH §5 (signos tempranos de deterioro)
- HEALTH §6 (equivalentes médicos: enfermedad crónica, cáncer, etc.)
- IDENTITY §5 (crisis de identidad)
- IDENTITY §6 (muerte ontológica)

**No desarrolla:**
- Catálogo sistemático de patologías
- Mecanismos de producción de patología
- Relación entre patologías
- Tratamiento

**Vivirá en:** `PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md` (Lote 3)

---

## 8. Advertencia explícita

### Este documento NO es V1 oficial

Es un índice mínimo de navegación. Está en estado DRAFT_CANONICAL_CANDIDATE como los tres documentos del Lote 1. Requiere validación cruzada con Lote 2 y Lote 3 antes de promoción a V1.

### Este documento NO fusiona nada

Los 3 documentos del Lote 1 permanecen intactos. La auditoría permanece intacta. Los ~190 documentos existentes permanecen intactos.

### Este documento NO archiva nada

No reclasifica documentos como obsoletos. No mueve archivos. No borra.

### Este documento NO reemplaza DOCUMENTATION_INDEX.md

`DOCUMENTATION_INDEX.md` (raíz) es el índice técnico-operativo del repositorio. Lista ADRs, contratos, catálogos, manuales. Este índice es doctrinal-conceptual: lista teorías y sus relaciones. Son capas complementarias, no redundantes.

### Este documento NO autoriza runtime

No habilita MCP, jobs, workflows, orquestación ni cambios de código. Solo organiza la capa doctrinal.

---

## Regla final

```
Este índice es un mapa.
No es el territorio.

Conecta auditoría con doctrina.
Conecta doctrina con doctrina.
Conecta Lote 1 con lotes futuros.

Su función es que el próximo lector
no tenga que reconstruir el orden
desde cero.

Cuando lleguen Lote 2 y Lote 3,
este índice debe actualizarse.

Y cuando se actualice,
debe preservarse su versión anterior
como evidencia de evolución doctrinal.
```

---

**Documento cerrado como DRAFT_CANONICAL_CANDIDATE.**

Listo para commit atómico antes de apertura de Lote 2.
