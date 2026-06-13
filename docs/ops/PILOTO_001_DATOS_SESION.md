# PILOTO 001 — Datos de sesión

Estado: PENDING_DATA
Frente: PILOTO_OPERATIVO_ASISTIDO_POST_LC
Runbook base: `docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md`

## 1. Identificación

| Campo | Valor |
|---|---|
| pilot_id | PILOTO_001 |
| alias_pyme | PENDIENTE |
| rubro | PENDIENTE |
| fecha_prevista | PENDIENTE |
| operador | PENDIENTE |
| tenant_alias | PENDIENTE |

## 2. Entrada requerida

| Campo | Valor |
|---|---|
| ruta_archivo_xlsx | PENDIENTE |
| mensaje_inicial_dueño | PENDIENTE |
| periodo_datos | PENDIENTE |
| columnas_esperadas | PENDIENTE |

## 3. Datos que no se piden todavía

- Integraciones bancarias.
- Acceso a sistemas contables.
- Credenciales.
- Datos fiscales sensibles no necesarios para el primer smoke asistido.
- Pronóstico.
- Decisiones o autorizaciones de acción.

## 4. Comando preparado

```bash
python -m pymia.cli.vertical_slice \
  --excel <ruta_archivo_real.xlsx> \
  --message "<mensaje_dueño>" \
  --tenant-id <tenant_alias> \
  --intake-id PILOTO_001 \
  --output .tmp/PILOTO_001_owner_report.md
```

## 5. Precondiciones de ejecución

- El archivo existe y es `.xlsx`.
- El archivo no está protegido ni corrupto.
- El dueño aportó una frase inicial textual.
- El operador no modifica código para adaptar el caso.
- El operador no promete diagnóstico final, SaaS, pronóstico ni automatización.

## 6. Criterio PASS

- El comando termina sin error.
- Se genera markdown owner-facing.
- Estado final: `DELIVERED_CANDIDATE` o `BLOCKED`.
- `Evidence ID` presente.
- `Run ID` presente.
- hash presente.
- Salida entendible para el dueño.
- Próxima pregunta clara.
- Sin diagnóstico final.
- Sin prescripción.

## 7. Criterio BLOCKED

- Archivo ilegible, protegido o corrupto.
- Evidencia mínima insuficiente.
- Salida inentendible para el dueño.
- El operador necesita intervenir demasiado.
- El dueño no reconoce sus datos.

## 8. Registro post-sesión

| Campo | Valor |
|---|---|
| pilot_id | PILOTO_001 |
| fecha_real | PENDIENTE |
| archivo_usado | PENDIENTE |
| mensaje_inicial | PENDIENTE |
| estado_final | PENDIENTE |
| evidence_id | PENDIENTE |
| run_id | PENDIENTE |
| hash | PENDIENTE |
| variables_detectadas | PENDIENTE |
| labels_lc_visibles | PENDIENTE |
| faltantes | PENDIENTE |
| reaccion_dueño | PENDIENTE |
| proxima_accion_humana | PENDIENTE |

## 9. Decisión operativa

Este documento permite preparar la sesión sin abrir código ni nuevos frentes. La ejecución queda bloqueada hasta completar los campos PENDIENTE de identificación y entrada requerida.
