# PYMIA_DOCTRINAL_INDEX

## Estado del documento

**Estado:** CANDIDATE_V1

**Nivel:** Índice doctrinal del núcleo organizacional

**No es V1 oficial todavía.** Este documento es la capa de navegación del núcleo organizacional completo (10 documentos). Requiere validación final antes de promoción a V1 oficial.

**No reemplaza a `DOCUMENTATION_INDEX.md`.** Ese índice es técnico-operativo. Este es doctrinal-conceptual.

**Rige:** `ARCHITECTURE_GUARDRAILS.md`

---

## 1. Propósito

Este índice es la **capa de navegación** que conecta:

- La auditoría doctrinal (`PYMIA_DOCTRINAL_AUDIT.md`) — fotografía del estado inicial
- Los 10 documentos del núcleo organizacional de PymIA

Su función no es definir doctrina. Es:

1. Establecer orden de lectura recomendado
2. Proveer glosario canónico de conceptos compartidos
3. Hacer explícito el mapa de dependencias entre documentos
4. Señalar conceptos huérfanos que vivirán en fases posteriores
5. Servir de puente entre auditoría inicial y doctrina consolidada
6. Preparar el terreno para el mapping doctrina → artefactos Python

---

## 2. Orden de lectura recomendado

```
FASE 0 — Fotografía inicial
─────────────────────────────────────
1. PYMIA_DOCTRINAL_AUDIT.md
   Fotografía inicial del repositorio.
   Clasifica ~190 documentos en 7 capas.
   Identifica fuentes para los lotes doctrinales.
   Lectura: 15-20 min.

LOTE 1 — Ontología organizacional
─────────────────────────────────────
2. PYMIA_ORGANIZATIONAL_MODEL_THEORY.md
   Responde: ¿Qué es una organización PyME para PymIA?
   Define ontología base (compromiso de intercambio, 5 dimensiones,
   8 invariantes).
   Es el sustrato sobre el que se construyen todos los demás.
   Lectura: 25-30 min.

3. PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md
   Responde: ¿Qué hace que siga siendo la misma organización?
   Define persistencia (4 identidades, 3 capas, evolución coherente,
   muerte ontológica).
   Usa ontología de MODEL como sustrato.
   Lectura: 30-35 min.

4. PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md
   Responde: ¿Cuándo funciona sanamente?
   Define salud (7 dimensiones, 7 órganos, fragilidad vs enfermedad,
   resiliencia).
   Usa MODEL + IDENTITY como contexto.
   Lectura: 30-35 min.

LOTE 2 — Aprendizaje y decisión
─────────────────────────────────────
5. PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md
   Responde: ¿Qué es aprendizaje organizacional y cómo ocurre?
   Define actualización verificable del modelo organizacional.
   Documento canónico para el concepto de "aprendizaje organizacional".
   Lectura: 25-30 min.

6. PYMIA_DECISION_QUALITY_THEORY.md
   Responde: ¿Qué hace que una decisión individual sea de alta calidad?
   Evalúa instancia decisional (8 componentes, 4 combinaciones
   calidad/resultado, 8 patologías, decision debt).
   Lectura: 30-35 min.

7. PYMIA_DECISION_CAPABILITY_THEORY.md
   Responde: ¿Cómo evalúo el sistema que produce decisiones?
   Evalúa sistema decisional (7 componentes, arquitectura decisional,
   5 niveles de madurez, progreso decisional).
   Usa LEARNING y DECISION_QUALITY como componentes.
   Lectura: 30-35 min.

LOTE 3 — Medicina y gobernanza organizacional
─────────────────────────────────────
8. PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
   Responde: ¿Qué enfermedades organizacionales existen?
   Cataloga 8 enfermedades PyME, cadena clínica de 11 pasos,
   diagnóstico diferencial.
   Usa HEALTH como criterio de contraste.
   Lectura: 30-35 min.

9. PYMIA_ORGANIZATIONAL_INTERVENTION_THEORY.md
   Responde: ¿Cómo se tratan las enfermedades organizacionales?
   Define tratamientos (sintomático/curativo/paliativo), iatrogenia,
   resistencia, adherencia.
   Requiere PATHOLOGY como catálogo base.
   Lectura: 30-35 min.

10. PYMIA_ORGANIZATIONAL_PROGNOSIS_THEORY.md
    Responde: ¿Cómo evolucionan las enfermedades y cuándo son críticas?
    Define trayectorias, puntos de no retorno, ventanas de intervención.
    Pronóstico ≠ predicción.
    Requiere PATHOLOGY + INTERVENTION.
    Lectura: 30-35 min.

11. PYMIA_ORGANIZATIONAL_GOVERNANCE_THEORY.md
    Responde: ¿Cómo se preserva coherencia organizacional en el tiempo?
    Define gobernanza como infraestructura de coherencia (no control).
    Integra IDENTITY + DECISION_CAPABILITY + PROGNOSIS.
    Lectura: 30-35 min.
```

**Justificación del orden:**

- La **auditoría** da contexto de masa documental real.
- **MODEL** establece el sustrato ontológico. Sin él, nada tiene base.
- **IDENTITY** requiere ontología previa para definir persistencia.
- **HEALTH** requiere ambos como insumos de evaluación.
- **LEARNING** define el mecanismo transversal de actualización del modelo.
- **DECISION_QUALITY** evalúa la instancia decisional (atómico).
- **DECISION_CAPABILITY** integra Quality + Learning en sistema (sistémico).
- **PATHOLOGY** diagnostica enfermedad usando HEALTH como contraste.
- **INTERVENTION** trata enfermedades específicas de PATHOLOGY.
- **PROGNOSIS** proyecta trayectorias sobre PATHOLOGY + INTERVENTION.
- **GOVERNANCE** cierra el núcleo integrando todo: preserva coherencia antes de cruzar umbrales.

**Tiempo total de lectura:** ~5-6 horas distribuidas en sesiones.

---

## 3. Glosario canónico de conceptos compartidos

Conceptos que atraviesan múltiples documentos con definición fijada para evitar deriva.

### 3.1 Compromiso de intercambio

**Definición canónica (MODEL §3):**
Acuerdo (explícito o implícito) por el cual la organización entrega algo a cambio de algo bajo condiciones determinadas. Es la **unidad mínima** de análisis organizacional.

**Uso cruzado:**
- **IDENTITY:** Los compromisos persistentes forman el núcleo persistente. Su ruptura puede causar muerte ontológica.
- **HEALTH:** La viabilidad financiera se define como capacidad de cumplir compromisos en el horizonte visible.
- **PATHOLOGY:** Enfermedades organizacionales son disfunciones que comprometen la red de intercambios.
- **GOVERNANCE:** Protege la capacidad de la organización de sostener compromisos críticos.

### 3.2 Restricciones

**Definición canónica (MODEL §7):**
Límites reales dentro de los cuales la organización opera. Son 8 tipos: caja, tiempo, capacidad, atención, información, regulación, mercado, crédito.

**Propiedad clave:** Las restricciones no se eliminan, se navegan.

**Uso cruzado:**
- **IDENTITY:** Las restricciones forman parte de la capa adaptable.
- **HEALTH:** Salud no es ausencia de restricciones, es conciencia y gestión de ellas.
- **PATHOLOGY:** Restricciones acumuladas sin reservas generan fragilidad.
- **DECISION_QUALITY:** Calidad decisional se evalúa dentro de restricciones reales.
- **PROGNOSIS:** Restricciones definen ventanas de intervención disponibles.

### 3.3 Tensiones estructurales

**Definición canónica (MODEL §8):**
Trade-offs permanentes que la organización debe navegar sin resolver. Son 10 tipos universales PyME (crecer/caja, volumen/rentabilidad, velocidad/orden, etc.).

**Propiedad clave:** Las tensiones no se resuelven, se equilibran.

**Uso cruzado:**
- **IDENTITY:** Tensiones no gestionadas derivan en crisis de identidad.
- **HEALTH:** Tensiones mal navegadas son fuente de enfermedad crónica.
- **DECISION_QUALITY:** Decisiones que intentan eliminar tensión suelen crear otra peor.
- **GOVERNANCE:** Debe permitir equilibrio dinámico de tensiones.

### 3.4 Modelo organizacional

**Definición canónica (MODEL §11):**
Representación viva que PymIA mantiene de una organización. Incluye identidad, estructura de intercambio, flujo económico, restricciones, tensiones, capacidades, dependencias.

**Propiedad clave:** El modelo no es la organización. Es la mejor hipótesis sostenida con evidencia disponible.

**Uso cruzado:**
- **IDENTITY:** El modelo incluye las 4 identidades. Divergencia severa = crisis.
- **HEALTH:** El modelo es el sustrato sobre el cual se evalúa salud.
- **LEARNING:** Aprendizaje = actualización verificable del modelo organizacional.
- **PATHOLOGY:** Las enfermedades se diagnostican como disfunciones del modelo.
- **DECISION_CAPABILITY:** Capacidad decisional depende de calidad del modelo.

### 3.5 Identidad declarada / observada / deseada / percibida

**Definición canónica (IDENTITY §2):**

- **Declarada:** Lo que la organización dice que es.
- **Observada:** Lo que la evidencia muestra que realmente es.
- **Deseada:** Lo que la organización quiere llegar a ser.
- **Percibida:** Lo que actores externos ven.

**MODEL las introduce de forma mínima** (§4.1). **IDENTITY las desarrolla en profundidad**. **HEALTH las usa como criterio** de coherencia estructural.

### 3.6 Aprendizaje organizacional

**Definición canónica (LEARNING_MODEL §2):**
Actualización verificable del modelo organizacional basada en evidencia de resultados de decisiones previas.

**Distinción crítica:** Memoria ≠ Aprendizaje. Memoria conserva, aprendizaje transforma.

**Uso cruzado:**
- **DECISION_QUALITY:** Componente 8 (aprendizaje post-decisión).
- **DECISION_CAPABILITY:** Componente 6 de capacidad (aprendizaje como mecanismo sistémico).
- **HEALTH:** Dimensión 7 de salud (aprendizaje adaptativo).
- **GOVERNANCE:** Gobernanza sana preserva capacidad de aprendizaje.

### 3.7 Decisión (instancia vs sistema)

**Definición canónica:**

- **Instancia** (DECISION_QUALITY §2): Selección de alternativa bajo incertidumbre.
- **Sistema** (DECISION_CAPABILITY §2): Capacidad organizacional para producir decisiones de alta calidad consistentemente.

**Propiedad clave:** Calidad de decisión ≠ calidad de resultado.

**Uso cruzado:**
- **MODEL:** Dimensión 5 (decisión concentrada como invariante PyME).
- **HEALTH:** Órgano nervioso.
- **PATHOLOGY:** Fatiga decisional crónica como enfermedad.
- **GOVERNANCE:** Estructura de autoridad como componente.

### 3.8 Enfermedad organizacional

**Definición canónica (PATHOLOGY §2):**
Disfunción de uno o más órganos funcionales que compromete viabilidad, coherencia o adaptabilidad de la organización.

**Distinción crítica:** Enfermedad ≠ fragilidad ≠ crisis.

**Uso cruzado:**
- **HEALTH:** Define criterio de contraste (qué es sano).
- **INTERVENTION:** Define tratamientos específicos para cada enfermedad.
- **PROGNOSIS:** Proyecta trayectoria de cada enfermedad.
- **GOVERNANCE:** Debe prevenir enfermedades sistémicas.

### 3.9 Tratamiento (sintomático / curativo / paliativo)

**Definición canónica (INTERVENTION §3):**

- **Sintomático:** Alivia síntomas sin atacar causa raíz.
- **Curativo:** Ataca causa raíz de la enfermedad.
- **Paliativo:** Gestiona enfermedad crónica sin cura conocida.

**Uso cruzado:**
- **PATHOLOGY:** Cada enfermedad catalogada tiene tratamiento sugerido.
- **PROGNOSIS:** Evalúa efectividad de cada tipo de tratamiento.
- **HEALTH:** Tratamiento sintomático sin curativo genera enfermedad crónica.

### 3.10 Pronóstico / Trayectoria

**Definición canónica (PROGNOSIS §2):**

- **Pronóstico:** Proyección de trayectoria de enfermedad bajo supuestos. **NO es predicción.**
- **Trayectoria:** Curso probable de evolución organizacional. 7 tipos: estable, progresiva, acelerada, recurrente, crítica, recuperación, errática.

**Uso cruzado:**
- **PATHOLOGY:** Cada enfermedad tiene trayectoria natural característica.
- **INTERVENTION:** Tratamientos modifican trayectoria.
- **GOVERNANCE:** Usa pronóstico para proteger umbrales.
- **DECISION_CAPABILITY:** Capacidad decisional incluye componente pronóstico.

### 3.11 Punto de no retorno

**Definición canónica (PROGNOSIS §4):**
Umbral estructural después del cual la organización pierde capacidad de recuperar un estado previo con los recursos disponibles. 5 categorías: financieros, comerciales, humanos, operativos, regulatorios.

**Propiedad clave:** La proximidad al punto de no retorno es más importante que la gravedad actual.

**Uso cruzado:**
- **INTERVENTION:** Después del punto de no retorno, intervención paliativa.
- **GOVERNANCE:** Debe proteger umbrales antes de cruzar puntos de no retorno.
- **HEALTH:** Fragilidad extrema puede significar proximidad a punto de no retorno.

### 3.12 Gobernanza (infraestructura de coherencia)

**Definición canónica (GOVERNANCE §2):**
Sistema de estructuras, procesos y normas que determina quién puede decidir qué, con qué autoridad, con qué responsabilidad, con qué rendición de cuentas, con qué coherencia con estrategia y valores.

**Tesis central:** Gobernanza no protege identidad estática. Protege capacidad de evolución coherente.

**Uso cruzado:**
- **IDENTITY:** Gobernanza protege evolución coherente de identidad.
- **DECISION_CAPABILITY:** Gobernanza es componente 7 del sistema decisional.
- **PROGNOSIS:** Gobernanza vigila umbrales críticos.
- **HEALTH:** Gobernanza sana es parte de salud estructural.

### 3.13 Iatrogenia organizacional

**Definición canónica (INTERVENTION §5):**
Daño causado por el tratamiento mismo. 4 tipos: sobretratamiento, tratamiento contradictorio, tratamiento tardío, tratamiento sin adherencia.

**Propiedad clave:** La cura puede matar al paciente.

**Uso cruzado:**
- **GOVERNANCE:** Debe prevenir iatrogenia sistémica.
- **HEALTH:** Iatrogenia puede convertir enfermedad aguda en crónica.
- **PROGNOSIS:** Trayectoria puede empeorar por iatrogenia.

---

## 4. Mapa de dependencias del núcleo organizacional

### Cadena ontológica (Lote 1)

```
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_MODEL_THEORY      │
│  ¿Qué es una organización?              │
│                                         │
│  • Compromiso de intercambio (unidad)   │
│  • 5 dimensiones estructurales          │
│  • 8 invariantes PyME                   │
└────────────────┬────────────────────────┘
                 │ usa ontología como sustrato
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_IDENTITY_THEORY   │
│  ¿Qué persiste?                         │
│                                         │
│  • 4 identidades                        │
│  • 3 capas estructurales                │
│  • Evolución coherente                  │
└────────────────┬────────────────────────┘
                 │ usa ontología + identidad como contexto
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_HEALTH_MODEL      │
│  ¿Cuándo funciona sanamente?            │
│                                         │
│  • 7 dimensiones de salud               │
│  • 7 órganos funcionales                │
│  • Fragilidad vs enfermedad             │
└─────────────────────────────────────────┘
```

### Cadena decisional (Lote 2)

```
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_LEARNING_MODEL    │
│  ¿Qué es aprendizaje y cómo ocurre?     │
│                                         │
│  • Actualización verificable            │
│  • 5 tipos de aprendizaje               │
│  • Ciclo de 8 pasos                     │
└────────────────┬────────────────────────┘
                 │
                 │ aprendizaje es componente
                 │
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_DECISION_QUALITY_THEORY          │
│  ¿Qué hace buena una decisión?          │
│                                         │
│  • 8 componentes de calidad             │
│  • 4 combinaciones calidad/resultado    │
│  • 8 patologías decisionales            │
└────────────────┬────────────────────────┘
                 │
                 │ quality es componente del sistema
                 │
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_DECISION_CAPABILITY_THEORY       │
│  ¿Cómo evalúo el sistema decisional?    │
│                                         │
│  • 7 componentes fundamentales          │
│  • Arquitectura decisional              │
│  • 5 niveles de madurez                 │
└─────────────────────────────────────────┘
```

### Cadena médica (Lote 3)

```
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY  │
│  ¿Qué enfermedades existen?             │
│                                         │
│  • 8 enfermedades catalogadas           │
│  • Cadena clínica de 11 pasos           │
│  • Diagnóstico diferencial              │
└────────────────┬────────────────────────┘
                 │ diagnostica
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_INTERVENTION      │
│  ¿Cómo se tratan?                       │
│                                         │
│  • 3 tipos de tratamiento               │
│  • Iatrogenia organizacional            │
│  • Resistencia y adherencia             │
└────────────────┬────────────────────────┘
                 │ proyecta efectividad
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_PROGNOSIS_THEORY  │
│  ¿Cómo evolucionan?                     │
│                                         │
│  • 7 tipos de trayectoria               │
│  • Puntos de no retorno                 │
│  • Ventanas de intervención             │
└────────────────┬────────────────────────┘
                 │ alimenta umbrales
                 ▼
┌─────────────────────────────────────────┐
│  PYMIA_ORGANIZATIONAL_GOVERNANCE_THEORY │
│  ¿Cómo se preserva coherencia?          │
│                                         │
│  • Infraestructura de coherencia        │
│  • Autoridad + procesos + mecanismos    │
│  • Gobernanza adaptativa                │
└─────────────────────────────────────────┘
```

### Integración transversal

```
HEALTH (criterio de contraste) ────────────┐
                                            │
IDENTITY (qué proteger) ───────────────────┤
                                            ▼
                                    GOVERNANCE
                                   (cierra núcleo)
                                            ▲
DECISION_CAPABILITY (sistema) ──────────────┤
                                            │
PROGNOSIS (umbrales) ───────────────────────┘
```

**Regla de navegación:**
- Leer en orden MODEL → IDENTITY → HEALTH (Lote 1)
- Luego LEARNING → DECISION_QUALITY → DECISION_CAPABILITY (Lote 2)
- Luego PATHOLOGY → INTERVENTION → PROGNOSIS → GOVERNANCE (Lote 3)
- Saltarse MODEL hace incomprensibles los otros nueve.

---

## 5. Relación con PYMIA_DOCTRINAL_AUDIT.md

La auditoría (`PYMIA_DOCTRINAL_AUDIT.md`) identificó tres cosas críticas que este índice hereda:

1. **Masa documental real:** ~190 documentos dispersos en 7 capas. Los 10 documentos del núcleo organizacional no reemplazan esa masa. **Conviven con ella.**

2. **Fuentes conceptuales:** Los 10 documentos del núcleo se apoyan en documentos existentes:
   - `fundamentos/organismo-pyme.md` (analogía biológica)
   - `fundamentos/cosmovision-clinico-operacional.md` (topología operacional)
   - `fundamentos/metodo-hipotetico-deductivo.md` (método clínico)
   - `epistemologia/modelo-verdad-soberania.md` (verdad soberana)

3. **Ubicación canónica:** La auditoría recomendó crear `docs/doctrina/organizacional/`. Los 10 documentos del núcleo viven allí.

Este índice es el documento transversal que vive en `docs/doctrina/` (fuera de `organizacional/`), cumpliendo función de navegación del núcleo completo.

---

## 6. Estado actual

```
FASE 0: Auditoría doctrinal inicial         ✅ COMPLETADA
        → PYMIA_DOCTRINAL_AUDIT.md

ÍNDICE: Capa de navegación del núcleo       ✅ COMPLETADA (este documento)
        → PYMIA_DOCTRINAL_INDEX.md

LOTE 1: Teoría organizacional fundacional   ✅ COMPLETADO
        → PYMIA_ORGANIZATIONAL_MODEL_THEORY.md
        → PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md
        → PYMIA_ORGANIZATIONAL_HEALTH_MODEL.md

LOTE 2: Aprendizaje y decisión              ✅ COMPLETADO
        → PYMIA_ORGANIZATIONAL_LEARNING_MODEL.md
        → PYMIA_DECISION_QUALITY_THEORY.md
        → PYMIA_DECISION_CAPABILITY_THEORY.md

LOTE 3: Medicina y gobernanza               ✅ COMPLETADO
        → PYMIA_ORGANIZATIONAL_PATHOLOGY_THEORY.md
        → PYMIA_ORGANIZATIONAL_INTERVENTION_THEORY.md
        → PYMIA_ORGANIZATIONAL_PROGNOSIS_THEORY.md
        → PYMIA_ORGANIZATIONAL_GOVERNANCE_THEORY.md

NÚCLEO ORGANIZACIONAL: 10 documentos        ✅ CERRADO

PRÓXIMA FASE: Mapping doctrina → artefactos ⏳ PENDIENTE
```

**Cobertura conceptual completa:**

| Concepto | Documento |
|----------|-----------|
| Ontología organizacional | MODEL |
| Persistencia identitaria | IDENTITY |
| Salud organizacional | HEALTH |
| Aprendizaje organizacional | LEARNING_MODEL |
| Calidad decisional | DECISION_QUALITY |
| Capacidad decisional | DECISION_CAPABILITY |
| Enfermedad organizacional | PATHOLOGY |
| Tratamiento organizacional | INTERVENTION |
| Pronóstico organizacional | PROGNOSIS |
| Coherencia institucional | GOVERNANCE |

---

## 7. Conceptos huérfanos que vivirán en fases posteriores

Conceptos mencionados en el núcleo organizacional pero **no desarrollados** en él. Son huérfanos intencionales que vivirán en documentos de fases futuras.

### 7.1 Cultura organizacional

**Aparece en:**
- IDENTITY §1.4 (mencionada como diferenciación)
- DECISION_CAPABILITY §5.3 (componente de arquitectura decisional)
- GOVERNANCE §5.2 (cultura decisional)

**No desarrolla:**
- Teoría completa de cultura organizacional
- Transmisión cultural
- Cambio cultural
- Patologías culturales

**Vivirá en:** `PYMIA_ORGANIZATIONAL_CULTURE_THEORY.md` (fase futura)

### 7.2 Decision Debt (deuda decisional)

**Aparece en:**
- DECISION_QUALITY §8 (4 tipos de deuda)

**No desarrolla:**
- Teoría completa de deuda decisional
- Métricas de acumulación
- Estrategias de reducción
- Relación con deuda técnica

**Vivirá en:** `PYMIA_DECISION_DEBT_THEORY.md` (fase futura)

### 7.3 Identity Debt (deuda identitaria)

**Aparece en:**
- IDENTITY (mencionada como concepto emergente)

**No desarrolla:**
- Teoría completa de deuda identitaria
- Acumulación de contradicciones identitarias
- Estrategias de reconciliación

**Vivirá en:** `PYMIA_IDENTITY_DEBT_THEORY.md` (fase futura)

### 7.4 Arquitectura Decisional

**Aparece en:**
- DECISION_CAPABILITY §5 (7 componentes)

**No desarrolla:**
- Teoría completa de arquitectura decisional
- Diseño de arquitecturas por tipo de organización
- Evolución de arquitectura decisional

**Vivirá en:** `PYMIA_DECISIONAL_ARCHITECTURE_THEORY.md` (fase futura)

### 7.5 SmartPyme Method & Value

**Aparece en:**
- Dialéctica recuperada en PYMIA_COGNITIVE_MNEMONIC_DIALECTIC.md

**No desarrolla:**
- Método SmartPyme (visible, vendible)
- Motor SmartPyme (interno)
- Hallazgo Verificable como unidad de valor externo

**Vivirá en:** `PYMIA_SMARTPYME_METHOD_VALUE.md` (fase futura)

### 7.6 Therapeutics (separado de Intervention)

**Aparece en:**
- INTERVENTION (tratamientos específicos)

**No desarrolla:**
- Teoría terapéutica independiente
- Dosis organizacional
- Mecanismos de acción detallados
- Contraindicaciones sistemáticas

**Vivirá en:** `PYMIA_ORGANIZATIONAL_THERAPEUTICS.md` (fase futura)

---

## 8. Advertencia explícita

### Este documento es CANDIDATE_V1

Ha sido actualizado para reflejar el núcleo organizacional completo (10 documentos). No es todavía V1 oficial. Requiere validación final antes de promoción.

### Este documento NO fusiona nada

Los 10 documentos del núcleo permanecen intactos. La auditoría permanece intacta. Los ~190 documentos existentes permanecen intactos.

### Este documento NO archiva nada

No reclasifica documentos como obsoletos. No mueve archivos. No borra.

### Este documento NO reemplaza DOCUMENTATION_INDEX.md

`DOCUMENTATION_INDEX.md` (raíz) es el índice técnico-operativo del repositorio. Lista ADRs, contratos, catálogos, manuales. Este índice es doctrinal-conceptual: lista teorías y sus relaciones. Son capas complementarias, no redundantes.

### Este documento NO autoriza runtime

No habilita MCP, jobs, workflows, orquestación ni cambios de código. Solo organiza la capa doctrinal.

### Este documento NO define contratos Python

Los conceptos aquí listados son doctrinales. Su mapeo a artefactos Python (clases, contratos, interfaces) corresponde a la siguiente fase: mapping doctrina → artefactos.

---

## Regla final

```
Este índice es un mapa.
No es el territorio.

Conecta auditoría con doctrina.
Conecta doctrina con doctrina.
Conecta los 10 documentos del núcleo organizacional.

Su función es que el próximo lector
no tenga que reconstruir el orden
desde cero.

Cuando se ejecute el mapping doctrina → artefactos,
este índice será el punto de partida.

Y cuando se actualice,
debe preservarse su versión anterior
como evidencia de evolución doctrinal.
```

---

**Documento cerrado como CANDIDATE_V1.**

Núcleo organizacional completo (10 documentos). Listo para mapping doctrina → artefactos Python en la siguiente fase.
