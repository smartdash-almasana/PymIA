# PILOTO_REAL_001 — Plan Operativo Minimo

Estado: PLANNED
Fecha: 2026-06-13
Fuente base: `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md`

## 1. Identificacion

- `pilot_id`: `PILOTO_REAL_001`
- `alias_pyme`: `PENDIENTE`
- `rubro`: `PENDIENTE`
- `fecha prevista`: `PENDIENTE`
- `operador`: `PENDIENTE`
- `estado inicial`: `PLANNED`

## 2. Entrada requerida

### Archivo esperado

- Formato obligatorio: `.xlsx`
- Ruta esperada: `PENDIENTE`
- El archivo debe ser legible localmente y no estar protegido.

### Mensaje inicial del dueno

- Texto obligatorio: `PENDIENTE`
- Debe ser una frase real del dueno sobre su problema operativo.

### Periodo de datos

- Periodo esperado: `PENDIENTE`
- Debe poder reconocerse por el operador antes de ejecutar el piloto.

### Columnas minimas esperadas

- ventas
- costos
- productos
- periodo

### Datos que NO pedir todavia

- Decision final del dueno
- Plan de accion
- Recomendacion ejecutiva
- Integraciones
- PDF final
- Datos fuera del foco inicial si no bloquean la lectura minima

## 3. Comando preparado

```bash
python -m pymia.cli.vertical_slice \
  --excel <ruta_archivo_real.xlsx> \
  --message "<mensaje_dueño>" \
  --tenant-id <tenant_alias> \
  --intake-id <pilot_id> \
  --output .tmp/<pilot_id>_owner_report.md
```

Plantilla concreta para completar:

```bash
python -m pymia.cli.vertical_slice \
  --excel PENDIENTE_RUTA_XLSX \
  --message "PENDIENTE_MENSAJE_DUENO" \
  --tenant-id PENDIENTE_TENANT_ALIAS \
  --intake-id PILOTO_REAL_001 \
  --output .tmp/PILOTO_REAL_001_owner_report.md
```

## 4. Criterio de ejecucion

- No ejecutar si el archivo no es `.xlsx`.
- No ejecutar si el dueno no aporta frase inicial.
- No ejecutar si el archivo esta protegido o corrupto.
- No editar codigo para adaptar el caso.
- No abrir runtime, UI, API, SaaS, packs, Telegram, Hermes ni conversa-engine.
- Tolerancia local permitida para esta sesion:
  - `.tmp/`
  - `_local_quarantine/`

## 5. Criterio PASS

- Comando termina sin error.
- Markdown generado en `.tmp/PILOTO_REAL_001_owner_report.md`.
- Estado `DELIVERED_CANDIDATE` o `BLOCKED`.
- `evidence_id` presente.
- `run_id` presente.
- Hash presente.
- Salida entendible para dueno.
- Proxima pregunta clara.
- No diagnostico final.
- No prescripcion.

## 6. Criterio BLOCKED

- Archivo ilegible.
- Evidencia minima insuficiente.
- Salida inentendible.
- El operador necesita intervenir demasiado para explicar lo que el reporte quiso decir.
- El dueno no reconoce sus datos como propios o correctos.

## 7. Registro post-sesion

| pilot_id | fecha real | archivo usado | mensaje inicial | estado final | evidence_id | run_id | hash | variables detectadas | labels LC visibles | faltantes | reaccion del dueno | proxima accion humana |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PILOTO_REAL_001 | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE | PENDIENTE |

## 8. Datos faltantes antes de ejecutar

Faltan estos datos concretos para poder correr el piloto real:

- `alias_pyme`
- `rubro`
- `fecha prevista`
- `operador`
- ruta real del archivo `.xlsx`
- mensaje inicial textual del dueno
- periodo de datos a observar
- `tenant_alias` a usar en el comando

## 9. Decision operativa actual

El piloto queda preparado, pero no ejecutable todavia mientras existan campos `PENDIENTE`.
