# Biblioteca documental PymIA

## Autoridad

La autoridad documental vigente de Servicio 1 es externa a este árbol documental y sigue este orden:

```text
NOP-1 VIGENTE
→ NOP-2 VIGENTE
→ SERVICE 1 — KNOWN STATE
→ Gold Registry / evidencia física cerrada
```

`docs/current/README.md` es sólo un índice físico subordinado. Ningún README, auditoría, closeout, roadmap, handoff, Architecture Lock, Canonical Axis, documento de producto, landing, protocolo Hermes o corpus migrado puede competir con NOP-1/NOP-2 como autoridad vigente.

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

La continuidad vigente debe comenzar fuera de este árbol histórico:

```text
NOP-1 VIGENTE
→ NOP-2 VIGENTE
→ SERVICE 1 — KNOWN STATE
→ Gold Registry / evidencia física cerrada
```

Los documentos bajo `docs/current/` conservan valor técnico, contractual o histórico según su alcance, pero no constituyen por sí mismos autoridad vigente ni pueden definir el próximo paso.

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
