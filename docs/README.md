# Biblioteca documental PymIA

## Autoridad

La autoridad documental vigente está en:

```text
docs/current/README.md
```

Ningún otro índice, auditoría, closeout, roadmap histórico, documento de producto, landing, protocolo Hermes o corpus migrado gobierna implementación salvo referencia explícita desde esa autoridad.

## Jerarquía

```text
código físico + tests observados
→ docs/current/README.md
→ documentos rectores enumerados allí
→ ADR/contratos citados
→ evidencia histórica acotada
```

## Política de saneamiento

```text
NO_MUSEUM_DIRECTORY
NO_ARCHIVE_DIRECTORY
GIT_PRESERVES_HISTORY
```

- La documentación obsoleta se elimina del árbol activo sólo con prueba de no dependencia.
- No se mueve a museo, archive, legacy o cuarentena documental.
- No se crea un documento nuevo cuando corresponde corregir uno rector existente.
- Una auditoría, TaskSpec, checkpoint o plan ya ejecutado no conserva autoridad de continuidad.
- Los documentos de evidencia sólo prueban el alcance exacto que observaron.
- La presencia física de un archivo en `docs/current/` no lo convierte en documento rector; gobierna únicamente el índice de `docs/current/README.md`.

## Servicio 1

La continuidad debe empezar en:

```text
docs/current/README.md
docs/current/SERVICE_1_CURRENT_PRODUCT_STATE_V1.md
docs/current/SERVICE_1_STATUS.md
docs/current/ACTIVE_ROADMAP.md
```

Arquitectura y operación:

```text
docs/current/SERVICE_1_CANONICAL_AXIS.md
docs/current/SERVICE_1_ARCHITECTURE_LOCK.md
docs/current/SERVICE_1_ARCHITECTURE_COMPONENT_MAP_V1.md
docs/current/SERVICE_1_OPERABILITY_PACKET.md
docs/current/SERVICE_1_DEPLOYMENT_TARGET_CONTRACT_V1.md
```

Producto vendible:

```text
docs/current/SERVICE_1_SELLABLE_PRODUCT_CONTRACT_V1.md
```

Raíz física:

```text
pymia/smartpyme/service_1_product_pipeline_v1.py
pymia/cli/service_1_product.py
```

## Regla de reconciliación

Si un documento no rector contradice código/tests o un documento rector actualizado, se trata como:

```text
HISTORICAL_OR_SUPERSEDED
```

No se corrige arquitectura para hacer coincidir un documento histórico.

## Catálogos y contratos

Los JSON, schemas, ADRs y contratos técnicos son fuentes válidas sólo dentro de su scope y cuando la raíz productiva o un documento rector vigente los referencia explícitamente.
