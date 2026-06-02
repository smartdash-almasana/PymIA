# M17 — Hallazgo contractual supplier_duplicate_check vs dispatcher formal

Fecha: 2026-06-01  
Estado: hallazgo documentado  
Alcance: SmartPyme dispatcher formal, tests smoke y registry de capacidades.

---

## 1. Resumen

`Supplier duplicate check` no es una ficha vacía.

El plugin existe, está testeado como unidad y está conectado por el camino CLI.

Pero el dispatcher formal todavía conserva un contrato anterior de **un solo microservicio**, donde sólo `excel_diagnostic` puede ejecutarse y `supplier_duplicate_check` debe quedar `UNSUPPORTED`.

Por lo tanto, M17 no es sólo un cambio de implementación.

Es un cambio de contrato.

---

## 2. Estado actual natural

### Máquina instalada

```text
supplier_duplicate_check existe como plugin real.
```

Ruta:

```text
pymia/smartpyme/classifications/supplier_duplicate_check.py
```

Función:

```text
diagnose_supplier_duplicates(...)
```

### Máquina testeada

Ruta:

```text
tests/smartpyme/test_supplier_duplicate_check.py
```

Cubre:

```text
PASS con proveedor/cuit/razon_social
BLOCKED si falta proveedor
PARTIAL si sólo hay proveedor
DUPLICATE_CUIT
MISSING_CUIT
MISSING_RAZON_SOCIAL
NORMALIZATION_NEEDED
LEGAL_SUFFIX_VARIATION
```

### Máquina conectada por camino lateral

Ruta:

```text
pymia/smartpyme/e2e_cli.py
```

El CLI ejecuta:

```text
excel_diagnostic
supplier_duplicate_check
```

### Máquina no conectada al circuito formal

Ruta:

```text
pymia/smartpyme/microservice_dispatcher.py
```

El dispatcher formal ejecuta sólo:

```text
excel_diagnostic
```

Para otra clasificación devuelve:

```text
UNSUPPORTED
```

---

## 3. Hallazgo de tests

El test actual del dispatcher todavía defiende explícitamente el contrato viejo.

Ruta:

```text
tests/smartpyme/test_one_microservice_smoke.py
```

Casos relevantes:

```text
test_dispatcher_does_not_import_supplier_duplicate_check
test_unsupported_runtime_returns_unsupported
test_supplier_duplicate_check_module_not_loaded_by_dispatcher_import
```

Lectura natural:

```text
El contrato actual exige que el dispatcher no cargue supplier_duplicate_check
y que supplier_duplicate_check sea UNSUPPORTED por el dispatcher.
```

Eso era correcto cuando el dispatcher era de un solo microservicio.

Pero entra en conflicto con el nuevo registry, donde `supplier_duplicate_check` está implementado y conectado por CLI.

---

## 4. Interpretación

El sistema tiene dos verdades parciales:

### Camino CLI

```text
supplier_duplicate_check = ejecutable
```

### Camino dispatcher formal

```text
supplier_duplicate_check = unsupported
```

Por eso el estado real no es:

```text
NOT_IMPLEMENTED
```

sino:

```text
PARTIALLY_AVAILABLE_BY_PATH
```

---

## 5. Implicancia para M17

M17 debe actualizar simultáneamente:

```text
1. microservice_dispatcher.py
2. tests/smartpyme/test_one_microservice_smoke.py
3. docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
```

No alcanza con agregar una rama de código.

Hay que cambiar el contrato de smoke:

Antes:

```text
dispatcher formal = un solo microservicio Excel
```

Después:

```text
dispatcher formal = microservicios soportados explícitamente
```

---

## 6. Cambio esperado de contrato

### Mantener

```text
excel_diagnostic sigue ejecutándose igual.
classification desconocida sigue devolviendo UNSUPPORTED.
candidato no READY_TO_EXECUTE sigue devolviendo BLOCKED.
can_dispatch false sigue devolviendo BLOCKED.
fallo del worker sigue devolviendo FAILED.
```

### Cambiar

```text
supplier_duplicate_check deja de ser UNSUPPORTED en dispatcher formal.
```

Debe pasar a:

```text
EXECUTED | FAILED | BLOCKED
```

según corresponda.

---

## 7. Tests a modificar o reemplazar

### Reemplazar

```text
test_dispatcher_does_not_import_supplier_duplicate_check
```

por un test que acepte el nuevo contrato.

### Reemplazar

```text
test_unsupported_runtime_returns_unsupported
```

Hoy usa `supplier_duplicate_check` como ejemplo de unsupported.

Debe usar una clasificación realmente desconocida, por ejemplo:

```text
unknown_runtime_classification
```

### Reemplazar

```text
test_supplier_duplicate_check_module_not_loaded_by_dispatcher_import
```

Este test sólo tiene sentido si el dispatcher debe ser lazy y no importar supplier al cargar.

Si se mantiene lazy import, el test debe cambiar a:

```text
supplier_duplicate_check no se carga al importar dispatcher,
pero sí se carga/ejecuta al despachar supplier_duplicate_check.
```

Si se acepta import directo, el test debe eliminarse o reescribirse.

---

## 8. Nuevo test mínimo requerido

Agregar un smoke tipo:

```text
test_supplier_duplicate_check_ready_candidate_executes
```

Debe crear un Excel mínimo de proveedores:

```text
proveedor
cuit
razon_social
```

Debe construir candidate:

```text
runtime_classification = supplier_duplicate_check
microservice_name = supplier_duplicate_check_worker
status = READY_TO_EXECUTE
can_dispatch = True
```

Debe esperar:

```text
status == EXECUTED
findings_count >= 0
output_refs poblado si output_dir fue provisto
markdown contiene SmartPyme Supplier Duplicate Check
```

---

## 9. Registry esperado después de M17

En:

```text
docs/smartpyme/SMARTPYME_CAPABILITY_PLUGIN_REGISTRY.md
```

Actualizar `supplier_duplicate_check`:

Antes:

```yaml
dispatcher_available: false
cli_available: true
status: PARTIALLY_AVAILABLE_BY_PATH
```

Después:

```yaml
dispatcher_available: true
cli_available: true
status: AVAILABLE_BY_CLI_AND_DISPATCHER
```

---

## 10. Riesgo principal

Cambiar el dispatcher sin actualizar tests deja el repo fallando.

Actualizar tests sin conectar el dispatcher deja una promesa falsa.

M17 debe cerrar ambas cosas juntas.

---

## 11. Veredicto

```text
M17 = cambio de contrato + cambio de dispatcher + actualización de registry.
```

No es una feature nueva.

Es cierre de inconsistencia entre:

```text
máquina instalada
camino CLI funcionando
dispatcher formal desactualizado
tests defendiendo contrato viejo
```

---

## 12. Frase rectora

```text
El dispatcher no está roto: está defendiendo un contrato viejo.
M17 debe cambiar ese contrato de forma explícita y testeada.
```
