# SERVICE_1_BASELINE_CORRECTION_MINIMAL_PATCH_V1

## Estado

```text
DOCUMENT_TYPE: BASELINE_CORRECTION
SERVICE: S1_FULL_ASSISTED_V1
STATUS: MINIMAL_PATCH
RUNTIME_MODIFIED: NO
CODE_MOVED: NO
FILES_RENAMED: NO
TESTS_REQUIRED: NO
S2_BLOCKED: NO
```

---

# 1. Veredicto

```text
VERDICT: PARTIAL_CLEAN_BUT_NEEDS_NAMESPACE_CLARIFICATION
```

Servicio 1 permanece cerrado como baseline protegida, pero existe una ambigüedad documental y semántica: hay contratos y sandbox de conciliación bajo nombres históricos asociados a Servicio 1.

Esta ambigüedad no habilita conciliación productiva dentro de S1.

---

# 2. Corrección de frontera

Los artefactos de conciliación preexistentes bajo namespace o documentación S1 deben interpretarse como:

```text
LEGACY_PREPARATORY_CONTRACTS
CONTRACT_ONLY
RUNTIME_NOT_AUTHORIZED
NOT_PRODUCTIVE_RECONCILIATION
NOT_SELLABLE_AS_S1_CAPABILITY
```

La capacidad activa nueva de conciliación asistida pertenece a:

```text
S2_ADMIN_OPERATIONS_V1
```

---

# 3. Evidencia mínima revisada

Se verificaron referencias reales a conciliación en repo:

```text
PymIA-Live/pymia/smartpyme/service_1_accounting_contracts_v1.py
- contiene runtime_authorized: Literal[False]
- retorna runtime_authorized: False

PymIA-Live/pymia/smartpyme/bank_reconciliation_contract_v1.py
- contiene runtime_authorized: Literal[False]
- retorna runtime_authorized: False

PymIA-Live/pymia/smartpyme/mercado_pago_reconciliation_contract_v1.py
- contiene runtime_authorized: Literal[False]
- retorna runtime_authorized: False
```

Esto confirma que la ambigüedad principal es de namespace/documentación, no de runtime autorizado.

---

# 4. Artefactos afectados por la aclaración

Código histórico/preparatorio:

```text
PymIA-Live/pymia/smartpyme/service_1_accounting_contracts_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_contract_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_contract_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_fixture_model_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_fixture_handoff_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_review_packet_v1.py
PymIA-Live/pymia/smartpyme/bank_reconciliation_sandbox_completion_slice_v1.py
PymIA-Live/pymia/smartpyme/mercado_pago_reconciliation_contract_v1.py
```

Documentación histórica/preparatoria:

```text
docs/producto/SERVICE_1_BANK_RECONCILIATION_CONTRACT_V1.md
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_RUNTIME_CONTRACT_V1.md
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_MODEL_V1.md
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_FIXTURE_HANDOFF_V1.md
docs/producto/SERVICE_1_BANK_RECONCILIATION_SANDBOX_REVIEW_PACKET_V1.md
docs/producto/SERVICE_1_MERCADO_PAGO_RECONCILIATION_CONTRACT_V1.md
docs/producto/BANK_RECONCILIATION_SANDBOX_COMPLETION_SLICE_V1.md
```

---

# 5. Decisión explícita

```text
S1_RECONCILIATION_RUNTIME: NOT_AUTHORIZED
S1_RECONCILIATION_COMMERCIAL_CLAIM: FORBIDDEN
S1_RECONCILIATION_DOCS: LEGACY_PREPARATORY_ONLY
S2_RECONCILIATION_ACTIVE_FRONT: YES
```

S1 no vende ni promete:

```text
- conciliación definitiva;
- conciliación bancaria cerrada;
- auditoría;
- certificación;
- saldo real confirmado;
- cierre contable;
- integración bancaria;
- Mercado Pago productivo;
- APIs transaccionales.
```

S2 sí puede avanzar en:

```text
- conciliación asistida;
- candidatos de match;
- diferencias visibles;
- pendientes;
- faltantes de evidencia;
- revisión humana requerida.
```

---

# 6. Regla de interpretación

Si un documento o módulo anterior usa lenguaje de conciliación bajo S1, debe leerse bajo esta regla:

```text
CONTRACT_ONLY_UNDER_HUMAN_REVIEW
NO_RUNTIME_AUTHORIZATION
NO_PRODUCTIVE_CLAIM
NO_FINAL_RECONCILIATION
```

Si el lenguaje sugiere capacidad productiva, prevalece este patch.

---

# 7. Por qué no se renombran archivos ahora

No se renombran ni migran archivos en este patch porque:

```text
- evitaría un refactor innecesario;
- podría romper referencias históricas;
- mezclaría corrección documental con cambio técnico;
- abriría riesgo de deriva.
```

La corrección actual es suficiente para proteger la frontera semántica S1/S2.

---

# 8. Relación con Servicio 2

Servicio 2 ya contiene el frente activo nuevo:

```text
S2_ADMIN_OPERATIONS_V1
S2_MICROSLICE_001_RECONCILIATION_MATCH_CANDIDATES
```

La continuación permitida no debe usar el nombre micro-slice aislado. Debe avanzar como bloque funcional mediano:

```text
S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1
```

---

# 9. Próximo frente permitido

```text
NEXT_ALLOWED_FRONT: S2_RECONCILIATION_ASSISTED_REVIEW_BLOCK_V1
S1_REOPEN_REQUIRED: NO
S1_RUNTIME_CHANGE_ALLOWED: NO
```

---

# 10. Cierre

Este patch no cambia la implementación. Sólo corrige la interpretación de frontera:

```text
Servicio 1 queda protegido como primeros auxilios operativos sobre archivos.
Servicio 2 concentra la conciliación asistida administrativa.
Los artefactos históricos de conciliación bajo S1 son legacy/preparatorios/no runtime.
```
