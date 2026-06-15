# PymIA Memoria — Decisiones vigentes

Fecha: 2026-06-15

## Decisión rectora

```text
El conocimiento de dominio es enchufable.
El kernel permanece estable.
```

Consecuencia:

```text
JSON/contratos = fuente declarativa de conocimiento.
Python runtime = carga, valida, calcula, orquesta, renderiza, falla cerrado.
```

## Autoridad operativa vigente

```text
Repo git real: E:\BuenosPasos\smartbridge\PymIA
Subcarpeta viva: PymIA-Live
No tratar PymIA-Live como repo git independiente.
```

Orden de autoridad:

```text
1. PymIA-Live ejecutable y smoke/evidencia validada.
2. PymIA-Live/README.md.
3. Contratos JSON vivos bajo PymIA-Live/pymia/contracts/.
4. Código runtime vivo bajo PymIA-Live/pymia/.
5. Documentos vivos explícitamente promovidos.
6. Museo histórico catalogado, sólo como contexto.
```

## Estado de saneamiento genético

```text
CERRADO hasta FORMULA_ENGINE_DISPATCH_TABLE_V1
```

Commits relevantes:

```text
2d70470 Evidence binding -> formula_aliases_v1.json
90fe961 Evidence requirement matcher -> evidence_requirement_aliases_v1.json
85d5bd2 Pathology knowledge tank -> pathology_rules_v1.json
926d2ff Question alignment gate -> question_alignment_v1.json
2dd8a1c Formula engine wired to formula_rules_v1.json
10126c8 Runtime consumers migrated from SUPPORTED_FORMULAS
b29e06b FORMULA_CONTRACT_RETIREMENT_V1
b61cbbb FORMULA_ENGINE_RESULT_COVERAGE_V1
e4e1844 PRESENTATION_LABELS_V1 wiring
5da7f43 FORMULA_ENGINE_DISPATCH_TABLE_V1
bc4e1b5 QAG reconduction copy dedup
c958ff3 canonical test command documented
42d19bc local temp/quarantine artifacts ignored
```

## Decisiones técnicas vigentes

```text
formula_rules_v1.json gobierna reglas declarativas de fórmulas.
formula_engine_service.py usa registry formula_id -> calculator.
SUPPORTED_FORMULAS no debe volver.
FormulaDefinition no debe volver.
calculate_formula no debe volver.
presentation_labels_v1.json gobierna labels owner-facing.
question_alignment_v1.json gobierna QAG.
pathology_rules_v1.json gobierna reglas de patologías.
evidence_requirement_aliases_v1.json gobierna aliases de evidence requirements.
formula_aliases_v1.json gobierna aliases de evidencia hacia fórmulas.
```

## Decisiones de higiene vigentes

```text
.tmp/ no se versiona.
_local_quarantine/ no se versiona.
PymIA-Live/.tmp_smoke_owner_alignment/ no se versiona salvo decisión explícita de evidencia sanitizada.
Pymia-memoria/ está trackeado: .gitignore no impide cambios porque los archivos ya existen en índice.
MUSEUM_CATALOG.md no gobierna runtime; sólo puede catalogar frontera museo/vivo.
ROLE_PLAYING_ONBOARDING_FINDINGS.md es hallazgo experimental hasta promoción explícita.
```

## Próximo foco recomendado

```text
HARD_CODE_INVENTORY_OUTSIDE_FORMULAS_V1
```

Objetivo:

```text
Listar deuda viva real posterior al saneamiento genético.
No implementar código runtime.
No crear contratos nuevos.
No abrir features.
No tocar fórmulas, QAG, pathology, evidence, presentation ni storage.
```

Salida esperada:

```text
DEUDA BLOQUEANTE
DEUDA NO BLOQUEANTE
DEUDA MUSEO / HISTÓRICA
PRÓXIMO SLICE CANDIDATO
VEREDICTO
```

## Reglas de trabajo

```text
Si trae evidencia -> validar evidencia.
Si pide prompt -> dar prompt con encabezado: PROMPT — objetivo / PARA: agente.
Si pide decisión -> dar decisión.
Si pide siguiente paso -> dar un solo siguiente paso.
Si pide ejecutar -> pedir AUTH si modifica repo, tests, commit o push.
Lectura/auditoría puede hacerse sólo cuando el usuario la autoriza o el frente lo requiere explícitamente.
```

## Reglas de limpieza

```text
No agregar .tmp/
No agregar PymIA-Live/.tmp_smoke_owner_alignment/
No agregar _local_quarantine/
No commitear museo ni documentación no intencional.
No mezclar memoria, museo, smoke y runtime en un mismo commit.
```

## Frase rectora actual

```text
PymIA-Live debe quedar pequeño, trazable y gobernado por contratos declarativos.
```
