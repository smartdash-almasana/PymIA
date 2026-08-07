# Servicio 1 — Cierre del piloto controlado de conciliación V1

**Fecha:** 2026-08-07
**HEAD base:** `b240636`
**Estado:** `PASS_CONTROLLED_RECONCILIATION_PILOT`
**Alcance:** piloto técnico asistido; no es auditoría, certificación, conciliación definitiva ni cierre contable.

## 1. Objetivo cerrado

Validar el recorrido físico completo de conciliación bancaria con dos fuentes XLSX reales del piloto:

```text
carga de dos fuentes
→ confirmación explícita de columnas
→ raíz única de Servicio 1
→ matcher determinístico
→ revisión humana
→ decisiones pendientes
→ papel de trabajo XLSX
→ comparación posterior contra control esperado
```

## 2. Fuentes del piloto

```text
E:\BuenosPasos\smartbridge\PymIA_piloto_conciliacion\01_COBRANZAS_ESPERADAS.xlsx
E:\BuenosPasos\smartbridge\PymIA_piloto_conciliacion\02_MOVIMIENTOS_BANCARIOS.xlsx
E:\BuenosPasos\smartbridge\PymIA_piloto_conciliacion\CONTROL_ESPERADO.md
```

Hashes observados antes y después:

```text
01_COBRANZAS_ESPERADAS.xlsx
80e7dab58d0fea6f1a6114a7c877d9b8a5b0d89a217dc434885890dd236b8262

02_MOVIMIENTOS_BANCARIOS.xlsx
c346adfdf80adf9112d47915e24ccaf6dc424bf483a1553f887ca34ed0e0bfab

CONTROL_ESPERADO.md
6c21847b2ab1d7c009979806ea64f81ad4402dbb72c3706dd36343211e1f4185
```

Resultado: `sources_unchanged = true`.

El control no fue enviado a PymIA. Se utilizó sólo después de obtener el resultado para la comparación técnica.

## 3. Defectos cerrados durante el piloto

1. pérdida del vínculo entre encabezado visible y clave normalizada;
2. fecha física de Excel no canonizada al formato de día;
3. depósitos agrupados `1:N` no reconstruidos desde referencia compuesta y suma;
4. pagos divididos `N:1` no reconstruidos desde referencia repetida y suma;
5. duplicados exactos compitiendo con la fila original en vez de quedar explícitos.

## 4. Resultado contra el control

```text
relaciones simples: 45
- coincidencias exactas: 40
- coincidencias con demora: 5

relaciones agregadas: 5
- depósitos agrupados 1:N: 3
- pagos divididos N:1: 2

diferencias de importe: 4
diferencias de fecha: 5
grupos de duplicados exactos: 2
faltantes de evidencia: 0
```

Las relaciones agregadas se forman sólo cuando:

- la referencia declara los miembros;
- la suma coincide dentro de la tolerancia explícita vigente;
- las filas no participan de otro candidato;
- no existe solapamiento entre agregados.

Ante solapamiento, el matcher se abstiene. No usa orden de fila ni matching codicioso.

## 5. Revisión humana y pendientes

```text
pipeline_status: RECONCILIATION_REVIEW_READY
review_items_exposed: 76
CONFIRM: 0
PENDING: 76
```

Los pendientes bancarios e internos incluyen deliberadamente movimientos con diferencia de importe. Esto es consistente con la arquitectura vigente: una diferencia puede ser analizable y continuar sin imputación hasta decisión humana.

Los duplicados exactos permanecen visibles y pendientes. La fila original conserva su candidato; ninguna copia se oculta ni se autoacepta.

## 6. Papel de trabajo

```text
E:\BuenosPasos\smartbridge\PymIA_piloto_conciliacion\resultado_pymia_fecha_fix\03_PAPEL_DE_TRABAJO_PYMIA.xlsx
```

Resultado observado:

```text
HTTP: 200
bytes: 22204
hojas: 6
- Resumen
- Casos
- Decisiones
- Pendientes
- Trazabilidad
- Limites
```

El papel de trabajo no modifica las fuentes y no autoriza cierre contable.

## 7. Evidencia de pruebas

Matcher focal:

```text
21 passed
```

Regresión amplia de conciliación:

```text
162 passed
0 failed
```

Comparación ejecutable posterior al resultado:

```text
PILOT_MATCHES_CONTROL_CATEGORIES
```

No se ejecutó la suite completa del repositorio.

## 8. Salud del onboarding web general

El corte posterior verificó que los dos fallos observados pertenecían a expectativas de test anteriores al contrato vigente de primer contacto: las pruebas respondían sólo una pregunta semántica aunque la interfaz exigía confirmar todas las preguntas expuestas.

La corrección se limitó a las pruebas. El runtime conservó el comportamiento fail-closed:

```text
confirmación parcial: HTTP 400
confirmación completa: continúa a selección de revisión
onboarding web focal: 3 passed
regresión web asistida: 18 passed
regresión de conciliación: 162 passed
```

No quedan fallos conocidos del onboarding web general dentro de este corte.

## 9. Decisión

```text
PILOTO_CONTROLADO_DE_CONCILIACION: CERRADO_PASS
MATCHING_1N_N1: CERRADO
DUPLICADOS_EXACTOS: EXPLÍCITOS
REVISIÓN_HUMANA: OBLIGATORIA
AUTOACEPTACIÓN: NO
CIERRE_CONTABLE_AUTOMÁTICO: NO
TENANT_MEMORY: NO_ABIERTO
NUEVAS_CAPACIDADES: NO
COMMIT: NO
PUSH: NO
```

El cierre certifica únicamente que este piloto controlado recorre la raíz vigente, reproduce las categorías del control y genera un papel de trabajo trazable sin modificar las fuentes.


## 10. Integration readiness verification

Before integration, the repository coverage guard exposed a stale harness assumption: its physical controls did not perform the explicit first-contact owner reentry required since `b240636`. The harness was corrected without changing P6 or product runtime behavior.

```text
coverage + module disposition + product completion guards: 25 passed
first-contact / P6 / owner reentry: 81 passed
assisted web: 18 passed
reconciliation: 162 passed
```

`adjusted_operating_cash_flow` remains `PHYSICAL_PARTIAL` at `CAPABILITY_NOT_GOVERNED`. No capability was silently promoted, no automatic decision was introduced, and the controlled reconciliation pilot remains ready for integration as part of one bounded cut.
