# SERVICE_1_ACCOUNTING_WORKPAPER_SYNTHETIC_EDGE_CASE_SERIES_V1

VEREDICT:

```text
SYNTHETIC_EDGE_CASE_SERIES_V1: EXECUTED_AS_CONTROLLED_MARKDOWN_SERIES
```

PURPOSE:

```text
Registrar una serie sintética adversa para validar seguridad operativa, límites, recorte y bloqueo del microservicio asistido de Servicio 1:
Papel de trabajo contable asistido.

La serie no busca repetir casos felices ni validar nueva funcionalidad.
```

SERIES_SCOPE:

```text
Casos sintéticos/controlados.
Artefactos operativos preservados fuera del repo.
No datos reales.
No código.
No tests.
No parser.
No OCR.
No APIs.
No XLSX commiteados.

Nota operativa: en esta ejecución se generaron artefactos markdown externos. No se generaron XLSX binarios desde MCP para no falsificar entregables.
```

CASES_EXECUTED:

```text
CASE_003_INCOMPLETE_SALES_COLLECTIONS
CASE_004_DUPLICATED_COLLECTIONS
CASE_005_PURCHASES_PAYMENTS_MISSING_MASTER_DATA
CASE_006_NEGATIVE_AMOUNTS_AND_CREDIT_NOTES
CASE_007_TOO_BROAD_MIXED_CASE
CASE_008_NO_TRANSACTION_KEYS
```

CASE_RESULTS_SUMMARY:

```text
CASE_003_INCOMPLETE_SALES_COLLECTIONS:
  family: ventas declaradas vs cobros declarados
  expected: PARTIAL_CONTROLLED_PILOT_RUN
  actual: PARTIAL_CONTROLLED_PILOT_RUN
  behavior: faltantes visibles sin inventar cobros
  pass_fail: PASS

CASE_004_DUPLICATED_COLLECTIONS:
  family: ventas declaradas vs cobros declarados
  expected: PASS_WITH_WARNINGS
  actual: PASS_WITH_WARNINGS
  behavior: posibles duplicados marcados para revisión humana
  pass_fail: PASS

CASE_005_PURCHASES_PAYMENTS_MISSING_MASTER_DATA:
  family: compras declaradas vs pagos declarados
  expected: PASS_WITH_WARNINGS
  actual: PASS_WITH_WARNINGS
  behavior: datos maestros incompletos marcados como brecha
  pass_fail: PASS

CASE_006_NEGATIVE_AMOUNTS_AND_CREDIT_NOTES:
  family: compras declaradas vs pagos declarados
  expected: NEEDS_HUMAN_REVIEW
  actual: NEEDS_HUMAN_REVIEW
  behavior: importes negativos/notas de crédito separados de pagos normales
  pass_fail: PASS

CASE_007_TOO_BROAD_MIXED_CASE:
  family: mixta
  expected: BLOCKED_OR_SCOPE_REDUCTION_REQUIRED
  actual: BLOCKED_OR_SCOPE_REDUCTION_REQUIRED
  behavior: caso amplio rechazado o enviado a reducción de alcance
  pass_fail: PASS

CASE_008_NO_TRANSACTION_KEYS:
  family: ventas/cobros o compras/pagos
  expected: NEEDS_SCOPE_REDUCTION
  actual: NEEDS_SCOPE_REDUCTION
  behavior: sin llaves sólo procede análisis agregado o pedido de columnas mínimas
  pass_fail: PASS
```

ACCEPTANCE_BEHAVIOR:

```text
Los casos aceptables con advertencias fueron procesados como revisión controlada:
- faltantes de cobros
- duplicados probables
- datos maestros incompletos
- importes negativos o notas de crédito

La aceptación no implicó auditoría, certificación, conciliación definitiva ni resultado final.
```

REJECTION_BEHAVIOR:

```text
El caso mixto amplio fue bloqueado o enviado a reducción de alcance.
No se intentó analizar ventas, compras, banco, Mercado Pago y stock en un único frente.
```

SCOPE_REDUCTION_BEHAVIOR:

```text
Cuando faltan llaves transaccionales o el caso es demasiado amplio, el comportamiento correcto es:
- pedir columnas mínimas
- limitar a análisis agregado
- reducir a una familia operativa soportada
- bloquear si el cliente exige resultado final
```

EVIDENCE_GAP_BEHAVIOR:

```text
Las brechas de evidencia fueron registradas como brechas documentales, no como conclusiones contables.

Patrones observados:
- cobros faltantes
- comprobantes o referencias ausentes
- proveedor/CUIT/fecha faltante
- soporte de nota de crédito ausente
- llaves transaccionales insuficientes
```

HUMAN_REVIEW_PATTERN:

```text
Todos los casos requieren revisión humana.

La revisión humana es especialmente crítica para:
- duplicados probables
- notas de crédito
- importes negativos
- datos maestros incompletos
- faltantes de llaves
- pedidos demasiado amplios
```

BOUNDARIES_PRESERVED:

```text
No auditoría.
No certificación.
No conciliación definitiva.
No validación fiscal.
No resultado contable final.
No garantía de exactitud.
No asientos automáticos.
No API bancaria.
No Mercado Pago API.
No Mercado Libre API.
No OCR.
No parser automático nuevo.
No datos reales.
No XLSX commiteados.
```

FAILURES_OR_WEAKNESSES:

```text
No hubo deriva de claims.
No hubo apertura de APIs/OCR/parser.
No hubo intento de resolver criterio profesional final.

Debilidad operativa observada:
- el runbook debe incorporar reglas explícitas para duplicados, notas de crédito/importes negativos, falta de llaves y reducción de alcance.
- en esta ejecución MCP no generó XLSX binarios; los casos quedaron como artefactos markdown externos controlados.
```

PRODUCT_LEARNINGS:

```text
- El servicio soporta casos no felices si preserva límites.
- Las advertencias son parte del valor del producto.
- Bloquear o reducir alcance es comportamiento correcto, no falla.
- Las diferencias visibles no deben presentarse como cierre contable.
- Las brechas documentales ayudan a ordenar la conversación con el contador.
- No conviene abrir parser/OCR/API todavía.
```

OPERATOR_LEARNINGS:

```text
El operador necesita reglas explícitas para:
- no inventar cobros faltantes
- marcar duplicados como probables
- tratar datos maestros incompletos como brecha
- separar notas de crédito/importes negativos de pagos normales
- bloquear casos mixtos amplios
- pedir llaves mínimas antes de análisis transaccional
```

READINESS_IMPACT:

```text
READINESS_REINFORCED
```

NEXT_SAFE_ACTION:

```text
PATCH_OPERATOR_RUNBOOK_WITH_EDGE_CASE_RULES
```

COMMIT_READY:

```text
YES
```
