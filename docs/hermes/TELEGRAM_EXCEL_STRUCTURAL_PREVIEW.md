# Telegram Excel Structural Preview

Estado: temporal y operativo.

Este documento encuadra la capacidad agregada en:

```text
4ba04fe feat(telegram): add temporary Excel structural summary
```

## Decision

`pymia.telegram_excel_summary` es una vista estructural temporal de archivos tabulares recibidos por Telegram directo.

No es el diagnostico de negocio final.
No reemplaza `excel_diagnostic`.
No reemplaza `pymia.smartpyme.microservice_dispatcher.dispatch_candidate(...)`.

## Uso permitido

Esta capacidad puede responder, con sentinel PymIA, a pedidos como:

```text
analiza el excel
analizalo
revisalo
```

Salida esperada:

```text
[PymIA:TELEGRAM_RUNTIME] Resumen estructural del Excel:
Archivo: ...xlsx
Hojas: N
- Hoja 'ventas': rows=..., cols=..., empty=no
  Columns preview: ...
```

## Alcance permitido

Puede informar:

```text
- nombre del archivo
- cantidad de hojas
- nombre de hojas
- filas y columnas por hoja
- si una hoja parece vacia
- preview de columnas
```

## Prohibido

Esta capacidad no debe afirmar:

```text
- rentabilidad
- margen real
- perdida o ganancia
- diagnostico financiero
- recomendaciones de negocio
- causas operativas
- conclusiones clinico-operacionales
```

Tampoco debe importar ni usar Hermes.

## Ruta correcta para diagnostico real

El diagnostico real debe conectarse por la frontera ya documentada:

```text
pymia.smartpyme.microservice_dispatcher.dispatch_candidate(
    candidate,
    evidence_path=archivo_excel,
    output_dir=...
)
```

con:

```text
runtime_classification = excel_diagnostic
status = READY_TO_EXECUTE
```

El dispatcher es la frontera futura para ejecutar `excel_diagnostic`.

## Regla de producto

El preview estructural ayuda a confirmar que PymIA recibio y puede leer la evidencia.

El diagnostico exige contrato de ejecucion y debe pasar por el microservicio real.

## Criterio de continuidad

Hasta que se conecte `microservice_dispatcher`, todo output de `telegram_excel_summary` debe tratarse como:

```text
STRUCTURAL_PREVIEW_ONLY
```

No como diagnostico.
