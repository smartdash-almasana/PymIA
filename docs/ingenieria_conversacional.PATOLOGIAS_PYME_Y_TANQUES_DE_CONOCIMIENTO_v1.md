# Patologías PyME y tanques de conocimiento — v1

## Estado

Documento rector inicial para la arquitectura modular de patologías, fórmulas y conocimiento intercambiable de PymIA.

## Principio rector

Las patologías PyME no son una lista rígida.

Son componentes conectables a:

- fórmulas matemáticas;
- taxonomías de industrias;
- skills;
- evidencia requerida;
- motores conversacionales;
- modelos de decisión;
- benchmarks;
- conocimiento sectorial.

## Arquitectura modular

La arquitectura debe permitir:

```text
enchufar
reemplazar
versionar
extender
fusionar
especializar
```

catálogos completos sin romper el runtime.

## Tanques de conocimiento

Un tanque de conocimiento es un módulo autocontenido de:

- patologías;
- fórmulas;
- reglas;
- taxonomías;
- evidencia;
- prompts;
- thresholds;
- benchmarks;
- interpretación.

Ejemplos:

```text
knowledge_tank_retail
knowledge_tank_textil
knowledge_tank_marketplaces
knowledge_tank_construccion
knowledge_tank_estudios_contables
knowledge_tank_logistica
knowledge_tank_agro
```

## Regla de intercambiabilidad

Todo catálogo debe poder:

```text
cargarse
removerse
versionarse
actualizarse
fusionarse
priorizarse
```

sin modificar código core.

## Separación obligatoria

### Catálogo de patologías

Define:

```text
qué puede estar pasando
```

### Catálogo de fórmulas

Define:

```text
cómo se calcula
```

### Catálogo de taxonomías

Define:

```text
para qué industria o vertical aplica
```

### Capa matematizadora

Define:

```text
qué fórmula usar
qué variables faltan
qué evidencia pedir
qué cálculo es válido
```

### Runtime conversacional

Define:

```text
cómo preguntar
cómo avanzar
cómo bloquear
cómo explicar
```

## Formato mutable

Los JSON deben ser:

```text
modulares
versionables
componibles
hot-swappable
```

Nunca rígidos ni hardcodeados.

## Relación entre catálogos

```text
patología
→ referencia fórmulas
→ referencia taxonomías
→ referencia evidencia
→ referencia skills
→ referencia preguntas
→ referencia thresholds
```

## Estructura esperada

```text
catalogs/
  pathology_catalog/
  formula_catalog/
  taxonomy_catalog/
  thresholds/
  benchmarks/
  prompts/
  industry_modules/
```

## Regla crítica

El runtime no debe asumir conocimiento fijo.

Debe cargar conocimiento desde:

```text
JSON
schemas
knowledge packs
industry modules
```

## Pathology JSON

El catálogo de patologías debe poder evolucionar sin romper compatibilidad.

Formato esperado:

```json
{
  "pathology_code": "REN_001",
  "name": "Margen Invisible",
  "formula_refs": [
    "margen_neto_real"
  ],
  "taxonomy_refs": [
    "retail",
    "marketplaces"
  ],
  "required_evidence": [
    "ventas",
    "costos",
    "comisiones"
  ],
  "version": "1.0"
}
```

## Formula JSON

```json
{
  "formula_id": "margen_neto_real",
  "expression": "((PV - Costos - Impuestos) / PV) * 100",
  "variables": [
    "PV",
    "Costos",
    "Impuestos"
  ],
  "industry_overrides": {
    "marketplaces": {
      "extra_costs": [
        "comision_ml",
        "envio"
      ]
    }
  }
}
```

## Regla de evolución

Nuevas industrias o verticales no deben requerir:

```text
reescribir runtime
reescribir prompts
reescribir matemáticas base
```

Solo conectar nuevos módulos.

## Implicancia arquitectónica

PymIA debe evolucionar hacia:

```text
kernel
+
knowledge packs
+
motor conversacional
+
capa matematizadora
+
motor epistemológico
```

No hacia lógica rígida embebida en prompts.
