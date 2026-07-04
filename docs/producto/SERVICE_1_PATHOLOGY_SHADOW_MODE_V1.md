# SERVICE_1_PATHOLOGY_SHADOW_MODE_V1

## Estado

```text
Tipo: PRODUCT_RUNTIME_INTEGRATION_METHOD
Servicio: SERVICE_1 / SmartPyme
Estado: DRAFT_CANONICAL_CANDIDATE
Runtime impact: SHADOW_ONLY
Code impact: NONE_IN_THIS_DOCUMENT
Tests impact: NONE_IN_THIS_DOCUMENT
```

Este documento fija la metodología preferida para integrar el catálogo de patologías PyME en Servicio 1 sin romper el flujo operativo existente.

---

## 1. Decisión metodológica

Para el catálogo de patologías, la metodología preferida NO es construir una capa aislada durante semanas y conectarla al final.

La metodología preferida es:

```text
Feature flag
+
Shadow mode
+
Artefacto observacional
+
Cero cambio en decisiones del pipeline
```

---

## 2. Regla central

El catálogo debe enchufarse temprano al runtime existente, pero al principio no debe decidir nada.

```text
Servicio 1 corre como siempre.
El catálogo observa el caso.
El catálogo genera candidatos de patología.
El pipeline original sigue mandando.
La entrega existente no se modifica.
```

---

## 3. Artefacto de salida shadow

El primer entregable técnico del shadow mode debe ser:

```text
pathology_candidates.json
```

Ese archivo debe generarse junto al paquete de caso o carpeta de entrega existente.

Ejemplo:

```json
{
  "case_id": "CASE_ID",
  "mode": "SHADOW_MODE",
  "runtime_decision": "NO_EFFECT",
  "detected_candidates": [
    {
      "pathology_id": "REN_001",
      "name": "margen_invisible",
      "domain": "rentabilidad",
      "confidence": "candidate",
      "matched_signals": [
        "vendo pero no sé si gano"
      ],
      "missing_evidence": [
        "costo_unitario",
        "comisiones",
        "impuestos"
      ],
      "suggested_formulas": [
        "Margen bruto por producto",
        "Margen neto",
        "Precio de venta con margen objetivo"
      ]
    }
  ]
}
```

---

## 4. Qué NO puede hacer shadow mode

En esta fase el catálogo no puede:

```text
- bloquear el caso;
- cambiar el routing;
- elegir tools obligatorias;
- modificar entregables existentes;
- alterar el estado del pipeline;
- reemplazar validaciones actuales;
- generar diagnóstico final autónomo.
```

---

## 5. Qué SÍ puede hacer shadow mode

En esta fase el catálogo sí puede:

```text
- leer señales textuales del dueño si están disponibles;
- leer metadata del caso si está disponible;
- proponer patologías candidatas;
- listar evidencia faltante;
- sugerir fórmulas o skills asociados;
- producir un artefacto JSON adicional;
- habilitar auditoría humana o automática posterior.
```

---

## 6. Feature flag

La integración debe quedar controlada por feature flag.

Nombre recomendado:

```text
SERVICE_1_PATHOLOGY_SHADOW_MODE
```

Estados:

```text
OFF
SHADOW_ONLY
ADVISORY
ROUTING_CANDIDATE
ACTIVE
```

Fase inicial obligatoria:

```text
SHADOW_ONLY
```

---

## 7. Camino de promoción

El catálogo debe avanzar por etapas:

```text
1. OFF
2. SHADOW_ONLY
3. ADVISORY
4. ROUTING_CANDIDATE
5. ACTIVE
```

### 7.1 OFF

No se ejecuta.

### 7.2 SHADOW_ONLY

Observa y genera `pathology_candidates.json`.

No altera el runtime.

### 7.3 ADVISORY

Puede aparecer en reportes internos o en outputs no vinculantes.

Todavía no decide.

### 7.4 ROUTING_CANDIDATE

Puede sugerir qué microservicio conviene ejecutar, pero la decisión sigue controlada por el pipeline existente.

### 7.5 ACTIVE

Puede participar en routing y diagnóstico final, sólo después de evidencia suficiente y tests.

---

## 8. Por qué reemplaza al enfoque anterior como default

El enfoque de micro-slices aislados sigue siendo válido para cambios peligrosos.

Pero para el catálogo de patologías no debe ser el default porque retrasa la integración real.

La razón:

```text
Una capa aislada puede funcionar sola y fallar al conectarse.
Shadow mode se conecta temprano y no rompe porque no decide.
```

---

## 9. Regla práctica para PymIA

```text
Si una capacidad nueva puede observar sin decidir:
usar SHADOW MODE.

Si una capacidad nueva cambia decisiones críticas:
usar micro-slice aislado primero.
```

El catálogo de patologías entra en la primera categoría.

---

## 10. Encaje con Servicio 1

El orden correcto para Servicio 1 es:

```text
Dueño expresa dolor
↓
Servicio 1 corre normal
↓
Catálogo observa en shadow mode
↓
Genera pathology_candidates.json
↓
Se revisa calidad de candidatos
↓
Luego se promueve gradualmente
```

---

## 11. Estado final

```text
SERVICE_1_PATHOLOGY_SHADOW_MODE_V1: CREATED
RUNTIME_TOUCHED: NO
CODE_TOUCHED: NO
TESTS_REQUIRED_NOW: NO
NEXT_STEP: IMPLEMENT_SHADOW_ARTIFACT_GENERATION_UNDER_FEATURE_FLAG
```
