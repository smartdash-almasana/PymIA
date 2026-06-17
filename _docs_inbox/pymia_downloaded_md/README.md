# PymIA Downloaded MD Inbox

## Estado

```text
IMPORTED_FOR_RECONCILIATION
NOT_ARCHITECTURAL_AUTHORITY
NOT_RUNTIME_AUTHORIZATION
NOT_PYMIA_LIVE_AUTHORIZATION
NOT_SOURCE_OF_TRUTH
```

## Propósito

Carpeta de cuarentena documental para archivos Markdown descargables generados fuera del repo vivo.

Estos documentos son insumos de reconciliación, no documentación autorizada.

## Regla

Ningún archivo de esta carpeta debe tratarse como fuente de verdad hasta ser comparado contra documentación viva del repo y promovido explícitamente a `docs/` mediante ciclo metodológico.

## Flujo

```text
_docs_inbox/pymia_downloaded_md
→ reconciliación documental
→ clasificación: COMPLEMENTS / CONTRADICTS / SUPERSEDED / PROMOTE
→ promoción explícita si corresponde
```
