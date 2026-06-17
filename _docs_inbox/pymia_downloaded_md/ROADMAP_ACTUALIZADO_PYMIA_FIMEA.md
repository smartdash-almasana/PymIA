# ROADMAP ACTUALIZADO — PYMIA / FIMEA / SMARTPYME

**Fecha:** 2026-06-17  
**Estado:** Roadmap corregido según documentación viva reportada por el usuario.  
**Alcance:** Dirección de maduración desde baseline end-to-end probado hacia producto sano, profesional, repetible y auditable.

---

## 1. Corrección de autoridad

El roadmap anterior ubicaba `owner_labels_v1` como próximo corte técnico.

La documentación viva leída en GitHub indica que el gap rector actual es:

```text
QuestionAlignmentGate
```

Por lo tanto, se corrige la prioridad.

```text
La documentación viva manda sobre el informe estratégico.
```

---

## 2. Veredicto actualizado

```text
Arquitectura base: PASS
PymIA-Live: PASS
Informe estratégico previo: PASS parcial
Roadmap anterior: parcialmente desactualizado
Prioridad actual: QuestionAlignmentGate
```

---

## 3. Criterio rector de avance

PymIA/FIMEA no debe avanzar por features.

Debe avanzar por maduración verificable:

```text
contrato
→ test
→ implementación
→ validación
→ auditoría
→ commit
```

Producto vendible significa:

```text
sano
profesional
repetible
auditable
sin hardcodes críticos
sin chapuzas
sin deuda genética escondida
```

---

## 4. Roadmap corregido

### R0 — Recuperación operativa

Objetivo:

```text
Recuperar acceso confiable al repo y congelar estado actual.
```

Acciones:

```text
git status --short
cd PymIA-Live
python -m pytest tests/contracts/test_formula_rules_v1.py -v --tb=short
```

Criterio PASS:

```text
formula_rules_v1: 8 passed
formula_engine_service.py intacto
sin cambios inesperados
```

---

### R1 — Project Director Protocol

Objetivo:

```text
Crear protocolo de dirección de proyecto IA.
```

Archivo sugerido:

```text
docs/pymia/PROJECT_DIRECTOR_PROTOCOL.md
```

Función:

```text
Definir gobierno, roles, ciclos, estados y criterios de bloqueo.
```

Estado:

```text
Diseñado conceptualmente; pendiente de incorporación al repo.
```

---

### R2 — TaskSpec Harness

Objetivo:

```text
Crear arnés para que Codex/OpenHands/Freebuff trabajen bajo tareas cerradas.
```

Archivo sugerido:

```text
docs/pymia/TASKSPEC_HARNESS.md
```

Debe definir:

```text
- estructura de TaskSpec
- archivos permitidos
- archivos prohibidos
- comandos permitidos
- tests obligatorios
- estados PASS / PARTIAL / BLOCKED / HARD_FAIL
- política de commit local
- prohibición de push
- reporte final obligatorio
```

---

### R3 — QuestionAlignmentGate Contract

Objetivo:

```text
Formalizar contrato propio para alinear síntoma/pregunta emergente del dueño con la próxima pregunta del sistema.
```

Razonamiento:

```text
El gap rector actual no es presentación visual.
El gap rector es semántico-operacional:
la pregunta siguiente debe emerger correctamente del síntoma, evidencia, faltante y estado del caso.
```

Entregables esperados:

```text
- contrato documentado
- campos mínimos
- estados válidos
- criterios de suficiencia
- criterios de bloqueo
- ejemplos positivos y negativos
```

No implementar código antes de cerrar este contrato.

---

### R4 — QuestionAlignmentGate Test

Objetivo:

```text
Crear tests contractuales antes de implementar.
```

Los tests deben validar:

```text
- síntoma del dueño → pregunta correcta
- evidencia faltante → pregunta concreta
- input técnico explícito → ruta técnica correcta
- input lego/caótico → traducción operativa correcta
- no inventar diagnóstico si falta evidencia
- no hacer pregunta genérica si existe faltante específico
```

Criterio PASS:

```text
Tests fallan antes de implementación si el gate no existe o no cumple.
Tests pasan después de implementación sin tocar motor.
```

---

### R5 — QuestionAlignmentGate Implementation

Objetivo:

```text
Implementar el gate sin contaminar runtime con conocimiento hardcodeado.
```

Reglas:

```text
- no tocar formula_engine_service.py
- no tocar formula_rules_v1.json salvo autorización explícita
- no tocar question_alignment_v1.json sin contrato previo
- no meter ifs por sector, patología o fórmula en código vivo
- usar contrato/catálogo si corresponde
- preservar trazabilidad
```

Salida esperada:

```text
Pregunta siguiente más precisa, trazable y coherente con evidencia/faltantes.
```

---

### R6 — Auditoría post-QuestionAlignmentGate

Objetivo:

```text
Verificar que el gate no introdujo deriva genética.
```

Auditoría debe revisar:

```text
- diff focal
- tests
- ausencia de hardcodes críticos
- no tocar motor
- no tocar catálogos no autorizados
- preservación del flujo end-to-end
- coherencia con documentación viva
```

Criterio PASS:

```text
El gate mejora alineación sin romper arquitectura.
```

---

### R7 — Revaluación de owner_labels_v1

Objetivo:

```text
Reevaluar deuda de labels owner-facing después de cerrar el gap rector.
```

`owner_labels_v1` sigue siendo deuda probable, pero ya no es prioridad inmediata.

Condición de entrada:

```text
QuestionAlignmentGate cerrado y auditado.
```

---

### R8 — Report Contract V1

Objetivo:

```text
Formalizar contrato del reporte owner-facing.
```

Debe contener:

```text
- resumen ejecutivo
- hallazgos
- evidencia usada
- evidencia faltante
- preguntas al dueño
- próximos pasos
- trazabilidad
- límites de interpretación
```

---

### R9 — Intake / Delivery Protocol V1

Objetivo:

```text
Convertir el uso de PymIA en operación repetible.
```

Debe definir:

```text
- qué pide el sistema al dueño
- qué archivos acepta
- cuándo bloquea
- cuándo procesa
- cuándo entrega
- qué registra
```

---

### R10 — Smoke real 2–3 casos

Objetivo:

```text
Probar el flujo saneado con casos reales o semi-reales.
```

Regla:

```text
Durante el smoke no se arregla en caliente.
Se registra PASS / PARTIAL / BLOCKED.
```

---

### R11 — Auditoría genética post-smoke

Objetivo:

```text
Separar problemas de producto, datos, arquitectura y operación.
```

Salida:

```text
- qué funcionó
- qué falló
- qué falta
- qué no debe tocarse
- qué impide vender sano
```

---

### R12 — Paquete vendible sano

Objetivo:

```text
Definir SmartPyme Laboratorio / FIMEA como oferta profesional acotada.
```

Debe incluir:

```text
- alcance
- entradas aceptadas
- salidas prometidas
- límites
- tiempos
- revisión humana
- precio tentativo
- condiciones de bloqueo
```

---

## 5. Orden operativo resumido

```text
R0  Recuperar acceso repo
R1  PROJECT_DIRECTOR_PROTOCOL.md
R2  TASKSPEC_HARNESS.md
R3  QuestionAlignmentGate Contract
R4  QuestionAlignmentGate Test
R5  QuestionAlignmentGate Implementation
R6  Auditoría post-gate
R7  Revaluar owner_labels_v1
R8  report_contract_v1
R9  intake_delivery_protocol_v1
R10 Smoke real 2–3 casos
R11 Auditoría genética post-smoke
R12 Paquete vendible sano
```

---

## 6. Herramientas recomendadas

```text
Codex:
builder principal bajo TaskSpec.

OpenHands:
sandbox / QA / automation runner.

Freebuff / Codebuff:
builder/refactor alternativo, no arquitecto autónomo.

Gemini / Opus / Qwen:
auditor externo.

ChatGPT:
director asistente, redactor de TaskSpecs, control metodológico.

Usuario:
owner con criterio, veto y aceptación final.
```

---

## 7. Regla anti-ping-pong

Los próximos prompts a Codex/OpenHands no deben pedir sólo auditoría si el objetivo es ejecución.

Formato correcto:

```text
Leer
→ validar precondición
→ implementar corte cerrado
→ correr tests definidos
→ reportar
→ commit local si PASS
→ NO push
```

Pero para `QuestionAlignmentGate`, primero debe existir contrato.

---

## 8. Bloqueos actuales

```text
MCP_SMARTBRIDGE: 502 upstream / external service errors
PymIA_Filesystem_MCP: conexión fallida
GitHub connector: no disponible en el chat anterior
Codex: usuario reportó sin conexión
```

Por lo tanto, hasta recuperar acceso:

```text
No asumir estado real del repo.
No afirmar lectura nueva.
No implementar a ciegas.
Preparar artefactos de gobierno y TaskSpecs.
```

---

## 9. Frase rectora

```text
PymIA/FIMEA no madura agregando features.
Madura cerrando gaps rectores con contratos, tests, evidencia y auditoría.
```

