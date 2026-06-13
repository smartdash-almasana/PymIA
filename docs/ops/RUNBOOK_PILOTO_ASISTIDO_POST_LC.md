# RUNBOOK — Piloto Operativo Asistido Post-LC

## Estado

`DOCUMENTO_OPERATIVO`

## Fecha

2026-06-13

## Propósito

Ejecutar un piloto operativo asistido del flujo PymIA con dueño PyME real, usando el vertical slice CLI + Language Corpus V1 (LC1-LC6).

Este runbook no abre desarrollo. No abre LC-7. No abre UI/API/SaaS/packs/Telegram/Hermes.

## Precondiciones

- Python 3.14+ instalado
- Repositorio clonado en `E:\BuenosPasos\smartbridge\PymIA` (o equivalente)
- Dependencias instaladas (`pip install -e .` o `pip install -r requirements.txt`)
- Sin archivos modificados sin commitear (confirmar con `git status --short`)
- Último commit: `2360968 feat(pymia): add Language Corpus LC1-LC6 foundation`
- Excel del dueño PyME disponible como `.xlsx`

## Comando único

```bash
python -m pymia.cli.vertical_slice \
  --excel <ruta_excel> \
  --message "<mensaje_dueño>" \
  --tenant-id <tenant_alias> \
  --intake-id <case_id> \
  --output .tmp/<case_id>_owner_report.md
```

### Flags reales del CLI

| Flag | Obligatorio | Descripción |
|---|---|---|
| `--excel` | Sí | Ruta al archivo `.xlsx` del dueño |
| `--message` | Sí | Mensaje textual del dueño (entre comillas) |
| `--tenant-id` | Sí | Alias del tenant (ej: `textil_srl_001`) |
| `--intake-id` | Sí | Identificador del caso (ej: `case_001`) |
| `--output` | No | Ruta para guardar el markdown owner-facing |
| `--formula-id` | No | Filtrar reconciliación por fórmula específica (repetible) |
| `--storage-dir` | No | Directorio de almacenamiento local (default: `.tmp/vertical_slice_storage`) |

### Ejemplo concreto

```bash
python -m pymia.cli.vertical_slice \
  --excel prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx \
  --message "tengo una textil y no me cierra la caja" \
  --tenant-id tenant_smoke_post_lc_textil \
  --intake-id intake_smoke_post_lc_textil \
  --output .tmp/post_lc_smoke_textil.md
```

## Formato de archivo aceptado

- **Soportado:** `.xlsx` (Excel)
- **Fuera de alcance:** CSV, PDF, imágenes, otros formatos (requieren desarrollo futuro)

## Artefactos generados

El sistema produce estos artefactos durante la ejecución:

| Artefacto | Dónde | Descripción |
|---|---|---|
| Markdown owner-facing | `--output` | Reporte visible para el dueño con estado, evidencia, variables y próxima pregunta |
| Evidence record | `.tmp/vertical_slice_storage/<tenant_id>/evidence/` | Registro JSONL con evidence_id, content_hash, metadata |
| Pipeline run record | `.tmp/vertical_slice_storage/<tenant_id>/pipeline_runs.jsonl` | Traza de ejecución con run_id, output_hash, steps |

## Criterio PASS del piloto

El piloto se considera PASS si el output markdown contiene:

- [ ] Estado `DELIVERED_CANDIDATE` o `BLOCKED`
- [ ] `Evidence ID` presente
- [ ] `Run ID` presente
- [ ] `Evidence SHA-256` presente
- [ ] Variables computables listadas (al menos 1)
- [ ] Labels owner-facing del Language Corpus visibles cuando aplican (formato: `label (variable_id)`)
- [ ] `## Próxima pregunta` clara y en lenguaje natural
- [ ] `## Límites` preservados (no diagnóstico, no prescriptivo, no canal productivo)

## Reglas de operación asistida

### Qué puede hacer el operador

- Leer el markdown al dueño textualmente
- Explicar que el sistema extrajo variables y tablas del Excel
- Preguntar si los datos corresponden al período que el dueño quiere analizar
- Tomar nota de correcciones del dueño (columnas malinterpretadas, datos faltantes, etc.)
- Ejecutar el comando nuevamente si el dueño corrige el Excel

### Qué NO debe hacer el operador

- Decir "el diagnóstico es..." o "el problema es..."
- Prescribir acciones (subí precios, reducí costos, etc.)
- Explicar IDs internos al dueño (`INV_001`, `historial_ventas_sku`, etc.)
- Basar la conversación en nombres snake_case
- Prometer reportes automáticos, integración SaaS, UI o app
- Afirmar que el sistema reemplaza a un contador o consultor

### Sobre IDs internos

El sistema puede mostrar IDs técnicos en el markdown:

- En la **referencia técnica** (indentada bajo la pregunta): visible para el operador
- En los **labels owner-facing**: el formato `label (variable_id)` es aceptable, el operador debe leer solo el label

El operador no debe leer ni explicar la referencia técnica al dueño a menos que el dueño pregunte explícitamente.

## Riesgos conocidos

- El CLI es local, no hay base de datos compartida ni sesión persistente entre ejecuciones
- El seed Language Corpus tiene solo 3 conceptos DRAFT (`op_sales_gross`, `op_cost_cogs`, `op_cash_collection`). Variables fuera de estos conceptos se muestran sin label owner-facing
- La próxima pregunta se genera desde reconcilición de catálogo. Si no hay catálogo que matchee, cae en pregunta genérica
- No hay soporte para reentry del dueño. El piloto es una sola ejecución lineal
- No hay almacenamiento de preguntas o respuestas del dueño más allá del reporte markdown

## Post-piloto

Después de ejecutar el piloto:

1. Guardar el markdown generado (`--output`) como evidencia
2. Registrar en el checkpoint del piloto: tenant_id, case_id, resultado (PASS/BLOCKED), observaciones del dueño
3. No abrir desarrollo nuevo basado en el piloto sin pasar por el ciclo ADR → CapabilitySpec → ModuleContract → TaskSpec

## Historial

| Fecha | Versión | Cambio |
|---|---|---|
| 2026-06-13 | 0.1.0 | Creación inicial post-LC1-LC6 |
