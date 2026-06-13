# OD1 — Owner Decision Capture Boundary for Confirmed Catalog Summary Checkpoint

Estado: `ACCEPTED`

Fecha: 2026-06-12

## 1. Alcance

OD1 define documentalmente la frontera entre:

```text
catalog_summary_confirmed
```

y un `DecisionRecord` formal compatible con:

```text
docs/contratos/owner-decision-v1.md
```

## 2. Fuentes rectoras

```text
docs/adr/ADR-025-faithful-operator-output-vs-owner-report-delivery-boundary.md
docs/pymia/POST_ADR_025_NEXT_FRONT_CLASSIFICATION_TASKSPEC.md
docs/contratos/owner-decision-v1.md
docs/pymia/OD1_OWNER_DECISION_CAPTURE_BOUNDARY_FOR_CONFIRMED_CATALOG_SUMMARY_CAPABILITYSPEC.md
```

## 3. Decisión certificada

```text
catalog_summary_confirmed ≠ APPROVE
catalog_summary_confirmed ≠ AUTHORIZE_ACTION
catalog_summary_confirmed ≠ DecisionRecord
```

Una confirmación semántica del dueño puede confirmar que una síntesis representa su situación, pero no autoriza acción, ejecución, delivery ni reporte productivo.

## 4. Qué queda permitido

Después de OD1 queda permitido, sólo a nivel documental, diseñar un TaskSpec futuro para clasificar potencial de decisión local.

Ese TaskSpec deberá mantener:

```text
- no persistencia productiva;
- no canal externo;
- no ejecución de acciones;
- no delivery;
- no PDF;
- no Telegram;
- no DB;
- no Hermes;
- no runtime externo;
- no M36;
- no nuevos puertos o gates formales;
- no cambios en matcher ni catálogos;
- no conversión automática de confirmación semántica en autorización.
```

## 5. Qué NO autoriza OD1

```text
- C4;
- delivery;
- Owner-Facing Report V1;
- reporte productivo;
- PDF;
- Telegram;
- DB;
- Hermes;
- runtime externo;
- diagnóstico final;
- recomendaciones definitivas;
- ejecución de acciones;
- M36;
- modificación de owner-decision-v1;
- modificación de catálogos;
- modificación del matcher.
```

## 6. Auditoría

Auditoría realizada por ChatGPT sobre las fuentes rectoras indicadas.

Resultado:

```text
VEREDICTO: PASS
RIESGOS DETECTADOS: Ninguno bloqueante
CORRECCIONES OBLIGATORIAS: Ninguna
OD1 ACCEPTED SIN CAMBIOS
```

## 7. Próximo paso posterior

Título del paso posterior:

```text
OD1-T1 — Local Owner Decision Potential Classifier TaskSpec
```

Objetivo del paso posterior:

```text
Definir un TaskSpec de implementación local, no productiva, que clasifique si una respuesta del dueño posterior a C3 tiene potencial de DecisionRecord o debe quedar como confirmación semántica, aclaración, corrección, incertidumbre o bloqueo.
```

Condición:

```text
OD1-T1 debe ser auditado antes de código.
```
