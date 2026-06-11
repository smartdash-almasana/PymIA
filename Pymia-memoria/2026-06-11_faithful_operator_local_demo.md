# Memoria PymIA — Faithful Operator local demo

Fecha: 2026-06-11

## Estado alcanzado

Se cerró un bloque operativo completo del `Faithful Operator` de PymIA, sin convertirlo en producto ni canal.

Flujo funcional alcanzado:

```text
mensaje del dueño
→ pedido de evidencia mínima
→ Excel real
→ spine batch importable
→ candidato trazable
→ confirmación/corrección/bloqueo del dueño
→ próximos pasos operativos
→ demo local asistida
```

## Archivos principales

- `pymia/faithful_operator.py`
- `pymia/cli/vertical_slice.py`
- `tests/test_faithful_operator.py`
- `tests/test_faithful_operator_confirmation.py`
- `scripts/demo_faithful_operator_local.py`
- `docs/pymia/PYMIA_FAITHFUL_OPERATOR_V1_PLAN.md`
- `docs/pymia/PYMIA_FAITHFUL_OPERATOR_LOCAL_DEMO_CHECKPOINT.md`

## Capacidades implementadas

- `handle_owner_message(...)`
  - recibe frase inicial del dueño;
  - no diagnostica;
  - pide evidencia mínima;
  - crea o conserva `intake_id`;
  - bloquea mensaje vacío.

- `receive_excel_and_build_candidate(...)`
  - recibe Excel real;
  - ejecuta el spine batch existente como función importable;
  - devuelve `evidence_id`, `evidence_hash`, `run_id`, `output_hash`;
  - queda en `OWNER_CONFIRMATION_PENDING`.

- `handle_owner_confirmation(...)`
  - confirma candidato;
  - procesa corrección;
  - bloquea incertidumbre del dueño;
  - preserva trazabilidad;
  - no declara diagnóstico final automático.

- `build_confirmed_candidate_next_actions(...)`
  - genera salida operativa posterior a confirmación;
  - incluye caso, evidencia, `run_id`, `output_hash`, límite explícito;
  - entrega exactamente 3 próximos pasos y 1 pregunta de seguimiento.

- `run_local_operator_flow(...)`
  - compacta el flujo local completo;
  - no introduce canal, framework, DB, LLM ni runtime.

- `scripts/demo_faithful_operator_local.py`
  - demo local mínima para operador asistido;
  - usa Excel real de `prueba_excels/Cafetería ABC.xlsx` si está disponible;
  - imprime entrada, evidencia, recorrido, trazabilidad y salida humana.

## Validaciones reportadas

### Demo local

```text
python scripts/demo_faithful_operator_local.py
VEREDICTO: PASS
```

### Tests focales

```text
python -m pytest tests/test_faithful_operator.py tests/test_faithful_operator_confirmation.py -q
19 passed in 2.96s
```

Salida observada de trazabilidad:

```text
tenant_id: demo_cafeteria_abc
intake_id: intake_93546f538f5da1a7
evidence_id: evidence_71243f593d54419daf55ee350d70d2fe
run_id: run_30feebad8f97461c90607991e8c856cf
output_hash: 81578193a973908d47346f05a554048617c40999b14820ef509dff347b530efd
```

## Límites preservados

No se introdujo:

- LangGraph;
- LLM real;
- canal externo;
- DB;
- Telegram;
- Hermes;
- runtime;
- PDF;
- marketplace;
- producto.

## Decisión operativa

Este bloque deja a PymIA con una demo local asistida real:

```text
frase caótica del dueño + Excel real → salida trazable para operador asistido
```

Próximo avance natural: usar esta salida como base para operación asistida real o para una interfaz mínima controlada, sin abrir producto ni canal todavía.
