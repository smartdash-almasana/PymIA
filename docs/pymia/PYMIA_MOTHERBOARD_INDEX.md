# PymIA — Motherboard Index

Estado: CANDIDATO
Fecha: 2026-06-08
Tipo: índice integrador de gobierno y obediencia

---

## 1. Propósito

Este documento no crea doctrina nueva.

Este documento identifica qué documentos existentes cumplen la función de **placa madre** de PymIA: el lugar de gobierno y obediencia que evita que el sistema crezca como islotes de código, documentación y agentes desconectados.

La motherboard no reemplaza:

```text
ADR-007
DOCUMENTATION_INDEX.md
PYMIA_DEVELOPMENT_METHOD.md
PORTS_AND_GATES_CONTRACT_REGISTRY.md
```

La motherboard los conecta.

---

## 2. Regla de no duplicidad

Por ADR-007, este documento no debe duplicar reglas normativas.

Su función es de navegación y trazabilidad:

```text
pregunta arquitectónica → documento vigente/candidato que la gobierna
```

Si una regla debe cambiarse, se cambia en su documento fuente, no aquí.

---

## 3. Definición operativa

En PymIA, la motherboard es el conjunto mínimo de documentos, contratos, gates y métodos que:

```text
autorizan
prohíben
ordenan
limitan
trazan
conservan identidad
```

Todo módulo, agente o slice debe obedecer esta red documental antes de modificar código productivo.

---

## 4. Mapa de gobierno documental

| Pregunta | Documento fuente | Estado en índice canónico | Función |
|---|---|---|---|
| ¿Qué documentación puede gobernar código? | `docs/adr/ADR-007-documentation-governance.md` | VIGENTE | Gobierno documental superior |
| ¿Qué documentos son vigentes, candidatos o superados? | `docs/DOCUMENTATION_INDEX.md` | VIGENTE | Índice soberano |
| ¿Cómo se trabaja sin deriva metodológica? | `docs/pymia/PYMIA_DEVELOPMENT_METHOD.md` | pendiente de verificar en índice | Método de desarrollo |
| ¿Cómo se conectan módulos sin islotes? | `docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md` | pendiente de verificar en índice | Puertos y gates |
| ¿Cómo debe comportarse una IA residente? | `docs/pymia/PYMIA_RESIDENT_INTELLIGENCE_CONTRACT.md` | pendiente de verificar en índice | Jaula / obediencia de IA residente |
| ¿Cómo se arnesa una IA residente? | `docs/pymia/PYMIA_RESIDENT_AI_HARNESS_ENGINEERING.md` | pendiente de verificar en índice | Arnés operativo |
| ¿Cómo se preserva trazabilidad de evidencia? | `docs/contratos/evidence-chain-v1.md` | VIGENTE | Cadena de evidencia |
| ¿Qué doctrina organizacional existe? | `docs/doctrina/PYMIA_DOCTRINAL_INDEX.md` | CANDIDATE_V1 | Navegación doctrinal |
| ¿Cómo pasa doctrina a artefactos? | `docs/doctrina/PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md` | CANDIDATE_V1 | Doctrina → artefactos |
| ¿Cómo pasan artefactos a contratos? | `docs/doctrina/PYMIA_ARTIFACT_TO_CONTRACT_MAPPING.md` | CANDIDATE_V1 | Artefactos → contratos |
| ¿Cómo pasan contratos a software? | `docs/doctrina/PYMIA_CONTRACT_TO_SOFTWARE_MAPPING.md` | CANDIDATE_V1 | Contratos → Python |
| ¿Qué significa identidad organizacional? | `docs/doctrina/organizacional/PYMIA_ORGANIZATIONAL_IDENTITY_THEORY.md` | DRAFT_CANONICAL_CANDIDATE | Identidad organizacional |

---

## 5. Lectura por situación

### 5.1 Antes de crear documentación nueva

Leer:

```text
docs/adr/ADR-007-documentation-governance.md
docs/DOCUMENTATION_INDEX.md
```

Regla:

```text
no crear documento normativo nuevo sin verificar duplicidad y ciclo de vida.
```

### 5.2 Antes de implementar código

Leer:

```text
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
```

Regla:

```text
arquitectura → contrato → TaskSpec → test → código → evidencia → checkpoint
```

### 5.3 Antes de conectar módulos

Leer:

```text
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
```

Regla:

```text
ningún módulo relevante se conecta por intuición; se conecta por puerto o gate.
```

### 5.4 Antes de usar IA residente/agentes

Leer:

```text
docs/pymia/PYMIA_RESIDENT_INTELLIGENCE_CONTRACT.md
docs/pymia/PYMIA_RESIDENT_AI_HARNESS_ENGINEERING.md
```

Regla:

```text
la IA residente no gobierna PymIA; obedece contratos, fuentes y gates.
```

### 5.5 Antes de razonar sobre evidencia

Leer:

```text
docs/contratos/evidence-chain-v1.md
docs/pymia/PORTS_AND_GATES_CONTRACT_REGISTRY.md
```

Regla:

```text
sin fuente no hay hecho fuerte; inferencia no es decisión ni diagnóstico confirmado.
```

### 5.6 Antes de crear artefactos de dominio

Leer:

```text
docs/doctrina/PYMIA_DOCTRINAL_INDEX.md
docs/doctrina/PYMIA_DOCTRINE_TO_ARTIFACT_MAPPING.md
docs/doctrina/PYMIA_ARTIFACT_TO_CONTRACT_MAPPING.md
docs/doctrina/PYMIA_CONTRACT_TO_SOFTWARE_MAPPING.md
```

Regla:

```text
doctrina → artefacto → contrato → software
```

---

## 6. Qué no es la motherboard

La motherboard no es:

```text
un nuevo documento constitucional soberano
una carpeta paralela de reglas
un reemplazo del índice canónico
un bypass de ADR-007
una justificación para duplicar invariantes
un roadmap de features
```

---

## 7. Qué sí es la motherboard

La motherboard es:

```text
un mapa de obediencia
un índice de gobierno transversal
una defensa contra islotes de código
una guía de lectura para agentes y humanos
un puente entre doctrina, contratos, gates, tests y ejecución
```

---

## 8. Estado de borradores previos

Durante la conversación se crearon dos borradores exploratorios:

```text
docs/pymia/motherboard/DRAFT_NOT_APPROVED_00_CONSTITUTION.md
docs/pymia/motherboard/DRAFT_NOT_APPROVED_01_INVARIANTS.md
```

Esos borradores no son canónicos, no gobiernan código y no deben usarse como fuente normativa.

Su única función posible es servir como material de discusión para revisar, fusionar o descartar bajo ADR-007.

---

## 9. Pendientes antes de promover este índice

Antes de promover este documento a VIGENTE:

```text
1. verificar que PYMIA_DEVELOPMENT_METHOD esté registrado en DOCUMENTATION_INDEX.md;
2. verificar que PORTS_AND_GATES_CONTRACT_REGISTRY esté registrado;
3. verificar que RESIDENT_INTELLIGENCE_CONTRACT esté registrado;
4. verificar que RESIDENT_AI_HARNESS_ENGINEERING esté registrado;
5. decidir si los borradores DRAFT_NOT_APPROVED se eliminan o se archivan;
6. actualizar DOCUMENTATION_INDEX.md con este documento como CANDIDATO;
7. auditar que no duplique reglas normativas activas.
```

---

## 10. Veredicto operativo

```text
La motherboard de PymIA no debe ser una nueva constitución paralela.
Debe ser el índice que muestra dónde vive cada autoridad existente.
```
