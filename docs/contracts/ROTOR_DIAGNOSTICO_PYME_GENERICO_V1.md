# ROTOR DIAGNOSTICO PYME GENERICO V1

## Estado

```text
DRAFT_CONTRACT_REDUCED
CODEX_AUDIT_VERDICT: PASS_WITH_WARNINGS
NO_RUNTIME_CHANGE
NO_CODE_AUTHORIZATION
NO_IMPLEMENTATION_AUTHORIZATION
```

## Propósito

Definir una frontera conceptual mínima para el `Rotor Diagnóstico PyME Genérico V1`.

El rotor es un selector declarativo de ruta matemático-evidencial para PyMEs. Su función es recibir una señal estructurada, activar un circuito declarado por packs y devolver una ruta candidata de investigación: circuito, fórmula inicial de referencia, incógnita actual, evidencia mínima requerida y trazabilidad de por qué no puede avanzar si falta evidencia.

Este documento reemplaza la versión amplia inicial del contrato e incorpora la auditoría Codex con veredicto `PASS_WITH_WARNINGS`.

## Fuentes rectoras

```text
ARCHITECTURE_GUARDRAILS.md
docs/adr/ADR-024-pack-system-foundation.md
docs/pymia/PYMIA_DEVELOPMENT_METHOD.md
PymIA-Live/docs/pymia/PYMIA_LIVE_CORE_MANIFEST.md
PymIA-Live/docs/pymia/PYMIA_LIVE_PIPELINE.md
PymIA-Live/docs/pymia/PYMIA_LIVE_TARGET_ARCHITECTURE_V1.md
PymIA-Live/docs/pymia/QUESTION_ALIGNMENT_GATE_SPEC.md
```

## Principios no negociables

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
No hardcodear fórmulas, patologías, pines, circuitos ni reglas PyME en Python.
No diagnosticar sin evidencia suficiente.
No pedir toda la evidencia posible; pedir la evidencia mínima para la incógnita actual.
No reemplazar FormulaEngine.
No reemplazar EvidenceSufficiency.
No reemplazar QuestionAlignmentGate.
No reemplazar OwnerFacingReport.
No abrir canales externos.
No modificar PymIA-Live desde este contrato.
```

## Dominio

El alcance es `PyME genérica`, no universalidad organizacional absoluta.

Incluye funciones comunes de PyMEs reales: ventas, cobranzas, caja, banco, stock, compras, proveedores, costos, precios, margen, producción, sueldos, procesos manuales, automatización y ROI.

No incluye ERP, AGI organizacional, automatización total ni administración autónoma de empresas.

## Definición reducida

```text
Rotor = selector declarativo de ruta.
No calcula fórmulas.
No evalúa suficiencia final de evidencia.
No interpreta patologías.
No prescribe tratamientos.
No humaniza salida final.
```

El rotor sólo puede producir un `RotorRouteCandidate`.

## Responsabilidad única

Dado un input normalizado y packs válidos, el rotor debe responder:

```text
1. qué circuito candidato se activa;
2. qué regla declarativa lo activó;
3. qué fórmula inicial de referencia corresponde consultar;
4. qué incógnita actual debe despejarse;
5. qué evidencia mínima se requiere para esa incógnita;
6. qué fórmulas adyacentes quedan diferidas;
7. por qué no diagnostica;
8. qué traza queda para auditoría.
```

## Fronteras negativas

### FormulaEngine

FormulaEngine conserva el cálculo determinístico de fórmulas.

El rotor no ejecuta expresiones, no calcula resultados, no valida aritmética y no decide outputs numéricos.

### EvidenceSufficiency

EvidenceSufficiency conserva el juicio de suficiencia.

El rotor puede declarar evidencia mínima candidata desde pack, pero no puede marcar evidencia como suficiente ni saltar gates.

### QuestionAlignmentGate

QAG conserva la alineación conversacional entre mensaje del dueño, eje declarado, evidencia detectada y pregunta candidata.

El rotor no interpreta texto libre directamente en runtime V1. Debe recibir input normalizado o una señal ya clasificada.

### PathologyInterpreter

La interpretación patológica queda fuera del rotor.

El rotor no emite patologías candidatas en V1. Sólo puede declarar que ciertas fórmulas adyacentes podrían alimentar, en otro módulo, una interpretación posterior.

### OwnerFacingReport / humanización

La traducción owner-facing queda fuera del rotor.

El rotor puede emitir `reason_code` y `trace`, pero no redacta salida final al dueño.

### Tratamientos

Los tratamientos operacionales quedan fuera de este contrato.

No hay `treatment_link` ni `treatment_candidate` en Rotor V1.

## Inputs aceptados

El rotor no presupone ignorancia técnica. Acepta señales normalizadas de estos modos:

```text
OWNER_SYMPTOM_NORMALIZED
TECHNICAL_QUERY_NORMALIZED
FORMULA_DIRECT
EVIDENCE_FIRST
PATHOLOGY_HYPOTHESIS_NORMALIZED
OPEN_EXPLORATION_NORMALIZED
```

Nota: la normalización de texto libre no pertenece al rotor.

`PATHOLOGY_HYPOTHESIS_NORMALIZED` debe entenderse sólo como una señal normalizada de entrada para routing.

El rotor no interpreta patologías, no evalúa patologías, no confirma patologías y no genera patologías candidatas.

La hipótesis patológica sólo participa como señal de activación o descarte de ruta.

## Conocimiento enchufable mínimo

El rotor depende de packs declarativos. Para V1 conceptual sólo se reconocen tres familias mínimas:

```text
PYME_BASE_ROUTING_PACK
FORMULA_REFERENCE_PACK
EVIDENCE_REQUIREMENT_PACK
```

Packs diferidos fuera de V1:

```text
TREATMENT_PACK
HUMANIZATION_PACK
SECTOR_PACK avanzado
PATHOLOGY_PACK operativo
```

## Modelo mínimo de ruta

```json
{
  "input_mode": "OWNER_SYMPTOM_NORMALIZED",
  "activated_circuit": "CIRCUIT_LIQUIDEZ_OPERATIVA",
  "activation_rule_id": "liquidity_route_v1",
  "formula_reference": "ventas_vs_cobranzas",
  "current_unknown": "cobranzas_del_periodo",
  "minimal_evidence_required": ["ventas_periodo", "cobranzas_periodo"],
  "adjacent_formula_refs_deferred": ["ratio_cobranza", "ciclo_conversion_caja"],
  "status": "NEEDS_EVIDENCE",
  "reason_code": "SALES_CASH_GAP_REQUIRES_COLLECTIONS_FIRST"
}
```

`formula_reference` es una referencia declarativa de ruta.

No implica ejecución, cálculo, evaluación, priorización ni despacho de fórmulas.

FormulaEngine conserva toda decisión de ejecución matemática.

## Fórmulas adyacentes

La adyacencia se reduce a una lista diferida de referencias.

Queda prohibido en V1 clasificar adyacencias como `direct`, `second_order` o `confirmatory`, porque esa taxonomía introduce inferencia diagnóstica prematura.

Regla:

```text
El rotor no prioriza una cadena completa de fórmulas.
Sólo declara referencias adyacentes diferidas desde pack.
La decisión de calcularlas requiere contrato posterior.
```

`adjacent_formula_refs_deferred` debe interpretarse como trazabilidad pasiva.

No implica planificación, secuencia de cálculo, agenda matemática, estrategia diagnóstica ni ejecución futura.

Son únicamente referencias observables asociadas a la ruta actual.

## Evidencia mínima

La evidencia mínima es una declaración candidata de pack para despejar una incógnita actual.

El rotor no certifica suficiencia. Sólo produce requerimiento candidato para que otros módulos o gates lo consuman.

## Microcircuito de auditoría: liquidez operativa

El único microcircuito conceptual permitido en este contrato es `CIRCUIT_LIQUIDEZ_OPERATIVA`.

Se usa sólo para auditar el modelo.

```text
Input normalizado:
problema entre ventas y caja

Circuito:
CIRCUIT_LIQUIDEZ_OPERATIVA

Fórmula de referencia:
ventas_vs_cobranzas

Incógnita:
cobranzas_del_periodo

Evidencia mínima candidata:
ventas_periodo + cobranzas_periodo

Adyacencias diferidas:
ratio_cobranza
ciclo_conversion_caja
stock_cash_lock
margen_bruto_pct
```

No se declaran patologías ni tratamientos en este microcircuito V1.

## Criterios de aceptación

El contrato reducido es aceptable si:

```text
- preserva kernel estable + packs enchufables;
- reduce el rotor a selector de ruta;
- no invade FormulaEngine;
- no invade EvidenceSufficiency;
- no invade QAG;
- no interpreta patologías;
- no sugiere tratamientos;
- no humaniza salida final;
- mantiene fail-closed;
- conserva trazabilidad de la ruta;
- no habilita implementación.
```

## Criterios de rechazo

Se rechaza cualquier futura ampliación que:

```text
- agregue cálculo de fórmulas al rotor;
- confirme o interprete patologías dentro del rotor;
- marque evidencia como suficiente;
- procese texto libre directamente;
- redacte owner-facing output final;
- agregue tratamientos;
- hardcodee conocimiento PyME en Python;
- convierta el rotor en orquestador total;
- abra roadmap o implementación sin nueva cadena metodológica.
```

## Próximo paso metodológico

```text
AUDITORIA_EXTERNA_DEL_CONTRATO_REDUCIDO
```

Este contrato no habilita código, tests, schemas Pydantic, runtime, migración de fórmulas, creación de packs activos ni modificación de `PymIA-Live`.
