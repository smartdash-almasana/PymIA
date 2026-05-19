# Decisión de ensamblaje Chip 1 — estructura destino PymIA

## Estado

Documento operativo de decisión previa a implementación.

Se analiza la estructura propuesta para migrar/recrear Chip 1 en PymIA.

Chip 1:

```text
FormulaInput
→ FormulaEngineService
→ FormulaResult
→ PathologyEngineService
→ PathologyFinding
→ Adapter
→ FindingRecord
→ DiagnosticReportService
→ DiagnosticReport
```

Decisión vigente:

```text
MIGRAR CON PODA + ADAPTADOR
```

---

## Estructura propuesta

```text
PymIA/
├── pymia/
│   ├── contracts/
│   │   ├── formula_contract.py
│   │   ├── pathology_contract.py
│   │   └── diagnostic_report_contract.py
│   ├── core/
│   │   └── exceptions.py
│   ├── entities/
│   │   └── findings.py
│   ├── services/
│   │   ├── formula_engine_service.py
│   │   ├── pathology_engine_service.py
│   │   ├── diagnostic_report_service.py
│   │   └── pathology_adapters.py
│   └── knowledge_tank/
│       ├── __init__.py
│       ├── pathology_catalog.py
│       └── pathology_evaluators.py
└── tests/
    ├── test_formula_engine_service.py
    ├── test_pathology_engine_service.py
    ├── test_diagnostic_report_service.py
    ├── test_pathology_adapter.py
    └── test_kernel_chip1_integration.py
```

---

## Contraste con estructura real de PymIA

Estructura real observada:

```text
pymia/contracts/
pymia/services/
pymia/pipeline/
pymia/interfaces/
pymia/hermes/
pymia/cli/
tests/
```

No existen actualmente:

```text
pymia/core/
pymia/entities/
pymia/knowledge_tank/
```

Esto no bloquea la propuesta, pero significa que esos namespaces son nuevos y deben justificarse.

---

## Veredicto sobre estructura

```text
APROBADA CON AJUSTES
```

La estructura respeta la decisión de no tocar Hermes, UI, jobs, factory ni orchestration.

También separa correctamente:

```text
contratos
servicios
adaptador
tanque de conocimiento
tests
```

---

## Ajustes requeridos antes de implementar

### 1. `pymia/core/exceptions.py`

No crear por defecto.

Motivo:

```text
En los archivos físicos revisados de SmartPyme para FormulaEngineService no aparece BusinessRuleException.
```

Decisión:

```text
Crear solo si el código migrado realmente lo requiere.
```

### 2. `pymia/entities/findings.py`

Aceptar solo si no duplica contratos.

Riesgo:

```text
PymIA ya usa pymia/contracts/ para estructuras de intercambio.
Crear entities/ puede fragmentar la semántica.
```

Decisión recomendada:

```text
Opción preferida: ubicar FindingRecord en diagnostic_report_contract.py.
Opción aceptable: entities/findings.py si se justifica como entidad compartida entre contratos.
```

### 3. `pymia/knowledge_tank/`

Aceptado conceptualmente.

Motivo:

```text
El kernel hard debe operar con tanques de conocimiento enchufables/desenchufables.
```

Condición:

```text
PathologyEngineService no debe importar un catálogo global rígido si luego se quiere cambiar el tanque.
```

Preferencia:

```text
PathologyEngineService debe recibir el tanque por constructor o por interfaz mínima.
```

### 4. tests

Aceptar estructura propuesta, pero preferir ubicación coherente con PymIA actual:

```text
tests/services/test_formula_engine_service.py
tests/services/test_pathology_engine_service.py
tests/services/test_diagnostic_report_service.py
tests/services/test_pathology_adapter.py
tests/services/test_kernel_chip1_integration.py
```

Motivo:

```text
PymIA ya tiene tests/services/.
```

---

## Estructura destino corregida recomendada

```text
PymIA/
├── pymia/
│   ├── contracts/
│   │   ├── formula_contract.py
│   │   ├── pathology_contract.py
│   │   └── diagnostic_report_contract.py
│   ├── services/
│   │   ├── formula_engine_service.py
│   │   ├── pathology_engine_service.py
│   │   ├── diagnostic_report_service.py
│   │   └── pathology_adapters.py
│   └── knowledge_tank/
│       ├── __init__.py
│       ├── pathology_catalog.py
│       └── pathology_evaluators.py
└── tests/
    └── services/
        ├── test_formula_engine_service.py
        ├── test_pathology_engine_service.py
        ├── test_diagnostic_report_service.py
        ├── test_pathology_adapter.py
        └── test_kernel_chip1_integration.py
```

Opcional:

```text
pymia/core/exceptions.py solo si aparece uso real.
pymia/entities/findings.py solo si se decide separar entidades de contratos.
```

---

## Regla de implementación

No copiar SmartPyme tal cual.

Implementar Chip 1 como circuito determinístico:

```text
formula
→ pathology
→ adapter
→ diagnostic_report
→ KernelState
```

Estados:

```text
BLOCKED
PARTIAL
PASS
```

No deben entrar:

```text
job_id
owner_question
proposed_next_actions
Hermes
factory
jobs
orchestration
authorization flow
```

---

## Decisión final

```text
La estructura propuesta sirve, pero se implementa con ajustes:
- sin core/exceptions.py salvo necesidad real;
- preferir FindingRecord dentro de diagnostic_report_contract.py;
- knowledge_tank aceptado como namespace nuevo;
- tests dentro de tests/services/;
- PathologyEngineService desacoplado del catálogo por interfaz o inyección.
```

---

## Implementación ejecutada

Chip 1 fue implementado en PymIA como circuito mínimo podado:

```text
FormulaInput
→ FormulaEngineService
→ FormulaResult
→ PathologyEngineService
→ PathologyFinding
→ pathology_finding_to_finding_record
→ DiagnosticReportService
→ DiagnosticReport
```

Archivos creados:

```text
pymia/contracts/formula_contract.py
pymia/contracts/pathology_contract.py
pymia/contracts/diagnostic_report_contract.py
pymia/services/formula_engine_service.py
pymia/services/pathology_knowledge_tank.py
pymia/services/pathology_engine_service.py
pymia/services/pathology_adapters.py
pymia/services/diagnostic_report_service.py
tests/services/test_formula_engine_service.py
tests/services/test_pathology_engine_service.py
tests/services/test_pathology_adapter.py
tests/services/test_diagnostic_report_service.py
tests/services/test_kernel_chip1_integration.py
```

Desviación técnica registrada:

```text
No se creó pymia/knowledge_tank/ porque el MCP disponible no crea directorios padre.
El tanque enchufable mínimo quedó temporalmente en pymia/services/pathology_knowledge_tank.py.
La propiedad enchufable se preserva por interfaz e inyección en PathologyEngineService.
```

Validación:

```text
python -m pytest -q
83 passed
```

Veredicto post-implementación:

```text
Chip 1 está implementado y probado en PymIA como bloque podado del kernel determinístico.
```

---

## Contraste de nueva lectura pegada

La nueva lectura refuerza la dirección general de Chip 1, pero no debe aceptarse automáticamente si propone cambios estructurales no validados contra PymIA real.

Puntos aceptados:

```text
- Chip 1 debe implementarse con poda.
- Debe existir adaptador entre PathologyFinding y FindingRecord.
- Deben existir tests unitarios y un test end-to-end.
- DiagnosticReportService no debe arrastrar owner/job/orchestration.
```

Puntos que requieren cautela:

```text
- No aceptar kernel_v1.py sin prueba previa.
- No reemplazar knowledge_tank por catalog si se pierde la idea de tanque enchufable/desenchufable.
- No mezclar dataclass/Pydantic sin una decisión explícita de contratos.
- No crear core/exceptions.py si no aparece una dependencia real.
```

Decisión mantenida:

```text
Árbol corregido aprobado con ajustes.
Implementar primero contratos separados + services + knowledge_tank + adapter + tests/services.
```
