# Conversation Clinical Runtime — Dirección Arquitectónica Estratégica

## Estado

VIGENTE_CANDIDATO

## Propósito

Formalizar el rumbo arquitectónico de SmartPyme/PymIA hacia un sistema conversacional clínico-operacional orientado a adquisición progresiva de contexto, evidencia y diagnóstico.

Este documento fija que el producto no debe evolucionar hacia un simple chatbot con parser de Excel, sino hacia un runtime clínico-operacional guiado por fases conversacionales, evidencia estructurada y contratos diagnósticos.

---

# Problema Detectado

Durante las primeras iteraciones del sistema, la implementación avanzó más rápido en:

- recepción de adjuntos;
- parsing de Excel;
- lifecycle documental;
- clasificación de evidencia;
- integración Telegram/Hermes;
- auditorías tabulares;
- procesamiento documental.

Sin embargo, la arquitectura conceptual original ya contemplaba:

- historia clínica inicial;
- taxonomía;
- síntomas;
- patologías;
- fórmulas;
- evidencia requerida;
- contexto operacional;
- fases de adquisición diagnóstica.

El problema es que gran parte de esa riqueza conceptual quedó documentada, pero no transformada todavía en runtime obligatorio.

Resultado:

El sistema actualmente interpreta demasiadas cosas desde el Excel aislado, en lugar de interpretar el Excel contra contexto clínico-operacional.

---

# Decisión Estratégica

SmartPyme/PymIA evoluciona hacia:

```text
Clinical Conversation Runtime
```

No hacia:

```text
chatbot + parser de Excel
```

---

# Definición de Clinical Conversation Runtime

Un runtime clínico conversacional es un sistema que:

- adquiere contexto progresivamente;
- guía a la PyME para externalizar conocimiento operacional;
- solicita evidencia contextualizada;
- detecta incertidumbre;
- cuantifica confianza;
- bloquea benchmarks peligrosos;
- emite preguntas específicas;
- transforma conversaciones y documentos en evidencia estructurada;
- alimenta un kernel diagnóstico.

---

# Cambio de Paradigma

## Paradigma Incorrecto

```text
archivo
→ parseo
→ respuesta
```

## Paradigma Objetivo

```text
síntoma
→ contexto
→ evidencia
→ interpretación
→ opacidad
→ diagnóstico
→ plan de acción
```

---

# Decisión Crítica

La conversación no existe para hablar.

Existe para:

```text
reducir incertidumbre diagnóstica
```

---

# Runtime Conversacional por Fases

La conversación se modela como:

```text
ConversationClinicalStateMachine
```

No como flujo lineal rígido.

Cada tenant posee:

- estado conversacional;
- subestado;
- confidence;
- evidencia mínima alcanzada;
- bloqueos;
- FIO activas;
- patologías abiertas;
- próxima mejor pregunta.

---

# Fases Conversacionales Oficiales

## FASE_0_IDENTIDAD

### Objetivo

Determinar qué tipo de organismo económico es la PyME.

### Produce

- BusinessIdentity.
- TenantClinicalContext base.

### Ejemplos

- distribuidora.
- retail.
- fabricante.
- gastronómico.
- servicios.

---

## FASE_1_SINTOMA

### Objetivo

Detectar motivo principal de consulta.

### Produce

- ClinicalHypothesis.
- ActivePathology candidates.

### Ejemplos

- vendo mucho y no queda plata.
- no entiendo márgenes.
- sospecho fuga de dinero.
- stock desordenado.
- costos no claros.

---

## FASE_2_CONTEXTO_OPERACIONAL

### Objetivo

Entender cómo opera la PyME.

### Produce

- OperationalProfile.
- FormulaContext inicial.

### Variables posibles

- stock;
- rutas;
- vendedores;
- clientes;
- sucursales;
- producción;
- distribución;
- reventa.

---

## FASE_3_EVIDENCIA_MINIMA

### Objetivo

Adquirir evidencia suficiente para análisis preliminar.

### Produce

- EvidencePlan.
- EvidenceRequirements.

### Regla

La evidencia solicitada depende de:

- rubro;
- síntoma;
- patologías activas;
- fórmulas necesarias.

---

## FASE_4_ANALISIS_PRELIMINAR

### Objetivo

Emitir primeras hipótesis cuantificadas.

### Produce

- hallazgos preliminares;
- confidence parcial;
- variables inferidas.

---

## FASE_5_OPACIDAD

### Objetivo

Resolver incertidumbres bloqueantes.

### Produce

- FIO;
- preguntas específicas;
- benchmark blockers.

### Regla Crítica

Toda pregunta al dueño debe nacer desde una FIO.

Prohibido:

```text
indicá qué columna es venta
```

Correcto:

```text
La columna costo puede representar costo total o costo unitario. Las ecuaciones disponibles no cierran con suficiente confianza.
```

---

## FASE_6_EVIDENCIA_COMPLEMENTARIA

### Objetivo

Cerrar hipótesis abiertas.

### Produce

- evidencia incremental;
- validaciones matemáticas adicionales;
- nuevas inferencias.

---

## FASE_7_DIAGNOSTICO

### Objetivo

Emitir diagnóstico operacional confiable.

### Produce

- hallazgos accionables;
- patologías confirmadas;
- priorización;
- impacto operacional.

---

## FASE_8_PLAN_ACCION

### Objetivo

Convertir diagnóstico en ejecución operacional.

### Produce

- plan operativo;
- próximos pasos;
- seguimiento;
- nuevas necesidades de evidencia.

---

# TenantClinicalContext como Pieza Central

La primera fase de encuentro PyME/sistema no puede vivir como texto libre.

Debe convertirse en:

```text
TenantClinicalContext
```

Ese contrato alimenta:

```text
TenantClinicalContext
→ PymeColumnOntology
→ BusinessSchemaInferenceEngine
→ Polars Mathematical Validator
→ SemanticSchema
→ EvidenceBundle enriquecido
→ Kernel PymIA
```

---

# UI Estratégica

La UI debe favorecer entrega de información valiosa.

No debe limitarse a:

```text
subí un Excel
```

Debe inducir:

- síntomas;
- contexto;
- evidencia útil;
- aclaraciones específicas;
- colaboración diagnóstica.

---

# Diseño Correcto del Menú del Bot

Ejemplo conceptual:

```text
📉 Rentabilidad
📦 Stock
💰 Caja
🧾 Costos
🚚 Rutas
👥 Clientes
📊 Subir evidencia
🧠 Estado del laboratorio
📌 Pendientes
```

---

# Cambio Fundamental

El Excel deja de ser el centro.

Pasa a ser:

```text
una pieza más dentro de un proceso clínico-operacional
```

---

# Definición Real del Producto

SmartPyme/PymIA no es:

```text
lector de Excel
```

SmartPyme/PymIA es:

```text
sistema operativo de diagnóstico PyME basado en evidencia
```

---

# Objetivo Enterprise

Enterprise-grade significa:

- contratos explícitos;
- trazabilidad completa;
- confidence cuantificada;
- validación matemática;
- bloqueo de benchmark inseguro;
- contexto clínico obligatorio;
- separación estricta de responsabilidades;
- evidencia estructurada;
- runtime conversacional gobernado;
- FIO obligatoria;
- lifecycle preservado;
- Hermes desacoplado de inferencia financiera.

---

# Invariantes Estratégicos

1. Ningún benchmark corre sin contexto mínimo.
2. Ningún Excel se interpreta aislado.
3. Ninguna inferencia financiera crítica se acepta sin validación.
4. Toda opacidad genera FIO.
5. Hermes no interpreta negocio.
6. BEM no es ruta principal.
7. TenantClinicalContext es obligatorio.
8. Las fases conversacionales son runtime, no sólo UX.
9. El sistema debe saber qué hipótesis siguen abiertas.
10. El sistema debe saber qué evidencia falta para cerrar diagnóstico.

---

# Dirección Técnica Futura

La evolución futura deberá introducir:

```text
ConversationPhase
ConversationState
PhaseTransition
RequiredEvidence
PhaseBlocker
PhaseConfidence
NextBestQuestion
```

como contratos runtime explícitos.

---

# Veredicto Estratégico

La ventaja competitiva futura de SmartPyme/PymIA no será tener IA.

La ventaja competitiva será:

```text
guiar a una PyME para transformar caos operacional en evidencia diagnóstica confiable
```
