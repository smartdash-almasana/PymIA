# PYMIA FAITHFUL OPERATOR — LOCAL DEMO CHECKPOINT

Estado: `PASS`

Fecha de cierre operativo: 2026-06-11

## Alcance

Este checkpoint documenta la primera demo local mínima del `Faithful Operator` de PymIA.

La demo no es producto, no es canal, no es runtime y no introduce arquitectura nueva. Es una demostración local asistida que muestra el recorrido completo desde una frase inicial del dueño PyME hasta una salida humana trazable para operador asistido.

## Flujo validado

```text
Dueño habla
→ operador no diagnostica
→ pide evidencia mínima
→ recibe Excel real
→ ejecuta spine batch importable
→ produce candidato trazable
→ recibe confirmación del dueño
→ genera próximos pasos operativos
```

## Script de demo

```text
scripts/demo_faithful_operator_local.py
```

Ejecución validada desde la raíz del repositorio:

```bash
python scripts/demo_faithful_operator_local.py
```

## Evidencia usada

Excel real detectado y usado por la demo:

```text
prueba_excels/Cafetería ABC.xlsx
```

## Salida validada

La demo imprime una salida humana con las siguientes secciones:

```text
PYMIA FAITHFUL OPERATOR — DEMO LOCAL ASISTIDA
ENTRADA DEL DUEÑO
EVIDENCIA
RECORRIDO
TRAZABILIDAD
SALIDA PARA OPERADOR ASISTIDO
```

## Trazabilidad observada

La demo incluye explícitamente:

```text
tenant_id
intake_id
evidence_id
run_id
output_hash
```

Ejemplo validado:

```text
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_71243f593d54419daf55ee350d70d2fe
run_id: run_30feebad8f97461c90607991e8c856cf
output_hash: 81578193a973908d47346f05a554048617c40999b14820ef509dff347b530efd
```

## Salida para operador asistido

La demo genera una respuesta final de trabajo posterior a confirmación, con:

- resumen del caso;
- evidencia usada;
- `run_id`;
- `output_hash`;
- límite explícito;
- tres próximos pasos operativos;
- una pregunta de seguimiento al dueño.

## Límites preservados

La demo preserva los límites arquitectónicos vigentes:

- no declara diagnóstico final automático;
- no usa LangGraph;
- no usa LLM real;
- no introduce canal externo;
- no introduce DB;
- no toca Telegram;
- no toca Hermes;
- no introduce runtime;
- no transforma esto en producto.

## Validación reportada

Validación de demo:

```text
VEREDICTO: PASS
```

Validación de tests focales:

```text
python -m pytest tests/test_faithful_operator.py tests/test_faithful_operator_confirmation.py -q

19 passed in 2.96s
```

## Estado funcional alcanzado

PymIA cuenta ahora con un recorrido local demostrable:

```text
mensaje del dueño
→ evidencia real
→ spine trazable
→ confirmación
→ salida humana para operador asistido
```

Este checkpoint cierra la demo local mínima del `Faithful Operator` y deja preparado el próximo bloque: usar esta salida como base para operación asistida real, sin convertirla todavía en canal ni producto.
