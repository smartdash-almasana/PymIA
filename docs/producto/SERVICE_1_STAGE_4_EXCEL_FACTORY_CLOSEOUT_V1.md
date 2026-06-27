# SERVICE_1_STAGE_4_EXCEL_FACTORY_CLOSEOUT_V1

## Estado

```text
SERVICE_1_STAGE_4_EXCEL_FACTORY_CLOSEOUT_V1: CREATED
ETAPA_4_FACTORY_EXCEL: CLOSED_IN_SCOPE_RUNTIME
DOC_PURPOSE: closeout documental mínimo de la Resolución de Factoría Excel
```

Este documento cierra documentalmente la Etapa 4 de Servicio 1: Resolución de Factoría Excel.

No abre una etapa nueva.

No autoriza pipeline full.

No autoriza delivery owner-facing automático.

No modifica el alcance de First Aid, Excel Lab ni servicios contables.

---

## 1. Contexto

La Etapa 4 nació para resolver el cuello de botella documentado de Factoría Excel:

```text
exeland2 externo
+ bridge lógico mínimo
+ falta de ejecución física controlada desde PymIA-Live
```

Ese estado anterior ya no representa completamente el estado técnico actual.

A la fecha de este closeout, PymIA-Live puede invocar la Factoría Excel bajo una ruta explícita y controlada desde el operador CLI.

---

## 2. Commits de cierre de Etapa 4

```text
Slice 1:
aeaa4af feat(pymia-live): formalize exceland factory dependency and add smoke test

Slice 2:
85700f1 feat(pymia-live): add exceland runtime adapter

Slice 3:
9d97b82 feat(pymia-live): wire exceland bridge to runtime adapter

Slice 4:
8af539f feat(pymia-live): wire exceland execution flow into operator cli
```

---

## 3. Arquitectura final cerrada en alcance

```text
exceland_bridge_v1.py
  -> valida contrato lógico de solicitud Exceland

exceland_runtime_v1.py
  -> ejecuta exceland_factory.build_product(...)
  -> genera XLSX físico mediante dependencia exeland-factory

exceland_execution_flow_v1.py
  -> orquesta bridge -> mapping explícito -> runtime
  -> falla cerrado si bridge/runtime/mapping no pasan

service_1_operator.py
  -> expone --run-factory como rama explícita de operador
```

Dependencia declarada:

```text
PymIA-Live/pyproject.toml
exceland-factory @ file:../../../exeland2
```

Esta dependencia queda aceptada como estrategia de workspace para la Etapa 4, no como decisión final de distribución del producto.

---

## 4. Rama CLI de Factoría Excel

El operador CLI acepta:

```text
--run-factory
--template-ref
--formula-ref         repetible
--factory-input       key=value repetible
--factory-output      opcional
```

Salida visible esperada para operador:

```text
Factoría Excel
- Estado: <status>
- Producto: <product_ref>
- Archivo: <output_path>
- Artifact existe: <artifact_exists>
- Revisión humana requerida: true
- Runtime autorizado: false
```

El resultado se registra en:

```text
factory_result.json
```

y el artefacto XLSX generado se trackea en el manifest de caso cuando existe.

---

## 5. Templates mapeados

El mapping `template_ref -> product_ref` es explícito y deliberadamente chico.

```text
precio_margen_basico_template -> precio_margen
caja_diaria_template          -> caja_diaria
stock_alertas_basicas_template -> stock_control
```

Estos templates pueden llegar a runtime físico si el bridge valida y el runtime responde OK.

---

## 6. Templates soportados por bridge pero no mapeados a runtime

```text
gastos_triage_template
proveedores_precio_variacion_template
```

Estado esperado:

```text
TEMPLATE_NOT_MAPPED
```

Motivo:

```text
exeland2 no tiene specs/product_ref cerrados para esos productos dentro del mapping mínimo actual.
```

No deben sobreprometerse como productos XLSX físicos disponibles.

---

## 7. Qué sí hace esta Etapa 4 cerrada

```text
- Declara dependencia workspace a exeland2 vía pyproject.toml.
- Verifica importabilidad/uso básico de exceland_factory.
- Agrega runtime adapter controlado en PymIA-Live.
- Agrega execution flow bridge -> mapping -> runtime.
- Agrega rama CLI explícita --run-factory.
- Genera XLSX físico para templates mapeados.
- Registra factory_result.json.
- Expone output_path y artifact_exists.
- Falla cerrado en bridge fail, template no mapeado o runtime fail.
```

---

## 8. Qué no hace esta Etapa 4

```text
- No integra Factoría Excel al pipeline full de Servicio 1.
- No modifica service_1_pipeline_v1.py.
- No modifica service_1_xlsx_delivery_v1.py.
- No usa delivery genérico para esta rama.
- No convierte factory output en owner-facing delivery final.
- No ejecuta diagnóstico contable.
- No reemplaza revisión humana.
- No amplía automáticamente templates no mapeados.
- No internaliza exeland2 dentro del repo PymIA.
```

---

## 9. Validación técnica de cierre

Suite objetivo reportada/auditada:

```text
python -m pytest \
  tests/smartpyme/test_service_1_operator_cli.py \
  tests/smartpyme/test_exceland_execution_flow_v1.py \
  tests/smartpyme/test_exceland_runtime_v1.py \
  tests/smartpyme/test_exceland_bridge_v1.py \
  tests/smartpyme/test_exceland_factory_smoke_v1.py \
  -q
```

Resultado auditado:

```text
47 passed
```

Distribución reportada:

```text
16 CLI
10 execution flow
9 runtime
9 bridge
3 smoke
```

---

## 10. Estado documental corregido por este closeout

Quedan obsoletas como descripción completa del estado actual las afirmaciones previas que decían:

```text
- Factoría Excel = PARTIAL_EXTERNAL_DEPENDENCY sin generación física controlada.
- exeland2/factory genera XLSX, pero no está conectada a PymIA-Live.
- el bridge existe, pero todavía NO ejecuta Exceland real.
- falta frontera runtime para compilar/generar XLSX real.
```

Lectura actual correcta:

```text
Factoría Excel está CLOSED_IN_SCOPE_RUNTIME para su ruta explícita de operador CLI.
```

Pero esta lectura no equivale a Servicio 1 full.

---

## 11. Estado final

```text
ETAPA_4_FACTORY_EXCEL:
CLOSED_IN_SCOPE_RUNTIME

ENTRYPOINT:
pymia/cli/service_1_operator.py --run-factory

RUNTIME_PATH:
service_1_operator.py
-> exceland_execution_flow_v1.py
-> exceland_bridge_v1.py
-> explicit template_ref/product_ref mapping
-> exceland_runtime_v1.py
-> exceland_factory.build_product(...)

OWNER_DELIVERY:
NOT_IN_SCOPE

PIPELINE_FULL:
NOT_IN_SCOPE

HUMAN_REVIEW:
REQUIRED

RUNTIME_AUTHORIZED_FLAG:
false
```

---

## 12. Próximo paso recomendado

No abrir una nueva implementación desde este documento.

Próximo paso seguro:

```text
SERVICE_1_FULL_CURRENT_CAPABILITY_AUDIT_V1
```

Objetivo:

```text
Auditar qué puede hacer hoy Servicio 1 completo después de First Aid, Excel Lab y Factoría Excel, sin tocar código.
```
