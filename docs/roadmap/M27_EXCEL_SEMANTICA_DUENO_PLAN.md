# M27 — Excel + semantica del dueno

## Estado

PLAN_DRAFT

## Objetivo

Demostrar con un slice minimo que PymIA puede unir:

- mensaje del dueno;
- Excel controlado;
- caso operativo estructurado;
- clasificacion inicial;
- evidence gate;
- estado del caso.

Este hito no declara producto. Solo prueba el puente entre semantica del dueno y evidencia Excel tratable por capacidades existentes.

## Fixture sugerido

Usar si aplica:

`tests/fixtures/smartpyme/ventas_costos_margen.xlsx`

Mensaje fixture: dueno declara duda sobre margen o ganancia.

## Alcance permitido

- test de aceptacion M27;
- reutilizar recepcion/intake existente;
- reutilizar clasificacion/interrogation existente;
- reutilizar evidence gate existente;
- asociar mensaje del dueno con Excel controlado;
- producir estado estructurado del caso.

## Fuera de alcance

- nuevo microservicio;
- registry;
- dispatcher;
- plugins;
- Telegram;
- PDF;
- HTML;
- UI;
- CI;
- ERP/Odoo/Dolibarr;
- LLM externo;
- declaracion de producto.

## Test esperado

Archivo sugerido:

`tests/smartpyme/test_m27_excel_semantica_dueno.py`

Debe validar:

1. mensaje del dueno + Excel controlado;
2. caso estructurado;
3. clasificacion inicial hacia margen/costos o equivalente;
4. evidence gate con evidencia suficiente o faltante explicita;
5. salida sin prometer diagnostico integral;
6. trazabilidad minima hacia mensaje y archivo.

## Criterio PASS

M27 aprueba si existe test reproducible para:

`owner_message + excel_fixture -> structured_case -> classification -> evidence_gate_result -> case_status`

## Criterio BLOCKED

Bloquear si requiere tocar dispatcher, registry, nueva capacidad, ERP, UI o promesa de producto.

## Proximo paso

Si M27 pasa, abrir M28: hallazgo tecnico -> narrativa grounded -> markdown legible.
