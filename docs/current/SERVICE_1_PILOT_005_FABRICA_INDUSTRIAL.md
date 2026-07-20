# Servicio 1 — Piloto 005 fábrica industrial

**Ciclo:** `CYCLE_038_RUN_S1_PILOT_005_FABRICA_INDUSTRIAL`  
**Estado:** `PASS`

## Caso

```text
Fixture: prueba_excels/fabrica_industrial_compleja.xlsx
Hoja primaria: PRODUCCION
Entrada oficial: python -m pymia.cli.service_1_product
```

## Ejecución observada

Primer pase:

```text
Estado: NEEDS_OWNER_CONFIRMATION
Preguntas al dueño: 7
Tools ejecutadas: false
```

La reentrada semántica utilizó exclusivamente opciones canónicas ofrecidas por `allowed_option_ids`. Las respuestas observadas seleccionaron la opción `A`; no se utilizó texto libre.

Segundo pase:

```text
Estado: PRODUCT_PIPELINE_READY
Bloqueo: ninguno
Bindings confirmados: true
Tool explícita: precio_margen_basico
Tools ejecutadas: true
Salida XLSX: first_aid_001_precio_margen_basico.xlsx
```

## Qué certifica

- El recorrido canónico funciona sobre la hoja `PRODUCCION` del workbook industrial.
- El primer pase bloquea antes de ejecutar tools.
- La confirmación del dueño forma parte de la lectura semántica.
- La reentrada acepta opciones canónicas y no texto libre.
- La tool se ejecuta únicamente por solicitud explícita.
- Se produce un XLSX trazable.

## Límites

- No existe selección automática de tool desde el workbook.
- No se declara diagnóstico industrial integral.
- `scrap`, `oee`, eficiencia de máquina, paradas y pérdidas productivas no quedan promovidos a fórmulas ni diagnósticos soportados.
- No se agregan fórmulas, patologías ni capacidades semánticas.
- La evidencia detallada vive en `docs/service_1_pilot_005_fabrica_industrial.v1.json`.
