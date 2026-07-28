# M31 — Servicio asistido repetible

## Alcance

M31 define un **servicio asistido repetible**.
No declara producto final.
No declara autonomía end-to-end.
No declara servicio comercial validado.

## Fronteras fuera de alcance

- `registry/capabilities.yaml`
- dispatcher
- telegram/pdf/html/ui
- erp/odoo/dolibarr
- llm/red
- producto final

## Criterio de entrada

- intake mínimo disponible
- evidencia inicial recibida
- problema del dueño explicitado
- caso identificable

## Criterio de bloqueo

- evidencia insuficiente
- semántica no confirmada
- archivos ilegibles
- dependencia externa no autorizada
- bloqueos operativos sin aclaración del dueño

## Checklist de ejecución

1. intake
2. evidencia
3. análisis
4. reporte
5. continuidad
6. medición
7. aprendizaje PymIA

## Criterio de repetibilidad

El caso se puede repetir sin improvisar cuando existe secuencia estable, entradas mínimas claras, checklist ejecutable y salida comparable.

## Criterio de no repetibilidad

No se puede repetir sin improvisar cuando cambia el criterio operativo del caso, faltan datos mínimos o el flujo depende de interpretación ad hoc.

## Plantilla de pilot record

```text
pilot_id
tenant_id
case_id
problema_declarado
archivos_recibidos
estado_evidencia
hallazgos
reporte_ref
proximo_paso
min_total
bloqueos
aprendizajes
casos_totales
casos_entregados
casos_bloqueados
tiempo_promedio_total
se_puede_repetir_sin_improvisar
```

## Medición

- casos_totales
- casos_entregados
- casos_bloqueados
- tiempo_promedio_total
- se_puede_repetir_sin_improvisar

## Aprendizaje PymIA

Todo aprendizaje debe quedar separado de ejecución y evidencia.
