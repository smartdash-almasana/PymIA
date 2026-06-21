# PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1

## Estado

```text
Tipo: ROADMAP_CYCLE_3_CLOSEOUT
Estado: DRAFT_APPLIED
Runtime impact: NONE
Code impact: NONE
Tests impact: NONE
```

## Propósito

Consolidar la arqueología documental/técnica inicial del Servicio 1 de PymIA.

Este documento cierra el ciclo de recuperación de evidencia disponible y ubica el estado real del Servicio 1 antes de abrir matriz de capacidades, loaders, pipeline, XLSX delivery o runtime productivo.

---

# 1. Roadmap rector

Según el roadmap vigente, Servicio 1 debe avanzar por ciclos:

```text
Fase 0 — definición / catálogo
Fase 1 — arqueología / mapa de piezas
Fase 2 — núcleo operativo
Fase 3 — entrada y salida
Fase 4 — Factoría Excel
Fase 5 — motores contables básicos
Fase 6 — IA con arnés
Fase 7 — madurez comercial
```

El ciclo correspondiente a este documento es:

```text
Ciclo 3 — Service 1 Archaeology Audit
```

Objetivo del ciclo:

```text
Recuperar qué ya existe, qué está documentado, qué código es reutilizable y qué falta enchufar.
```

---

# 2. Archivos efectivamente leídos

| Path | Líneas leídas | Categoría | Qué prueba | Qué NO prueba |
|---|---:|---|---|---|
| `docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | 1156 | CATALOG | Define catálogo amplio de Servicio 1, familias, estados de madurez, riesgos y next actions. | No prueba código productivo ni runtime autorizado. |
| `docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md` | 530 | PLAN | Documenta orden de integración por ciclos y restricciones de no mezclar servicios. | No prueba que los ciclos estén implementados. Declara `NO_CODE_AUTHORIZED`. |
| `docs/producto/SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1.md` | 270 | BOUNDARY | Define frontera entre First Aid Toolbox y Commercial Modules. | No prueba loader compartido, registry común ni wiring de pipeline. |
| `docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md` | 448 | CONCEPT | Define concepto de Excel Treatment Lab, fases funcionales, relación con OCF, anamnesis taxonómica y service depth. | No prueba implementación runtime ni tests. |
| `docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md` | 493 | ARCHAEOLOGY | Clasifica fórmulas, validaciones y herramientas provenientes de Exceland. | No prueba migración YAML a runtime ni packs cargados. |
| `docs/producto/FIRST_AID_TOOL_ACTIVATION_V1.md` | 145 | CONTRACT | Define contrato documental de activación First Aid, estados, reglas, inputs, outputs y prohibiciones. | No prueba por sí solo runtime autorizado. |

---

# 3. Evidencia textual relevante

## 3.1 Catálogo Servicio 1

Archivo:

```text
docs/producto/PYMIA_SERVICE_1_FULL_CATALOG_V1.md
```

Fragmentos relevantes reportados:

```text
"Servicio 1 no es un MVP mutilado"
"20 capacidades mapeadas con estados DEFINED a MISSING"
```

Conclusión:

```text
Existe una definición amplia de Servicio 1 y una intención explícita de no achicar el universo funcional.
```

Límite:

```text
El catálogo no equivale a implementación.
```

---

## 3.2 Plan de integración

Archivo:

```text
docs/producto/PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
```

Fragmentos relevantes reportados:

```text
"Orden recomendado de implementación: 14 ciclos"
"NO_CODE_AUTHORIZED, NO_TESTS_AUTHORIZED"
```

Conclusión:

```text
Existe plan incremental y regla de no mezclar capas.
```

Límite:

```text
El plan declara autorización documental, no implementación.
```

---

## 3.3 Frontera First Aid vs Commercial Modules

Archivo:

```text
docs/producto/SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1.md
```

Fragmentos relevantes reportados:

```text
"First Aid Toolbox no reemplaza Commercial Modules"
"No crear loader compartido todavía"
```

Conclusión:

```text
La frontera conceptual está documentada: First Aid es triage inicial; Commercial Modules son paquetes comerciales declarativos más estructurados.
```

Límite:

```text
No hay integración runtime entre ambas capas.
```

---

## 3.4 Excel Treatment Lab

Archivo:

```text
docs/producto/EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md
```

Fragmentos relevantes reportados:

```text
"Excel Treatment Lab no es un Excel Reader"
"9 fases funcionales descritas"
```

Conclusión:

```text
Existe concepto de producto para Laboratorio Excel, con fases y relación con expediente organizacional.
```

Límite:

```text
No autoriza runtime, contratos ni tests productivos.
```

---

## 3.5 Arqueología Exceland / First Aid

Archivo:

```text
docs/producto/FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
```

Fragmentos relevantes reportados:

```text
"Exceland = cantera de herramientas"
"10 fórmulas FIRST_AID, 5 restringidas"
```

Conclusión:

```text
Exceland queda clasificado como cantera de herramientas, no como módulo vivo a copiar directamente.
```

Límite:

```text
No hay migración directa de YAML ni runtime autorizado.
```

---

## 3.6 Contrato de activación First Aid

Archivo:

```text
docs/producto/FIRST_AID_TOOL_ACTIVATION_V1.md
```

Fragmentos relevantes reportados:

```text
"8 estados de activación mutuamente excluyentes"
"No autoriza ejecutar cálculo, generar XLSX, diagnosticar"
```

Conclusión:

```text
First Aid Activation tiene contrato documental claro y límites explícitos.
```

Límite:

```text
El contrato no autoriza ejecución productiva.
```

---

# 4. Estado por área

## 4.1 Product Definition / Full Catalog

```text
FOUND: YES
MATURITY: DOCUMENTED
CONFIDENCE: HIGH
```

Evidencia:

```text
PYMIA_SERVICE_1_FULL_CATALOG_V1.md
PYMIA_SERVICE_1_IMPLEMENTATION_INTEGRATION_PLAN_V1.md
```

Estado:

```text
Servicio 1 está definido como universo funcional amplio: Laboratorio Operacional de Datos, Excel y Contabilidad + Factoría Excel + servicios contables operativos + IA con arnés + entregables descargables.
```

Límite:

```text
La definición no implica implementación runtime.
```

---

## 4.2 First Aid

```text
FOUND: YES
MATURITY: PARTIAL_IMPLEMENTED_FOCAL
CONFIDENCE: HIGH
```

Evidencia documental:

```text
FIRST_AID_TOOLBOX_ARCHAEOLOGY_EXCELAND_V1.md
FIRST_AID_TOOL_ACTIVATION_V1.md
FIRST_AID_ACTIVATION_SCENARIOS_V1.md
FIRST_AID_TOOL_ACTIVATION_EVALUATOR_V1_CLOSEOUT.md
FIRST_AID_ACTIVATION_SCENARIOS_TEST_V1_CLOSEOUT.md
```

Evidencia técnica reciente:

```text
Commit: 6351b1b feat(pymia-live): add first aid activation evaluator
```

Incluye:

```text
first_aid_tool_activation_v1.json
first_aid_toolbox_pack_seed_v1.json
first_aid_tool_activation_evaluator_v1.py
tests contractuales y focales
escenarios First Aid
closeouts documentales
```

Estado:

```text
First Aid Activation tiene contrato, seed pack, evaluator puro, escenarios y tests focales.
```

Límite:

```text
Las 5 herramientas First Aid todavía no existen como tools ejecutables productivas.
Runtime sigue no autorizado.
```

---

## 4.3 Excel Factory / Excel Treatment Lab

```text
FOUND: YES
MATURITY: CONCEPTUAL / DOCUMENTED
CONFIDENCE: MEDIUM
```

Evidencia:

```text
EXCEL_TREATMENT_LAB_PRODUCT_CONCEPT.md
PYMIA_SERVICE_1_FULL_CATALOG_V1.md
```

Estado:

```text
Existe concepto fuerte de Laboratorio Excel / Factoría Excel.
```

Límite:

```text
No se confirma ExcelSpec ejecutable, generador XLSX productivo ni plantillas conectadas a Servicio 1.
```

---

## 4.4 File Intake

```text
FOUND: PARTIAL
MATURITY: DOCUMENTED_ONLY
CONFIDENCE: MEDIUM
```

Estado:

```text
El roadmap define File Intake V1 para xlsx, csv, pdf, zip e imagen.
```

Límite:

```text
No se confirma módulo File Intake V1 productivo dentro de Servicio 1.
```

---

## 4.5 XLSX Delivery

```text
FOUND: PARTIAL
MATURITY: DOCUMENTED_ONLY
CONFIDENCE: HIGH
```

Estado:

```text
El roadmap declara XLSX Delivery como parte central del producto.
```

Límite:

```text
No existe `first_aid_xlsx_delivery.py` ni delivery First Aid productivo confirmado.
```

---

## 4.6 Accounting Operations

```text
FOUND: PARTIAL
MATURITY: DOCUMENTED / MISSING_RUNTIME
CONFIDENCE: MEDIUM
```

Áreas mencionadas:

```text
conciliación bancaria
Mercado Pago / tarjetas
facturas vs cobros
papeles de trabajo
IVA / IIBB
asientos
vencimientos
```

Límite:

```text
No se confirma runtime productivo para conciliación bancaria, Mercado Pago, papeles de trabajo ni servicios contables completos.
```

---

## 4.7 Operational FSM

```text
FOUND: PARTIAL
MATURITY: DOCUMENTED_ONLY
CONFIDENCE: MEDIUM
```

Estado:

```text
El roadmap define FSM operacional y la regla: La IA conversa. La FSM gobierna. Las tools ejecutan.
```

Límite:

```text
No se confirma `SERVICE_1_FSM_V1` implementado ni conectado.
```

---

## 4.8 LLM Harness

```text
FOUND: PARTIAL
MATURITY: DOCUMENTED_ONLY
CONFIDENCE: MEDIUM
```

Estado:

```text
La IA está definida como capa conversacional y de explicación, no como motor de cálculo.
```

Límite:

```text
No existe `LLM_ADAPTER_V1` productivo confirmado para Servicio 1.
```

---

## 4.9 Commercial Modules

```text
FOUND: YES
MATURITY: DOCUMENTED_SEPARATE_LAYER
CONFIDENCE: HIGH
```

Evidencia:

```text
SERVICE_1_TOOLBOX_AND_COMMERCIAL_MODULES_BOUNDARY_V1.md
```

Módulos detectados previamente:

```text
cobranzas_vencidas
stock_roto
conciliacion_ventas_ml
```

Estado:

```text
Commercial Modules existen como capa documental separada.
```

Límite:

```text
No están conectados a PymIA-Live ni comparten loader con First Aid.
```

---

# 5. Roadmap alignment

| Ciclo | Estado arqueológico | Evidencia | Nota |
|---|---|---|---|
| Ciclo 1 — Product Definition V1 | PARTIAL / DOCUMENTED | Catálogo + plan | Falta documento único de definición si se exige salida formal exacta. |
| Ciclo 2 — Full Catalog V1 | DOCUMENTED | `PYMIA_SERVICE_1_FULL_CATALOG_V1.md` | Catálogo amplio existe. |
| Ciclo 3 — Archaeology Audit | THIS_DOCUMENT | `PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1.md` | Este documento consolida evidencia inicial. |
| Ciclo 4 — Capability Matrix V1 | NEXT | pendiente | Próximo paso lógico. |
| Ciclo 5 — TaskSpec V1 | NOT_STARTED / DOCUMENTED_ONLY | roadmap | No confirmado como contrato operativo. |
| Ciclo 6 — Operational FSM V1 | DOCUMENTED_ONLY | roadmap | No conectado a Servicio 1. |
| Ciclo 7 — File Intake V1 | DOCUMENTED_ONLY | roadmap | No confirmado productivo. |
| Ciclo 8 — XLSX Delivery V1 | DOCUMENTED_ONLY | roadmap | Pendiente crítico. |
| Ciclo 9 — Excel Factory Spec V1 | CONCEPTUAL | Excel Treatment Lab | Falta implementación conectada. |
| Ciclos 11-14 — contables | PARTIAL / MISSING_RUNTIME | catálogo | Falta implementación validada para Servicio 1. |
| Ciclos 15-16 — IA con arnés / chatbot | DOCUMENTED_ONLY | roadmap | No abrir todavía. |

---

# 6. Claims no soportados

No se puede afirmar todavía:

```text
Servicio 1 tiene herramientas ejecutables productivas.
La factoría Exceland está integrada a PymIA-Live.
Existe service_1_pipeline.py.
Runtime First Aid está autorizado.
Commercial Modules están conectados al core.
Hay XLSX delivery First Aid funcionando.
La IA está bajo arnés operativo en Servicio 1.
Conciliación bancaria o Mercado Pago funcionan como producto Servicio 1.
Existe seed loader separado.
Los candidates están versionados como runtime.
```

---

# 7. Brechas detectadas

```text
No existe Capability Matrix V1 consolidada.
No existe Service 1 TaskSpec V1 cerrado.
No existe Service 1 Operational FSM V1 conectado.
No existe File Intake V1 productivo.
No existe XLSX Delivery V1 productivo.
No existen tools First Aid ejecutables.
No existe loader separado para First Aid pack.
No existe service_1_pipeline.py.
No existe LLM Adapter V1 para Servicio 1.
Commercial Modules siguen separados y sin integración runtime.
```

---

# 8. Decisión de gobierno

```text
No avanzar a runtime productivo.
No abrir loader.
No abrir pipeline.
No abrir XLSX delivery.
No abrir LLM adapter.
No conectar Commercial Modules.
```

Motivo:

```text
Antes falta transformar el catálogo y la arqueología en Capability Matrix V1.
```

---

# 9. Próximo documento recomendado

```text
docs/producto/PYMIA_SERVICE_1_CAPABILITY_MATRIX_V1.md
```

Objetivo:

```text
Convertir el catálogo Servicio 1 en mapa operativo.
```

Formato rector:

```text
CAPACIDAD | CLIENTE | INPUT | OUTPUT | ESTADO | DEPENDENCIAS | RIESGO
```

---

# 10. Veredicto

```text
PYMIA_SERVICE_1_ARCHAEOLOGY_AUDIT_V1 = CLOSED_AS_INITIAL_EVIDENCE
```

Condición:

```text
Este cierre no implica implementación productiva. Sólo fija el mapa arqueológico inicial y habilita el Ciclo 4: Capability Matrix V1.
```
