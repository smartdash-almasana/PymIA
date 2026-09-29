# PymIA Quality Toolchain — FASE 1-B

STATUS: REPORT-ONLY / OBSERVED ENVIRONMENT

## Objetivo

Registrar qué herramientas del Fast Quality Gate están realmente disponibles en el entorno local y qué versión ejecuta el runner.

## Estado observado — 2026-09-28

| Tool | Estado | Versión / evidencia |
|---|---|---|
| Ruff | AVAILABLE / FINDINGS | `ruff 0.16.0` |
| Pyright | NOT_AVAILABLE | no executable; no Python module |
| Architecture tests | AVAILABLE / PASS | ejecutados vía `python -m pytest -q tests/architecture` |

## Regla de reproducibilidad

El reporte JSON debe registrar:
- comando ejecutado;
- versión cuando la herramienta está disponible;
- return code;
- stdout/stderr;
- estado normalizado: `PASS / FINDINGS / NOT_AVAILABLE / ERROR`.

Una herramienta ausente nunca se convierte en PASS.

## Evidencia

Primer reporte real:
`E:\BuenosPasos\smartbridge\PYMIA_FAST_QUALITY_REPORT_V1.json`

Ese archivo es evidencia local fuera del repo, no autoridad de producto.

## Pyright

Pyright sigue siendo obligatorio en el roadmap, pero en este entorno está **NOT_AVAILABLE**.

FASE 1-B no instala ni fija una versión de Pyright por reflejo. La incorporación reproducible de Pyright requiere una microtarea posterior que decida explícitamente:
- mecanismo de instalación;
- versión/floor;
- configuración;
- alcance del baseline;
- cómo distinguir deuda histórica de findings causados por diff.

## No autorizado en esta fase

- autofix;
- remediación Ruff;
- remediación Pyright;
- bloqueo de PR;
- cambios de CI;
- cambios de product code.
