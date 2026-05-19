# Documentación Migrada: CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md

**Origen**: SmartPyme/docs/architecture/CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
**Destino**: PymIA/docs/migrado_desde_smartpyme/formulas/CLINICAL_MATHEMATICAL_KERNEL_AND_HUMAN_COGNITIVE_LOOP.md
**Categoría**: formulas
**Fecha migración**: 2026-05-18
**Prioridad**: alta
**Riesgo drift**: medio

---

## Resumen 1 línea

Kernel matemático clínico: motor de reducción dirigida de incertidumbre con pipeline cognitivo (narrativa→hipótesis→fórmulas→evidencia→cálculo) y axiomas de trazabilidad, DAG fisiológico y estado INSUFFICIENT_DATA.

---

## Contenido preservado (extracto)

### Tesis central

> SmartPyme no calcula totales. SmartPyme computa estados de salud operacional.

El sistema funciona como motor de reducción dirigida de incertidumbre sobre sistemas complejos auditables.

### Cambio ontológico

El núcleo real es configurable por catálogos:
- FormulaCatalog
- PathologyCatalog
- evidencia documental
- ontología semántica
- políticas del tenant

### El dueño como HumanKnowledgeNode

El dueño/gerente es fuente cognitiva dentro del circuito de evidencia. El sistema debe:
- hacerlo pensar
- obligarlo a ordenar conocimiento
- separar intuición de evidencia
- detectar contradicciones
- pedir aclaraciones dirigidas

> SmartPyme no reemplaza al conocedor. Lo convierte en parte activa del circuito de evidencia.

### Pipeline cognitivo-operacional

```
narrativa humana
→ hipótesis
→ fórmulas/reglas
→ variables faltantes
→ evidencia requerida
→ pregunta dirigida al conocedor
→ documento o aclaración
→ cálculo/tensión
→ nueva pregunta mejor
```

### Arquitectura del Matematizador Pericial

**Layer 1: FormulaCatalog**
- Definición estática de leyes matemáticas, exigencias e invariantes

**Layer 2: MathEngine / Matematizador**
- Evaluador puramente reactivo. Valida procedencia, computa o declara INSUFFICIENT_DATA

**Layer 3: PathologyEvaluator**
- Contrasta la Verdad Computada contra condiciones del catálogo y límites del tenant

### Axiomas del Matematizador

**Axioma 1 — Variable Trazable**
Cada variable debe declarar: valor matemático, source_id, evidence_id/fact_id, tenant_id, confidence, timestamp, origen humano o documental.
> Si no existe trazabilidad: NO CALCULAR

**Axioma 2 — DAG Fisiológico**
Las fórmulas viven en un grafo acíclico dirigido. Ejemplo:
```
Costo Unitario → CMV → Margen Bruto → Margen Neto → Punto de Equilibrio → Flujo de Caja
```

**Axioma 3 — INSUFFICIENT_DATA**
La falta de datos no es excepción técnica. Es estado clínico ejecutable.

### Fórmulas clave mencionadas

- Margen Bruto
- Margen Neto
- CMV (Costo de Mercadería Vendida)
- Punto de Equilibrio
- Flujo de Caja
- pricing
- cashflow
- stock
- margen

---

## Notas de migración

- Documento preservado sin reinterpretación
- Contenido original disponible en SmartPyme/docs/architecture/
- Clasificado como fórmulas por su definición del kernel matemático y catálogo de fórmulas
- No se migró código ni configuración asociada
- Posible drift: terminología técnica en inglés vs castellano requiere resolución posterior

---

## Referencias cruzadas

- Relacionado con: `SPECIFIC_KNOWLEDGE_TANKS_AND_SOURCE_ENGINE.md`
- Relacionado con: `PYME_OPERATIONAL_MODELS_SYMPTOMS_AND_CASES.md`
- Ver también: `CATALOGO_FORMULAS_MATEMATICAS_PYME_v1.md` en PymIA/docs/
