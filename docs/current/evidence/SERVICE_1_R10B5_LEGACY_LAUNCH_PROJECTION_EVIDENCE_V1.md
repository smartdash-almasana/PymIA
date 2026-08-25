# Servicio 1 — R10B5 legacy launch projection evidence

Date: 2026-08-24

## Scope

R10B5 removes only the residual post-semantic launch compatibility projection. Canonical F10 discovery, F12 commercial exposure, P7/P8 computability, and the existing direct legacy workflow entrypoints remain intact. Canonical-ingestion aliases and R11 are out of scope.

## Before / after

Before, `build_service_1_post_semantic_analysis_discovery_v1` emitted the compatibility fields `available`, `blocked`, and `legacy_launch_compatibility`, and two Web consumers read those fields. The builder also duplicated P8 decisions over `_LAUNCH_REVIEW_OPTIONS`.

After, that builder and its two consumers are removed. Web menu construction calls the canonical `build_service_1_dynamic_analysis_discovery_v1` and `project_service_1_dynamic_discovery_menu_v1` directly. The menu preserves canonical F10/F12 available and blocked analysis information. Post-discovery execution checks use the existing P8 computability decision directly; no compatibility projection, wrapper, alias, or fallback was added. Existing direct launch workflow entrypoints remain available for their specialized behavior.

## Static evidence

- `build_service_1_post_semantic_analysis_discovery_v1`: zero references in `pymia/` and `tests/` Python sources.
- `legacy_launch_compatibility`: zero references in `pymia/` and `tests/` Python sources.
- Web no longer reads `discovery["available"]` or `discovery["blocked"]` from the removed packet.
- Canonical F10/F12 menu data remains sourced from `project_service_1_dynamic_discovery_menu_v1`.

## Focal verification

Command:

```text
python -m pytest -q tests/smartpyme/test_service_1_assisted_semantic_product_wiring_v1.py tests/smartpyme/test_service_1_assisted_web_http_v1.py tests/smartpyme/test_service_1_dynamic_analysis_discovery_f10_v1.py tests/smartpyme/test_service_1_catalog_expansion_f12_v1.py
```

Result: **67 passed / 0 failed** in 196.51 seconds.

No full suite, R11, commit, push, or deploy was run.
