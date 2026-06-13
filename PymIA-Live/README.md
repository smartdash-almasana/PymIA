# PymIA Live — Núcleo Clínico Operativo

## Propósito
`PymIA-Live` es el núcleo operativo y autoportante extraído del motor clínico PymIA. Su propósito es consolidar la cadena de ejecución viva actual, aislando las capacidades operativas validadas de toda la deuda técnica, canales obsoletos y borradores históricos (el "museo") acumulados en fases previas del proyecto.

---

## Alcance
Este repositorio contiene **únicamente** las piezas que ejecutan, validan, registran y auditan el flujo de análisis actual.

### Componentes Incluidos:
- **CLI Operativo:** [vertical_slice.py](file:///e:/BuenosPasos/smartbridge/PymIA/PymIA-Live/pymia/cli/vertical_slice.py) como punto de entrada único de ejecución local.
- **Contratos de Entrada y Salida:** Language Corpus V1 (`language_corpus_v1.py`), Evidence V1 (`evidence_v1.py`) y Pipeline Run V1 (`pipeline_run_v1.py`).
- **Core de Suficiencia y Reconciliación:** `evidence_sufficiency.py` y `evidence_requirement_matcher.py`.
- **Salida Dueño-Facing:** `owner_facing_report.py` para la traducción de variables en lenguaje dueño.
- **Herramientas de Ingesta:** `document_ingestion.py` y la suite de perfilado semántico `bem_schema_builder/`.
- **Evidencia y Runbooks:** Casos reales de prueba (.xlsx) y normativas operativas del piloto asistido.

---

## Cómo Ejecutar

### 1. Preparación del Entorno
Desde la raíz de la carpeta `PymIA-Live/`, cree un entorno virtual de Python (>= 3.11) e instale las dependencias en modo editable:
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

# Instalar dependencias del proyecto
pip install -e .
```

### 2. Ejecutar los Smoke Tests
El pipeline lee un archivo de planilla de PyME y un mensaje del dueño, produciendo un reporte en formato Markdown local en la carpeta `.tmp/`.

#### Smoke Textil (Caso: La Textil Cosida SRL)
```bash
python -m pymia.cli.vertical_slice \
  --excel prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx \
  --message "tengo una textil y no me cierra la caja" \
  --tenant-id tenant_smoke_textil \
  --intake-id intake_smoke_textil \
  --output .tmp/smoke_textil.md
```

#### Smoke Cafetería (Caso: Cafetería ABC)
```bash
python -m pymia.cli.vertical_slice \
  --excel prueba_excels/cafeteria_abc.xlsx \
  --message "vendo mas pero no me queda plata" \
  --tenant-id tenant_smoke_cafeteria \
  --intake-id intake_smoke_cafeteria \
  --output .tmp/smoke_cafeteria.md
```

---

## Limitaciones Actuales (Gaps Operativos)
1. **Mensaje del Dueño no vinculante:** El parámetro `--message` ingresa al reporte y al historial de ejecución para trazabilidad, pero la lógica del catálogo no lo utiliza para priorizar u ordenar la próxima pregunta.
2. **Mitigación por Operador Humano:** Ante discrepancias entre la primera pregunta del catálogo y el síntoma dominante del mensaje, se debe aplicar el protocolo de reconducción humana transitoria documentado en [RUNBOOK_PILOTO_ASISTIDO_POST_LC.md](file:///e:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/ops/RUNBOOK_PILOTO_ASISTIDO_POST_LC.md).
3. **Resultado Candidato:** La salida es un resumen estructurado útil para la entrevista, no un diagnóstico automático o automatizado.
