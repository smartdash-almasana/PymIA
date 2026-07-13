# Biblioteca documental PymIA

## Autoridad

La autoridad documental vigente está en:

```text
docs/current/README.md
```

Ningún otro índice, auditoría, closeout, roadmap histórico, documento de producto, landing, protocolo Hermes o corpus migrado puede gobernar implementación salvo referencia explícita desde esa autoridad.

## Regla de uso

```text
Código + tests + evidencia observada
→ docs/current
→ contratos/ADR citados explícitamente
```

`docs/DOCUMENTATION_INDEX.md`, `docs/DEPRECATED_DOCS.md` y otros inventarios anteriores conservan valor histórico hasta su eliminación, pero no son autoridad soberana.

## Política de saneamiento

- La documentación obsoleta se elimina del árbol activo.
- No se mueve a museo, archive, legacy o cuarentena documental.
- Git conserva la trazabilidad histórica.
- No se crea un documento nuevo cuando corresponde corregir uno vigente.
- Una auditoría o plan ya ejecutado no permanece como orientación actual.
- Los documentos de evidencia pueden conservarse solo cuando prueban un hecho que sigue siendo relevante y su alcance está claramente limitado.

## Servicio 1

La orientación actual se reduce a:

```text
docs/current/SERVICE_1_STATUS.md
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_DETERMINISTIC_SEMANTIC_PIPELINE_ENGINEERING_METHOD_V1.md
docs/current/ARCHITECTURE_BOUNDARY.md
```

La raíz productiva real está en:

```text
PymIA-Live/pymia/smartpyme/service_1_product_pipeline_v1.py
PymIA-Live/pymia/cli/service_1_product.py
```

## Catálogos

Los catálogos JSON y contratos técnicos se consideran fuentes válidas únicamente cuando están cargados o referenciados por la raíz productiva y cubiertos por tests.
