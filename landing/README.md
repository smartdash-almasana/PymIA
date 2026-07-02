# Landing governance

## Estado

LANDING_GOVERNANCE_SANITIZED_V1

## Regla

La carpeta `landing/` no gobierna Servicio 1.

No es fuente de verdad de runtime, diagnóstico, evidencia, conversación semántica ni delivery.

## Permitido por ahora

```text
landing/service_1_excel_upload_smoke.html
```

Rol: smoke técnico local/browser-only para verificar que un XLSX puede ser leído en navegador y mostrar estructura sin diagnóstico.

## No operativo

Los siguientes archivos quedan explícitamente desautorizados para flujo operativo hasta ser eliminados o archivados físicamente:

```text
landing/index.html
landing/app.js
landing/servicio1-excel-ingestion-chat.html
landing/src/pages/index.astro
landing/src/components/FileIngestionPanel.astro
landing/src/components/ReportPreview.astro
```

Motivo:

```text
mezclan landing/demo/prototipo con simulación, hardcode, promesas comerciales o conversación no gobernada por contratos reales.
```

## Fuente de verdad

```text
docs/current/
PymIA-Live/pymia/smartpyme/
PymIA-Live/pymia/contracts/
```

## Prohibido en landing operativa

- diagnóstico de negocio;
- reportes ficticios;
- métricas inventadas;
- branching por filename;
- semántica no confirmada por el dueño;
- runtime/tool/delivery;
- mezcla de marketing demo con intake real.
