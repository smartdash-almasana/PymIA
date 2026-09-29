# PymIA Software Health

STATUS: FASE 1-A / REPORT-ONLY

Este directorio implementa el primer scaffold del Roadmap **Salud Integral del Software**.

## Objetivo

Tener un único punto de entrada reproducible para observar salud del repo sin modificar producto ni convertir findings históricos en fallos bloqueantes.

## FASE 1-A

Runner:

`scripts/quality/fast_quality_gate.py`

Cobertura inicial:

- Ruff
- Pyright
- architecture tests existentes

Semántica:

- `PASS`: herramienta ejecutó sin findings.
- `FINDINGS`: herramienta ejecutó y reportó findings.
- `NOT_AVAILABLE`: herramienta no está disponible en el entorno.
- `ERROR`: la herramienta no pudo completar correctamente.

En esta fase:

- `FINDINGS` no bloquea.
- `NOT_AVAILABLE` no se interpreta como defecto de producto.
- no hay autofix.
- no se cambian oráculos.
- no se modifica código productivo.

## Ejecución

`python scripts/quality/fast_quality_gate.py`

Selección focal:

`python scripts/quality/fast_quality_gate.py --tool ruff --tool architecture`

Salida JSON opcional:

`python scripts/quality/fast_quality_gate.py --output <path>.json`

## Próximos escalones

Semgrep, Bandit, pip-audit, Gitleaks, Vulture y coverage se incorporan en fases posteriores del Fast Quality Gate, con autorización separada.

Este documento no convierte el roadmap en autoridad normativa. NOP y owner decision siguen gobernando.
