# PYMIA ASSISTED CASE — Next Action Board

Estado: `OPERATIVO_LOCAL`

Este tablero evita que un caso asistido quede como documento muerto. Cada output debe dejar explícito el siguiente paso operativo.

## Regla central

Cada artefacto debe terminar con:

```text
NEXT_ACTION:
owner_question: [pregunta concreta]
required_evidence: [evidencia concreta o NONE]
operator_decision: [qué debe decidir el operador]
stop_condition: [cuándo bloquear honestamente]
```

Si un documento no deja `NEXT_ACTION`, se considera incompleto para operación asistida.

## Caso activo — Cafetería ABC

### Estado actual

```text
case_id: cafeteria_abc_assisted_001
state: SESSION_RECORD_READY
owner_message: Vendo más pero no me queda plata.
evidence: prueba_excels/Cafetería ABC.xlsx
```

### Último output generado

```text
Cafetería ABC queda lista para reproceso focalizado o conversación operativa posterior sin perder trazabilidad.
```

### NEXT_ACTION

```text
owner_question: ¿Querés revisar primero margen por producto, caja por período o costos directos?
required_evidence: NONE hasta que el dueño elija foco.
operator_decision: esperar elección de foco y clasificarla como MARGEN_PRODUCTO, CAJA_PERIODO o COSTOS_DIRECTOS.
stop_condition: si el dueño no puede elegir foco, sugerir empezar por mayor volumen de ventas; si tampoco puede validar datos, bloquear por incertidumbre semántica.
```

### Si el dueño elige MARGEN_PRODUCTO

```text
owner_question: ¿Tenés lista de precios, costo unitario y descuentos/promociones por producto?
required_evidence: lista de precios + costo unitario + descuentos/promociones + merma si existe.
operator_decision: preparar reproceso focalizado sobre margen por producto.
stop_condition: si no hay costo unitario confiable, bloquear margen y pedir fuente de costos.
```

### Si el dueño elige CAJA_PERIODO

```text
owner_question: ¿Tenés movimientos de caja/banco, pagos a proveedores, sueldos, alquiler y retiros del mismo período?
required_evidence: caja/banco + proveedores + sueldos + alquiler + retiros + deudas/pagos pendientes.
operator_decision: preparar reproceso focalizado sobre caja por período.
stop_condition: si ventas son facturadas pero no cobradas, bloquear lectura de caja hasta separar cobrado vs facturado.
```

### Si el dueño elige COSTOS_DIRECTOS

```text
owner_question: ¿Tenés facturas de proveedores, recetas/fichas técnicas, cantidades compradas y stock inicial/final?
required_evidence: facturas + ficha técnica + cantidades + stock inicial/final.
operator_decision: preparar reproceso focalizado sobre costos directos.
stop_condition: si los costos mezclan estructura y producto, pedir separación antes de reprocesar.
```

## Cola de próximos casos

### Caso 2 — Distribuidora

Estado: `PENDIENTE_DE_APERTURA`

```text
NEXT_ACTION:
owner_question: pegar relato inicial del dueño de distribuidora.
required_evidence: Excel real o fixture validado de distribuidora.
operator_decision: abrir caso desde PYMIA_ASSISTED_CASE_TEMPLATE.md.
stop_condition: no abrir si no hay relato + evidencia base.
```

### Caso 3 — Fábrica

Estado: `PENDIENTE_DE_APERTURA`

```text
NEXT_ACTION:
owner_question: pegar relato inicial del dueño de fábrica.
required_evidence: Excel real o fixture validado de fábrica.
operator_decision: abrir caso desde PYMIA_ASSISTED_CASE_TEMPLATE.md.
stop_condition: no abrir si no hay relato + evidencia base.
```

## Regla de avance

Avanzar sólo si el output anterior dejó una acción ejecutable. No crear arquitectura nueva para reemplazar una pregunta pendiente al dueño.

## Prohibiciones

No usar este tablero para:

- inventar evidencia;
- saltar confirmación del dueño;
- declarar diagnóstico final;
- crear canal/producto/runtime;
- abrir LLM libre;
- mezclar casos sin `case_id`.
