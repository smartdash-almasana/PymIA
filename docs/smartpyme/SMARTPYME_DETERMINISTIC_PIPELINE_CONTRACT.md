# SmartPyme — Contrato de consolidación del pipeline determinístico

Fecha: 2026-06-01  
Estado: contrato operativo propuesto  
Alcance: pipeline central determinístico SmartPyme, sin bordes externos.

---

## 1. Propósito

Este documento fija cómo llegar a un pipeline determinístico **end-to-end consolidado y testeado OK**.

La prioridad no es agregar nuevas features.

La prioridad es certificar un circuito canónico mínimo, completo y honesto.

---

## 2. Regla de alcance

Este contrato evalúa sólo el pipeline central.

Quedan fuera de esta certificación inicial:

```text
Telegram
HTML
PDF
Docling
UI
memoria avanzada
supracorteza IA
resident AI harness
```

Esos bordes pueden existir o documentarse, pero no deben mezclarse con la certificación del núcleo determinístico.

---

## 3. Pipeline central canónico

El circuito a consolidar es:

```text
intake
→ evidence_requirement
→ evidence
→ evidence_gate
→ readiness
→ runtime_bridge
→ microservice_dispatcher
→ plugin
→ microservice_execution_result
→ execution_result_gate
→ delivery_package
```

Este es el primer circuito que debe quedar probado de punta a punta.

---

## 4. Primera ficha canónica

La primera ficha para certificar debe ser:

```text
excel_diagnostic
```

Motivo:

```text
es la ficha más conectada en el circuito formal actual.
```

Objetivo:

```text
un caso entra con relato + evidencia Excel
y sale con DeliveryPackage READY_TO_DELIVER.
```

Sin atajos por CLI paralelo.

---

## 5. Test end-to-end formal requerido

Crear un test nuevo:

```text
tests/smartpyme/test_deterministic_pipeline_e2e.py
```

Debe construir el flujo paso a paso, usando contratos reales:

```text
1. create_intake_record(...)
2. create/register EvidenceRecord(...)
3. evaluate_evidence_sufficiency(...)
4. evaluate_analysis_readiness(...)
5. prepare_runtime_execution(...)
6. dispatch_candidate(...)
7. validate execution result gate
8. build_delivery_package(...)
```

---

## 6. Happy path esperado

Para `excel_diagnostic`, el test debe afirmar:

```text
status final == READY_TO_DELIVER
runtime_classification == excel_diagnostic
execution status == EXECUTED
findings_count > 0
output_refs existe
delivery_package.output_refs existe
```

El criterio no es que cada módulo funcione aislado.

El criterio es que el circuito completo funcione conectado.

---

## 7. Casos negativos obligatorios

El pipeline no está consolidado si sólo pasa el happy path.

Deben existir bloqueos sanos para:

```text
falta evidencia → NEEDS_EVIDENCE
evidencia insuficiente → NEEDS_MORE_EVIDENCE / BLOCKED
classification desconocida → UNSUPPORTED
candidate no ready → BLOCKED
plugin falla → FAILED
gate rechaza → delivery BLOCKED / FAILED
```

La consolidación exige que el sistema no invente salida cuando falta una condición.

---

## 8. Separación respecto de CLI

`e2e_cli.py` puede ser útil, pero no certifica el pipeline central.

Motivo:

```text
el CLI ejecuta un camino local directo que no equivale necesariamente al circuito formal:
readiness → runtime_bridge → dispatcher → gate → delivery.
```

Por lo tanto:

```text
CLI passing ≠ pipeline central certified.
```

---

## 9. Separación respecto de supplier_duplicate_check

`supplier_duplicate_check` no debe mezclarse con la primera certificación.

Estado actual:

```text
implementado como plugin;
conectado por CLI;
reconocido por readiness/runtime_bridge;
no conectado al dispatcher formal;
tests actuales del dispatcher defienden contrato viejo.
```

Por eso debe tratarse en un frente separado:

```text
M17 — Align supplier_duplicate_check with formal dispatcher.
```

Orden recomendado:

```text
1. Certificar excel_diagnostic end-to-end.
2. Luego cerrar M17 supplier_duplicate_check.
```

---

## 10. Documento de contrato del pipeline

Este documento debe actuar como contrato del pipeline central.

Debe mantenerse alineado con:

```text
docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
docs/smartpyme/M17_SUPPLIER_DISPATCHER_CONTRACT_FINDING.md
tests/smartpyme/test_deterministic_pipeline_e2e.py
```

Cuando el pipeline cambie, este contrato debe cambiar junto con los tests.

---

## 11. Criterio de consolidación

Sólo puede declararse “pipeline central consolidado” cuando se cumpla:

```text
[ ] existe contrato documental del pipeline;
[ ] existe test e2e formal, no CLI lateral;
[ ] happy path excel_diagnostic pasa completo;
[ ] bloqueos negativos pasan;
[ ] execution_result_gate está incluido;
[ ] delivery_package queda READY_TO_DELIVER;
[ ] registry refleja exactamente lo certificado;
[ ] no se mezclan bordes externos en la certificación.
```

---

## 12. Orden de trabajo propuesto

```text
M18.1 — Documentar contrato del pipeline central.
M18.2 — Crear test e2e formal para excel_diagnostic.
M18.3 — Agregar negativos de bloqueo.
M18.4 — Actualizar registry: excel_diagnostic = pipeline_certified.
M18.5 — Recién después: M17 supplier_duplicate_check al dispatcher formal.
```

---

## 13. Veredicto

No se llega a un pipeline consolidado intentando certificar todo a la vez.

Se llega certificando primero un circuito canónico mínimo:

```text
relato + evidencia Excel
→ gates
→ readiness
→ dispatch formal
→ plugin
→ gate de ejecución
→ delivery_package
```

Cuando ese circuito pase de punta a punta, PymIA tendrá su primera corteza determinística end-to-end real.

---

## 14. Frase rectora

```text
Pipeline consolidado no significa muchas capacidades.
Significa un circuito canónico completo, testeado y honesto.
```
