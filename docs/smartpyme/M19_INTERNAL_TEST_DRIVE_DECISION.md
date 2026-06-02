# M19 — Decisión: Test Drive interno para radiografía del pipeline

Fecha: 2026-06-01  
Estado: decisión operativa  
Alcance: estrategia de testing real para el pipeline determinístico central SmartPyme.

---

## 1. Decisión

Para la primera versión de radiografía operacional del pipeline, **no se incorporará software externo**.

La solución será un **Test Drive interno dentro del repo PymIA**.

---

## 2. Motivo

El objetivo inmediato no es tener una plataforma visual ni un sistema externo de QA.

El objetivo inmediato es responder con evidencia computacional:

```text
¿El pipeline determinístico central funciona end-to-end?
¿Dónde bloquea?
¿Qué fase falló?
¿Qué output produjo cada etapa?
¿El resultado coincide con el contrato?
```

Eso puede lograrse con herramientas ya presentes:

```text
Python
pytest
fixtures
scripts internos
Makefile opcional
GitHub para trazabilidad
```

---

## 3. Qué se construirá

Un módulo interno:

```text
pymia/pipeline_radiography/
```

Con responsabilidad de:

```text
definir escenarios,
registrar trazas,
ejecutar el pipeline formal,
chequear contratos,
comparar contra registry,
y generar reporte para desarrollador.
```

Primera estructura prevista:

```text
pymia/pipeline_radiography/
  scenario.py
  trace.py
  runner.py
  contract_checker.py
  registry_checker.py
  report.py
```

Tests previstos:

```text
tests/smartpyme/e2e/test_pipeline_radiography_excel.py
```

Fixtures previstos:

```text
tests/fixtures/smartpyme/ventas_costos_margen.xlsx
```

---

## 4. Qué NO se incorporará ahora

No se agregará por ahora:

```text
plataforma externa de test drive
dashboard web
servicio SaaS de QA
sistema visual de monitoreo
herramienta externa de observabilidad
framework externo de orquestación
```

Tampoco se mezclará con:

```text
Telegram
PDF
HTML
Docling
UI
IA residente runtime
arnés runtime completo
memoria avanzada
```

---

## 5. Lugar correcto de ejecución

### Desarrollo principal

```text
repo local
```

Motivo:

```text
editar → correr pytest → ver fallo → ajustar → volver a correr
```

es más eficiente en local.

### Validación secundaria

```text
VM o entorno limpio
```

Uso:

```text
pull limpio
ejecutar make smartpyme-radiography o pytest focal
confirmar que no dependía del entorno local
```

### Trazabilidad

```text
GitHub
```

Uso:

```text
docs
commits
PR/issues si corresponde
CI futura
```

---

## 6. Automatización esperada

La meta operativa es llegar a un comando único:

```bash
make smartpyme-radiography
```

O, alternativamente:

```bash
python -m pymia.pipeline_radiography.run_scenarios
```

Ese comando debe producir:

```text
PASS
BLOCKED_EXPECTED
FAIL
AMBIGUOUS
```

Y dejar artefactos como:

```text
.tmp/pipeline_radiography/trace.json
.tmp/pipeline_radiography/report.md
```

---

## 7. Primer paso técnico

El primer paso no es runner completo.

El primer paso es:

```text
M19.1 — Scenario + Trace models
```

Archivos previstos:

```text
pymia/pipeline_radiography/scenario.py
pymia/pipeline_radiography/trace.py
tests/smartpyme/test_pipeline_radiography_models.py
```

Criterio:

```text
modelos importables,
serializables,
con estados explícitos,
y tests básicos de contrato.
```

---

## 8. Relación con pytest

pytest sigue siendo el motor de ejecución de tests.

El Test Drive interno no reemplaza pytest.

Lo organiza alrededor de escenarios operativos.

```text
pytest prueba funciones y contratos.
Pipeline Radiography prueba escenarios completos y produce trazas.
```

---

## 9. Relación con IA residente

La IA residente no debe interpretar intuiciones.

Debe interpretar hechos.

Pipeline Radiography será una fuente de hechos para la futura IA residente:

```text
pipeline determinístico
→ radiografía operacional
→ reporte estructurado
→ IA residente interpreta estado, bloqueo y próximo paso
```

---

## 10. Veredicto

No hace falta otro software para la primera versión.

La primera radiografía operacional de PymIA debe nacer dentro del repo, usando Python, pytest, fixtures y trazas propias.

---

## 11. Frase rectora

```text
Primero Test Drive interno.
Después, si hace falta, plataforma externa.
```
