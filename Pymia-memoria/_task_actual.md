# PymIA Memoria — Task actual

Fecha: 2026-06-16

## Task actual

```text
OWNER_SIMPLE_BUILDER_EXTRACTION_V1
```

## Estado

```text
APPLIED_NOT_COMMITTED
```

## Objetivo

```text
Reducir responsabilidad de vertical_slice.py moviendo la construcción de owner_simple a un builder externo en smartpyme, sin cambiar contrato, output, JSON ni comportamiento esperado.
```

## Último HEAD validado por MCP

```text
e736a3b feat(pymia-live): add owner simple presentation layer
```

## Tarea documental previa incorporada

```text
RECOVERY_CHECKPOINT_AFTER_OWNER_SIMPLE_DERIVA_V1
OWNER_SIMPLE_PRESENTATION_V1.md
```

## Veredicto operativo

```text
FREEZE_AND_DOCUMENT + MINIMAL_EXTRACTION
```

## Cambios aplicados

```text
- Creado PymIA-Live/docs/pymia/OWNER_SIMPLE_PRESENTATION_V1.md.
- Creado PymIA-Live/pymia/smartpyme/owner_output.py.
- Movida la lógica owner_simple fuera de vertical_slice.py:
  - _owner_understanding_text()
  - _owner_readable_summary()
  - build_owner_simple_view()
- vertical_slice.py ahora consume build_owner_simple_view() como builder externo.
- Creado tests/smartpyme/test_owner_output_boundary.py para impedir dependencia inversa hacia vertical_slice.py o argparse.
- Actualizada memoria para registrar la extracción mínima.
```

## Runtime / Contratos / Tests

```text
Runtime modificado de forma limitada.
Contratos JSON no modificados.
vertical_slice_copy_v1 se mantiene como contrato declarativo temporal.
No se creó owner_output_v1.
No se creó dataclass.
No se cambió el shape de owner_simple.
```

## Tests de validación

```text
Intento 1: run_pytest sobre smartbridge/PymIA/PymIA-Live falló porque PymIA-Live no es repo git independiente.
Intento 2: run_pytest sobre smartbridge/PymIA quedó en timeout.
Resultado: VALIDACIÓN AUTOMATIZADA NO CONCLUIDA por limitación/timeout de herramienta.
Requiere ejecución local canónica:
cd E:\BuenosPasos\smartbridge\PymIA\PymIA-Live
python -m pytest -q
```

## Commit

```text
No realizado.
Requiere autorización explícita del usuario.
```

## Worktree esperado posterior

```text
M PymIA-Live/pymia/cli/vertical_slice.py
M Pymia-memoria/_decisiones_vigentes.md
M Pymia-memoria/_estado_actual.md
M Pymia-memoria/_task_actual.md
?? PymIA-Live/docs/pymia/OWNER_SIMPLE_PRESENTATION_V1.md
?? PymIA-Live/pymia/smartpyme/owner_output.py
?? PymIA-Live/tests/smartpyme/test_owner_output_boundary.py
```

## Próximo foco recomendado

```text
VALIDAR_OWNER_SIMPLE_BUILDER_EXTRACTION_V1
```

## Objetivo del próximo foco

```text
Ejecutar pytest canónico local en PymIA-Live y auditar diff antes de commit.
```

## Prohibiciones vigentes

```text
- No crear owner_output_v1 todavía.
- No crear JSON nuevo.
- No crear dataclass todavía.
- No cambiar copy.
- No cambiar output.
- No abrir multicanal.
- No abrir producto/piloto antes de validar extracción.
```
