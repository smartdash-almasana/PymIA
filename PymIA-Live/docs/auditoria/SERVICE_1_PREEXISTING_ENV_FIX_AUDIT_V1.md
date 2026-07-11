# SERVICE_1_PREEXISTING_ENV_FIX_AUDIT_V1

**Auditoría de entorno `exceland_factory` / specs** (solo lectura; NO instala, NO
modifica código).

Objetivo: explicar por qué 11 tests de la suite S1 fallan y determinar si el fix
es de entorno, `pyproject`, `SPEC_ROOT` o fixtures.

---

## VERDICT

**ENV_ONLY — los 11 fallos son de entorno, no bugs de lógica de Servicio 1.**

`exceland_factory` está instalado en el venv del proyecto pero resuelve su
directorio de specs a una ruta que **no existe**, y el repo fuente `exeland2`
(no presente en disco) es de donde deberían provenir esos specs. No hay nada que
arreglar en el flujo asistido ni en los módulos de Servicio 1.

---

## HEAD

- `HEAD == origin/main == 50f76e3`
- Working tree limpio (1 archivo ajeno `../task.zip` untracked, fuera de alcance).
- Este slice NO commitea (solo doc de auditoría de entorno si se decidiera; aquí
  solo reporte).

---

## WT

Limpio. Sin cambios.

---

## PYTHON_USED

- Intérprete que usa pytest: `E:\BuenosPasos\smartbridge\PymIA\.venv\Scripts\python.exe`
  (es el venv del **proyecto** `PymIA`, no el de `PymIA-Live` ni el de Hermes).
- Invocación canónica verificada: `PYTHONPATH= ../.venv/Scripts/python.exe -m pytest ...`
  (el `PYTHONPATH=` evita la fuga del venv roto de Hermes).

---

## EXCELAND_LOCATION

- Paquete importado: `E:\BuenosPasos\smartbridge\PymIA\.venv\Lib\site-packages\exceland_factory`
- Declarado en `PymIA-Live/pyproject.toml` línea 14:
  `"exceland-factory @ file:../../../exeland2"`
  (apunta a un repo hermano `exeland2` tres niveles arriba del pyproject).
- **Ese repo `exeland2` NO existe en disco** (`/e/BuenosPasos/smartbridge/exeland2`
  ausente). La instalación en el venv es por tanto "huérfana" (sin fuente local).

---

## SPEC_SEARCH_PATHS

En `exceland_factory/factory.py` -> `config.SPECS_DIR`, definido en
`exceland_factory/registry.py`:

```
_REPO_ROOT = Path(__file__).resolve().parents[2]   # = .../PymIA/.venv/Lib/site-packages/exceland_factory/../../..  =>  PymIA/.venv/Lib
SPECS_DIR  = _REPO_ROOT / "specs"
CATALOG_DIR = _REPO_ROOT / "catalog"
```

Resolución real (bajo `PYTHONPATH=`):

- `SPECS_DIR  = E:\BuenosPasos\smartbridge\PymIA\.venv\Lib\specs`   -> **existe: False**
- `CATALOG_DIR = E:\BuenosPasos\smartbridge\PymIA\.venv\Lib\catalog` -> **existe: False**

La función `build_product(slug)` primero intenta `slug` como path; si no existe,
lo resuelve como `SPECS_DIR / f"{slug}.yaml"`. Al faltar el dir, cae en
`FileNotFoundError: Spec no encontrado: .../.venv/Lib/specs/<slug>.yaml`.

---

## SPECS_FOUND

Buscados en todo el repo (excluyendo `site-packages` y `PymIA-Live/.venv`):

- `caja_diaria.yaml`          -> **no encontrado**
- `precio_margen*.yaml` (incl. `precio_margen_basico_template`) -> **no encontrado**
- `stock_control.yaml`        -> **no encontrado**
- cualquier dir `specs/` fuera de site-packages -> **no encontrado**
- `product_registry.yaml`     -> **no encontrado**

Los tests piden estos slugs: `precio_margen`, `precio_margen_basico_template`,
`precio_margen_minimal`, `caja_diaria`, `stock_control`. Ningún spec existe.

---

## FAILURES_COUNT

Corrida de los 4 archivos pedidos:

```
pytest test_exceland_execution_flow_v1.py
       test_exceland_factory_smoke_v1.py
       test_exceland_runtime_v1.py
       test_service_1_operator_cli.py
=> 11 failed, 27 passed  (37.9s)
```

Los 11 fallidos = los 11 remanentes del triage previo:

| test | archivo | status devuelto | causa inmediata |
|------|---------|-----------------|-----------------|
| test_success_precio_margen | test_exceland_execution_flow_v1.py | RUNTIME_ERROR | factory no halla spec |
| test_success_caja_diaria | idem | RUNTIME_ERROR | idem |
| test_success_stock_control | idem | RUNTIME_ERROR | idem |
| test_build_product_creates_xlsx_with_sheets | test_exceland_factory_smoke_v1.py | FileNotFoundError | spec ausente |
| test_build_product_respects_runtime_authorized_false | idem | FileNotFoundError | idem |
| test_build_product_with_minimal_spec | idem | FileNotFoundError | idem |
| test_success_path_generates_xlsx_with_sheets | test_exceland_runtime_v1.py | FACTORY_ERROR | spec ausente |
| test_success_path_custom_filename | idem | FACTORY_ERROR | idem |
| test_allowed_product_refs_are_callable | idem | FACTORY_ERROR | idem |
| test_cli_run_factory_success | test_service_1_operator_cli.py | assert 'OK' | el factory subyacente falla (mismo root) |
| test_cli_run_factory_custom_output_filename | idem | assert 'OK' | idem |

---

## ROOT_CAUSE

1. `exceland_factory` está instalado en `PymIA/.venv` pero su `SPECS_DIR` apunta a
   `PymIA/.venv/Lib/specs`, que nunca se creó.
2. El origen de los specs (`exeland2`) no está en disco, así que no se pueden
   regenerar copiándolos del repo fuente.
3. Sin specs, `build_product`/`run_exceland_*` devuelven error (no `OK`), y la CLI
   legacy (`operator_cli`) igualmente no llega a emitir `OK`.

Es 100% de entorno: `exceland_factory` es una dependencia externa (monorepo
hermano `exeland2`) ausente en esta máquina. No afecta los 12 eslabones del flujo
asistido ni el orquestador (que no lo usan).

---

## SAFE_FIX_PLAN (no ejecutado en este slice)

Orden recomendado, todos fuera del flujo asistido:

1. **Recuperar `exeland2`**: clonar/traer el repo hermano en
   `/e/BuenosPasos/smartbridge/exeland2` (raíz del `file:../../../exeland2`).
2. **Reinstalar con specs**: `cd PymIA-Live && PYTHONPATH= ../.venv/Scripts/python.exe -m pip install -e .`
   para que `exceland-factory` se relinke al `exeland2` real y copie/monte sus
   `specs/` y `catalog/`.
3. **Alternativa sin repo fuente**: si `exeland2` no está disponible, crear
   `PymIA/.venv/Lib/specs/` con los YAML mínimos (`caja_diaria.yaml`,
   `precio_margen_basico_template.yaml`, `stock_control.yaml`,
   `product_registry.yaml`) como fixtures del entorno. Esto es un fix de
   **fixtures/env**, no de código de Servicio 1.
4. **No tocar `pyproject`** salvo para corregir la ruta de `exeland2` si la raíz
   real difiere. No se requiere cambio de `SPEC_ROOT` en el paquete (la ruta por
   defecto es correcta una vez que el venv tenga los specs).

Categoría del fix: **ENV_ONLY** (o **fixtures** si se opta por YAML mínimos).
Ningún módulo de Servicio 1 necesita cambio.

---

## NEXT_PROMPT

Si querés avanzar, el siguiente slice seguro sería:

> TASK: SERVICE_1_PREEXISTING_ENV_FIX_V1
> BASE: PymIA-Live, HEAD == origin/main == 50f76e3
> DO: recuperar/instalar exceland_factory + specs en PymIA/.venv (sin tocar
>      módulos ni flujo asistido).
> CHECK: luego re-correr los 4 archivos y confirmar 0 fallos de ese grupo.
> DON'T: no modificar código de Servicio 1, no refactor, no reescribir specs
>        de negocio (usar los del repo fuente exeland2 o fixtures mínimos).

O, si preferís no depender del repo externo, un slice de **fixtures** que cree los
YAML mínimos bajo `PymIA/.venv/Lib/specs/`.
