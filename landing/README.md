# Landing governance

## Estado

LANDING_GOVERNANCE_SANITIZED_V1

## Regla

La carpeta `landing/` no gobierna Servicio 1.

La autoridad operativa está en:

```text
docs/current/
PymIA-Live/pymia/smartpyme/
PymIA-Live/pymia/contracts/
```

## Único smoke permitido

```text
landing/service_1_excel_upload_smoke.html
```

Rol: smoke técnico local/browser-only para verificar captura de archivo Excel y preview estructural, sin diagnóstico ni ejecución de runtime.

## Demos y prototipos archivados

Los flujos demo/prototipo fueron archivados en:

```text
landing/archive_demo/
landing/archive_prototype/
```

No deben reactivarse como flujo operativo.

## Prohibiciones

En `landing/` queda prohibido:

- diagnóstico de negocio;
- reportes ficticios;
- métricas inventadas;
- simulación de análisis;
- runtime;
- tool run;
- delivery;
- mezcla de marketing demo con intake real.
