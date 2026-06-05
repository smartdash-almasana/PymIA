# M32 — SmartPyme Local Assisted MVP Checkpoint

## Estado

IMPLEMENTED_PENDING_LOCAL_VALIDATION

## Motivo

Después de M31-P, M31-C y M31-R, el proyecto necesitaba dejar de producir sólo documentación y crear una columna vertebral ejecutable mínima.

M32 introduce un flujo local directo:

```text
XLSX de PyME
→ curación local
→ evidencia estructurada
→ reporte narrativo
→ validación de grounding
→ reporte Markdown mínimo
→ resumen de corrida
```

## Código creado

```text
pymia/smartpyme/minimum_report.py
pymia/smartpyme/local_assisted_mvp.py
```

## Test creado

```text
tests/smartpyme/test_m32_local_assisted_mvp.py
```

## Comando de producto mínimo local

Ejemplo:

```powershell
python -m pymia.smartpyme.local_assisted_mvp --excel prueba_excels/simple_bem_test.xlsx --tenant-id m32-demo --out .out/m32-demo
```

También puede probarse con:

```powershell
python -m pymia.smartpyme.local_assisted_mvp --excel prueba_excels/la_textil_cosida_srl_mar_abr_may_2026.xlsx --tenant-id m32-textil --out .out/m32-textil
```

## Artefactos esperados

El comando debe generar:

```text
run_summary.json
report.md
evidence.json
curation.json
narrative_report.json
grounding.json
```

Además, por persistencia existente de curation artifacts, puede generar:

```text
<stem>.raw_tables.json
<stem>.normalized_tables.json
<stem>.sheet_reports.json
<stem>.structured_evidence.json
```

## Criterio PASS local

M32 puede declararse PASS_LOCAL si:

```powershell
python -m pytest tests/smartpyme/test_m32_local_assisted_mvp.py -q
```

pasa y si el comando local genera `report.md` y `run_summary.json` para al menos un Excel fixture.

## Qué certifica

Este checkpoint certifica implementación inicial de:

- comando local ejecutable;
- reporte Markdown mínimo;
- resumen de corrida;
- artefactos JSON auditables;
- test focal de flujo local;
- manejo de archivo faltante.

## Qué no certifica

No certifica:

- producto comercial;
- clientes reales;
- UI;
- PDF profesional;
- Telegram;
- ERP;
- autonomía end-to-end;
- Guided Evidence Recovery;
- M31-R operativo;
- que el usuario PyME entienda o valore el reporte.

## Regla de no-humo

M32 no debe cerrarse por documentación.

Debe cerrarse con ejecución local reportada:

```text
pytest focal PASS
+ comando local genera artefactos
+ report.md inspeccionable
```

## Próximo paso

Ejecutar localmente:

```powershell
python -m pytest tests/smartpyme/test_m32_local_assisted_mvp.py -q
python -m pymia.smartpyme.local_assisted_mvp --excel prueba_excels/simple_bem_test.xlsx --tenant-id m32-demo --out .out/m32-demo
```

Luego registrar salida real y actualizar este checkpoint a PASS_LOCAL si corresponde.
