# Abandono del Lenguaje MVP en PymIA

## Doctrina
PymIA no persigue MVP; persigue robustez incremental. Una pieza puede ser pequeña, pero debe ser verificable, trazable y segura en su frontera.

## Clasificacion de referencias

### Historico / provenance (no modificado)
- `docs/migrado_desde_smartpyme_MIGRATION_INDEX.md`
- `docs/migrado_desde_smartpyme_MIGRACION_FISICA_FASE3.md`
- `docs/migrado_desde_smartpyme_ARQUEOLOGIA_FASE3.md`
- `docs/vision/SMARTPYME_MVP_REALISTA_Y_FILOSOFIA_OPERACIONAL.md`
- `docs/arquitectura/domain-classification.md` (referencia de rama historica)

Accion: mantener como evidencia arqueologica; no reescribir narrativa de origen.

### Docs vivos (actualizados)
- `docs/README.md`
- `docs/producto/registro-ciclos-operativos.md`
- `docs/producto/protocolo-anamnesis-mvp.md`
- `docs/hermes/pipeline-funcional-pymia-nodos-existentes.md`
- `docs/hermes/kernel-minimo-viable-y-corpus-minimo.md`
- `docs/hermes/inventario-smartpyme-nodos-colgados-para-pymia.md`
- `docs/hermes/contrato-minimo-integracion-externa.md`
- `docs/hermes/autoaditoria-hermes-pipeline-minimo-accionable.md`
- `docs/BEM_INGESTA_DOCUMENTAL_Y_ENTRADA_KERNEL_PYMIA.md`
- `docs/arquitectura/palantir-principles.md`

Reemplazos aplicados:
- `MVP` -> `núcleo robusto inicial`
- `mínimo viable` -> `mínimo confiable`
- `MVP conversacional` -> `interfaz experimental`
- `MVP técnico` -> `prueba de frontera`
- `MVP funcional` -> `ciclo robusto verificable`

### Campos tecnicos / schema (migracion compatible)
- `docs/formula_catalog.v1.json`
- `docs/formula_catalog.schema.v1.json`

Estrategia:
1. Mantener `priority_mvp` para compatibilidad con consumidores existentes.
2. Introducir `priority_robustez` como campo equivalente recomendado.
3. Mantener `priority_mvp` como legado documentado, no eliminarlo en v1.
4. Migrar consumidores a `priority_robustez` y deprecar `priority_mvp` en v2 del catalogo.
