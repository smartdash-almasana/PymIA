# Servicio 1 — Piloto 008 textil completa

**Ciclo:** `CYCLE_037_RUN_S1_PILOT_008_TEXTIL_COMPLETA`  
**Estado:** `PASS`

## Caso

```text
Fixture: prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx
Hoja primaria: ventas
Entrada oficial: python -m pymia.cli.service_1_product
```

## Ejecución observada

Primer pase:

```text
Estado: NEEDS_OWNER_CONFIRMATION
Preguntas al dueño: 4
Columnas: cliente, descuento_pct, medio_cobro, plazo_cobro_dias
Tools ejecutadas: false
```

La reentrada semántica utilizó exclusivamente opciones canónicas ofrecidas por `allowed_option_ids`. Las cuatro respuestas seleccionaron la opción `A`; no se utilizó texto libre.

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

- El recorrido canónico funciona sobre la hoja `ventas` de un workbook textil completo multihoja.
- El primer pase bloquea antes de ejecutar tools.
- La confirmación del dueño forma parte de la lectura semántica.
- La reentrada acepta opciones canónicas y no texto libre.
- La tool se ejecuta únicamente por solicitud explícita.
- Se produce un XLSX trazable.

## Límites

- No existe selección automática de tool desde el workbook.
- No se declara diagnóstico textil integral.
- No se agregan fórmulas, patologías ni capacidades semánticas.
- El piloto no promueve `REN_001`; su evaluador permanece `SUPPORT_NECESSARY` y fuera de la raíz productiva.
- La evidencia detallada vive en `docs/service_1_pilot_008_textil_completa.v1.json`.
