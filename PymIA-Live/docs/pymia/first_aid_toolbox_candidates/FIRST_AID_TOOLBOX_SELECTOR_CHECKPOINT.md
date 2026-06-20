# First Aid Toolbox Selector Checkpoint

## Estado

CODE_SLICE_CLOSED

## Alcance

Segundo slice técnico de Primeros Auxilios PyME / Fase 1.

Se creó un selector puro que consume el veredicto de `first_aid_entrypoint` y el contrato declarativo `first_aid_toolbox_v1` para seleccionar componentes y composiciones candidatas.

No ejecuta herramientas.
No calcula fórmulas.
No diagnostica.
No lee archivos del dueño.
No persiste datos.
No toca OCF.
No toca replay.
No llama vertical pipeline.
No toca storage.

## Archivos creados

```text
PymIA-Live/pymia/smartpyme/first_aid_toolbox_selector.py
PymIA-Live/tests/smartpyme/test_first_aid_toolbox_selector.py
```

## Entrada

```text
FirstAidEntrypointVerdict
```

Fuente:

```text
PymIA-Live/pymia/smartpyme/first_aid_entrypoint.py
```

## Salida

```text
FirstAidToolboxSelection
```

Estados posibles:

```text
TOOLBOX_SELECTION_READY
TOOLBOX_SELECTION_NEEDS_EVIDENCE
TOOLBOX_SELECTION_NOT_ALLOWED
```

## Reglas implementadas

### FIRST_AID_READY

Devuelve:

```text
22 componentes Fase 1
5 composiciones candidatas
allowed_to_present_toolbox: true
next_allowed_action: present_first_aid_toolbox_candidates
```

### FIRST_AID_NEEDS_EVIDENCE

Devuelve:

```text
0 componentes
0 composiciones
allowed_to_present_toolbox: false
next_allowed_action: request_minimal_evidence
```

### NOT_FIRST_AID

Devuelve:

```text
0 componentes
0 composiciones
allowed_to_present_toolbox: false
next_allowed_action: heredado del entrypoint
```

## Exclusiones preservadas

Fase 2 queda excluida:

```text
auto_stock
compras_y_proveedores
control_de_gastos
punto_equilibrio
stock_control
```

SmartExcel queda fuera del selector:

```text
top_deudores_payload
structured_warnings_payload
exclude_ambiguous_amounts_rule
```

## Tests ejecutados

Comando reportado:

```text
python -m pytest tests/smartpyme/test_first_aid_toolbox_selector.py -q
```

Resultado:

```text
TESTS_RUN: 9
RESULT: 9/9 PASSED
FAILURES: NONE
```

## Validaciones cubiertas

```text
ready → 22 componentes + 5 composiciones
Fase 2 excluida
SmartExcel excluido
needs evidence bloquea selección
not first aid bloquea selección
composiciones enriquecidas con componentes
shape inválido rechazado
sin runtime/pipeline/storage/core
dependencias limitadas a entrypoint + contract
```

## Límites preservados

```text
runtime_touched: NO
kernel_touched: NO
pipeline_touched: NO
storage_touched: NO
diagnostic_core_touched: NO
implementation_authorized: NO
```

## Decisión

El selector queda cerrado como slice técnico puro.

No autoriza ejecución de herramientas.
No autoriza integración a pipeline.
No autoriza runtime.

## Próximo paso seguro

```text
Commit del segundo slice técnico.
```

## Estado final

```text
FIRST_AID_TOOLBOX_SELECTOR_CHECKPOINT = CREATED
status: CODE_SLICE_CLOSED
tests: 9/9 PASSED
verdict: PASS
```
