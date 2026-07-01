# 04 — Deuda técnica y riesgos

## Riesgo 1 — Hermes como deuda masiva

Se detectaron 309 archivos con referencias a Hermes y 2495 referencias textuales. Esto representa deuda conceptual, documental y técnica.

Riesgo: que futuros LLMs reinterpreten Hermes como vigente y reconstruyan una arquitectura que el dueño del proyecto ya descartó.

Acción: retiro total, reemplazo por contratos neutrales y limpieza de tests/imports.

## Riesgo 2 — Documentación superior a ejecución

El repo contiene 792 archivos Markdown y 922 archivos Python. Hay 195 archivos `*service_1*.py` y múltiples documentos de cierre/checkpoint.

Riesgo: sensación de avance por densidad documental, sin validación proporcional en caso real.

Acción: congelar documentación nueva salvo que sea requerida por caso real, issue técnico, ADR o corrección de autoridad.

## Riesgo 3 — `vertical_pipeline.py` como concentrador

Archivo observado: `PymIA-Live/pymia/application/vertical_pipeline.py`, 566 líneas.

Concentra lectura de Excel, construcción de evidencia, reconciliación, reporte owner-facing, adapter diagnóstico, question alignment y registro de pipeline.

Riesgo: reemplazar el viejo script gigante por un nuevo ensamblador gigante.

Acción: no agregar responsabilidades nuevas sin extraer módulos con contrato/test.

## Riesgo 4 — Imports rotos en núcleo vivo

Smoke test selectivo en `PymIA-Live` falló por import roto de `load_formula_rules` desde `pymia.contracts.formula_rules_v1`.

El import aparece en `PymIA-Live/pymia/smartpyme/diagnostic_operator_adapter.py`.

El módulo target existe pero está vacío o no exporta la función esperada: `PymIA-Live/pymia/contracts/formula_rules_v1.py`.

Acción: corregir contrato/import antes de nuevas features.

## Riesgo 5 — Persistencia asimétrica

`pipeline_registration.py` usa storage para varios registros, pero escribe `pipeline_runs.jsonl` directamente.

Riesgo: duplicación de política de persistencia, difícil migración a backend alternativo.

Acción: unificar escritura en `storage.py` o crear puerto/repositorio explícito.

## Riesgo 6 — Dependencia local externa

`PymIA-Live/pyproject.toml` contiene una dependencia local hacia `exeland2`.

Riesgo: instalación no reproducible en otra máquina si esa ruta exacta no existe.

Acción: vendorizar, publicar paquete, fijar submódulo o reemplazar por dependencia interna clara.

## Riesgo 7 — Archivos vacíos por extracción parcial

Se detectaron 166 archivos vacíos en la extracción auditada. Algunos son relevantes:

- `tests/architecture/policy.py`
- `pymia/smartpyme/owner_facing_report.py`
- `PymIA-Live/pymia/contracts/formula_rules_v1.py`
- `docs/current/SAAS_AUTONOMY_TARGET.md`

Riesgo: conclusiones técnicas incompletas si el archivo original no estaba vacío.

Acción: verificar repo Git original o reexportar comprimido limpio antes de aplicar cambios masivos.

## Riesgo 8 — SaaS/autonomía prematura

`docs/current/PRODUCT_VISION.md` habla de SaaS autónomo con IA conversacional, pero el estado ejecutable apunta a servicio asistido.

Riesgo: diseñar infraestructura para un futuro no validado por caso real.

Acción: diferir Phase G / autonomía / SaaS hasta completar caso real supervisado.

## Riesgo 9 — Catálogo activable insuficiente

Hay catálogos y labels amplios, pero no debe asumirse que todas las patologías son detectables.

Riesgo: sobrepromesa comercial o diagnóstica.

Acción: separar catálogo activo, aspiracional y presentation-only.

## Riesgo 10 — Tests numerosos pero no necesariamente productivos

El repo contiene una suite grande. Sin embargo, pruebas selectivas fallan en collection y hay tests legacy/vacíos.

Riesgo: contar tests no equivale a tener cobertura efectiva del pipeline vivo.

Acción: construir una suite mínima de smoke tests vivos y distinguirla del archivo histórico.
