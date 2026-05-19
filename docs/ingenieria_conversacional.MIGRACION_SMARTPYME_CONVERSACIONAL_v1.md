# Migración SmartPyme → PymIA — ingeniería conversacional y epistemológica

## Objetivo

Centralizar en PymIA todos los activos conversacionales, epistemológicos, taxonómicos y clínico-operacionales existentes en SmartPyme.

## Estado

Migración conceptual iniciada.

## Ejes detectados en SmartPyme

### Catálogos

Detectado:

```text
.agent/memory/catalog_patologias.json
app/catalog/pathologies.py
```

## Runtime de patologías

Detectado:

```text
app/services/pathology_engine_service.py
app/services/pathology_evaluators.py
app/contracts/pathology_contract.py
```

## Taxonomía operacional

Detectado:

```text
app/services/operational_taxonomy_service.py
app/services/operational_taxonomy_matcher_service.py
```

Conceptos encontrados:

```text
senales_anamnesis
patologias_probables
```

## Catálogos externos JSON

Detectado:

```text
app/services/normalization_service.py
app/catalogs/column_mapping_catalog.json
```

Confirma arquitectura enchufable.

## Skills

Detectado:

```text
SKILLS_CATALOGO_SMARTPYME.md
```

## Objetivo de reorganización

Separar:

```text
memoria histórica
normativa viva
runtime
experimentos
prompts
conocimiento enchufable
```

## Nueva estructura objetivo en PymIA

```text
docs/
  ingenieria_conversacional/
  epistemologia/
  taxonomias/
  patologias/
  runtime/
  prompts/
  memoria_historica/
  investigaciones/
  dramatizaciones/
  roleplays/
```

## Regla

Nada crítico debe quedar perdido dentro de SmartPyme.

Todo conocimiento reusable debe:

```text
migrarse
clasificarse
normalizarse
versionarse
```

## Próxima fase

1. Extraer catálogos reales.
2. Extraer taxonomías.
3. Extraer prompts conversacionales.
4. Extraer dramatizaciones y roleplays.
5. Separar normativa viva de memoria histórica.
6. Declarar documentos canónicos.
7. Declarar qué gobierna runtime.
