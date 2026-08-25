# Servicio 1 — R10B5 ChatGPT Physical Audit V1

**Fecha/hora:** 2026-08-24 16:15 ART (UTC-03:00)

## Veredicto

`PASS_PHYSICAL_AUDIT`

## Verificación física

- `build_service_1_post_semantic_analysis_discovery_v1` tiene 0 referencias en `pymia/`.
- `legacy_launch_compatibility` no existe en runtime/tests actuales; las coincidencias restantes están sólo en evidencia histórica y `_audit/`.
- `Service1SemanticReceptionWebApplicationV1._post_semantic_analysis_menu_page()` consume directamente `build_service_1_dynamic_analysis_discovery_v1(...)` y luego `project_service_1_dynamic_discovery_menu_v1(...)`.
- La UI conserva `available` y `blocked` como datos del **menu canónico proyectado**, no como campos de la proyección legacy retirada.
- El flujo continúa fail-closed si F10 discovery o su proyección de menú no están `READY`.
- No se observó wrapper, alias, fallback o segundo discovery path nuevo en el alcance auditado.

## Tests

La evidencia Codex registra:

`67 passed / 0 failed`

Se intentó rerun independiente mediante MCP-5000 del mismo focal, pero el gateway devolvió HTTP 502 antes de obtener resultado. No se reintentó para evitar confundir fallo de infraestructura con fallo de tests.

## Estado

- `LEGACY_LAUNCH_PROJECTION = REMOVED`
- `CANONICAL_F10_DISCOVERY = PRESERVED`
- `CANONICAL_MENU_PROJECTION = PRESERVED`
- `R11 = NOT_STARTED`

Siguiente frente R10: aliases transitorios del canonical ingestion envelope, a migrar por slices antes de cualquier eliminación masiva.
