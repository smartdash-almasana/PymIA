# PYMIA FAITHFUL OPERATOR — assisted packet example

Estado: `EXAMPLE`

Este documento conserva un ejemplo versionable del paquete local para operador asistido generado por `scripts/demo_faithful_operator_local.py --write-report`.

No es producto, no es canal, no es runtime y no declara diagnóstico final automático.

## Uso previsto

Este ejemplo sirve para verificar el formato humano esperado de una salida asistida:

- entrada del dueño;
- evidencia usada;
- recorrido de estados;
- trazabilidad;
- salida para operador asistido;
- control operativo;
- límite explícito.

## Demo ejecutada

```text
PYMIA FAITHFUL OPERATOR — DEMO LOCAL ASISTIDA

Alcance: demo local, sin canal, sin producto, sin diagnóstico final automático.

ENTRADA DEL DUEÑO
Vendo más pero no me queda plata.

EVIDENCIA
prueba_excels/Cafetería ABC.xlsx

RECORRIDO
1. EVIDENCE_REQUESTED
2. OWNER_CONFIRMATION_PENDING
3. CLOSED

TRAZABILIDAD
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_fb309447997d4ef684c23bd417f645bf
run_id: run_c1c805258c8f4262bc309376f81cd662
output_hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba

SALIDA PARA OPERADOR ASISTIDO
Resultado de trabajo posterior a confirmación
Caso: Vendo más pero no me queda plata.
Evidencia usada: evidence_fb309447997d4ef684c23bd417f645bf
Run ID: run_c1c805258c8f4262bc309376f81cd662
Output hash: bea6fc31cb1fbf33cb2be7ea3771ba9c39dbedf8f346c73011786e7762f012ba
Límite: Resultado candidato: no declara verdad final sin confirmación del dueño.
Próximos pasos operativos:
1. Revisar con el dueño si las ventas y costos cargados cubren el período completo.
2. Separar productos o líneas con margen dudoso para lectura focalizada.
3. Pedir al dueño una decisión operativa concreta sobre qué variable quiere ajustar primero.
Pregunta de seguimiento: ¿Querés que revisemos primero margen por producto, caja por período o costos directos?
```

## Control operativo

- Verificar con el dueño que la evidencia corresponde al período correcto.
- Confirmar que las columnas usadas representan ventas, costos y productos reales.
- Registrar cualquier corrección antes de sostener una recomendación operativa.

## Límite

Este paquete no declara causa definitiva ni automatiza decisiones. Sirve para operación asistida trazable.

## Nota de versionado

La salida runtime original queda en `.tmp/faithful_operator_demo_report.md` y no debe versionarse. Este documento es la copia estable y sanitizada para documentación.
