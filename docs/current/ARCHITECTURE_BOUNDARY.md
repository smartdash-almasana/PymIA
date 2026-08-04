# Límite arquitectónico vigente

**Estado:** `ACTIVE`  
**Reconciliado:** 2026-07-29

## Flujo rector

```text
Dueño PyME
   ↕
Capa conversacional / recepción
   ↕
Superficie de aplicación
   │
   ▼
Servicio 1 — raíz productiva canónica
   │
   ▼
PymIA computacional determinística
   │
   ▼
Tools / evaluadores autorizados
   │
   ▼
Outcomes y archivos de entrega
```

Capas transversales:

```text
domain        = vocabulario y objetos de dominio
narrative     = proyección legible de evidencia
harness       = observación de ingeniería
radiography   = trazabilidad de escenarios
```

Ninguna capa transversal gobierna runtime por existir.

## Responsabilidades

### Dueño PyME

- aporta evidencia;
- declara el problema operativo;
- confirma o corrige significado;
- puede aportar nueva evidencia.

Su confirmación es evidencia semántica. No es permiso universal de ejecución o delivery.

### Capa conversacional / recepción

Puede:

- escuchar;
- formular preguntas;
- pedir evidencia;
- presentar candidatos;
- explicar límites.

No puede:

- decidir verdad operacional;
- autorizar computabilidad;
- elegir soberanamente una capacidad productiva;
- crear diagnóstico causal;
- modificar resultados calculados.

### Superficie de aplicación

Incluye componentes como:

```text
pymia/faithful_operator.py
pymia/cli/vertical_slice.py
pymia/application/vertical_pipeline.py
pymia/pipeline/admission/v1/*
```

Estas superficies pueden conectar interacción, evidencia y reportes locales, pero no constituyen una segunda raíz productiva.

### Servicio 1

Única entrada oficial:

```text
pymia/cli/service_1_product.py
```

Única raíz productiva:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
```

La raíz productiva conserva el recorrido P0–P10 y gobierna bindings, owner reentry, aprobación, requirement matching, computabilidad, ejecución y delivery autorizado.

### PymIA computacional

PymIA gobierna:

- estado;
- evidencia;
- bindings semánticos;
- bloqueos;
- P6 approval;
- P7 requirement/grain;
- P8 computability;
- selección explícitamente solicitada de capacidades;
- ejecución determinística.

### Tools y evaluadores

Ejecutan cálculos o transformaciones dentro de contratos explícitos.

No deciden por sí mismos cuándo deben ejecutarse.

### Narrative

```text
pymia/narrative/*
```

Convierte evidencia y resultados en claims legibles.

```text
NARRATIVE ≠ EVIDENCE
NARRATIVE ≠ AUTHORIZATION
```

### Domain

```text
pymia/domain/*
```

Expresa objetos de dominio puros.

No autoriza ejecución ni sustituye contratos de Servicio 1.

### Harness / Radiography

```text
pymia/operational_harness/*
pymia/pipeline_radiography/*
```

Miden, trazan y clasifican comportamiento técnico.

```text
ENGINEERING_STATUS ≠ PRODUCT_AUTHORIZATION
```

## Contabilidad y conciliación

Los contratos contables pueden vivir como soporte sin formar parte del closure productivo.

La conciliación está integrada a la raíz de Servicio 1 de forma controlada: una compuerta gobernada de solicitud (`service_1_reconciliation_request_gate_v1`) y un adaptador controlado hacia revisión asistida (`service_1_reconciliation_candidate_to_assisted_review_v1`) preparan candidatos únicamente para revisión humana. Esta integración no autoriza cierre contable, aceptación automática ni modificación de movimientos.

Ambigüedad de conciliación debe permanecer visible y escalar a revisión humana.

## Prohibiciones

- No segundo parser XLSX productivo.
- No segunda raíz productiva.
- No cadenas semánticas paralelas.
- No texto libre que convierta `unknown` en confirmado.
- No score que autorice matching, computabilidad o runtime.
- No LLM como autoridad de cálculo, diagnóstico o estado.
- No web/UI con fórmulas o verdad de negocio propia.
- No operador humano obligatorio como condición universal del producto; sí revisión humana cuando el contrato del caso sea ambiguo.
- No admission, narrative, harness o domain promovidos silenciosamente a runtime.
- No landing, demo o documentación histórica gobernando código.

## Regla de promoción

Una capa de soporte sólo entra al producto si existe:

```text
contrato
posición en P0–P10
caller productivo
fail-closed
tests
guards
clasificación PRODUCTIVE
actualización documental
```

## Documento de detalle

El mapa completo de componentes y planos está en:

```text
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
```
