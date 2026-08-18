# Servicio 1 — F13 Longitudinal Result Memory V1

**Estado:** FROZEN CONTRACT — LOCAL + REMOTE GATES PASS  
**Base:** F0–F12 closed + committed  
**Objetivo:** persistir longitudinalmente ResultSets F9 ya gobernados, por tenant y período, sin recalcular, reinterpretar ni convertir la memoria en una autoridad alternativa.

## 1. Regla arquitectónica

F13 comienza únicamente después de F9/F12:

```text
P6 owner-confirmed semantics
→ P7 requirements/grain
→ P8 computability
→ F7 governed evidence
→ FormulaEngineService / F8 math
→ F9 governed ResultSet
→ F13 immutable longitudinal snapshot
```

F13 no ejecuta matemática, no modifica `AnalysisPlan`, no resuelve semántica y no autoriza delivery.

## 2. Contrato persistido

Cada `Service1ResultMemoryRecordV1` contiene como mínimo:

```text
tenant_id
cliente_id
identity_contract_id
case_id
analysis_id
period
  period_ref
  start_date
  end_date
  basis_ref
  source_refs
grain
formula_versions
result_set
result_set_integrity_digest
evidence_refs
owner_evidence_refs
executed_at
artifact_ref
artifact
```

Los authority flags permanecen siempre `False`, incluyendo `automatic_reuse_authorized`.

## 3. Identidad content-addressed

`memory_record_id` es SHA-256 determinístico sobre:

```text
identity contract
tenant
case
analysis
period
grain
formula versions
F9 ResultSet digest
compact evidence refs
owner evidence refs
artifact ref
```

`executed_at` no forma parte de esa identidad.

Consecuencia:

```text
mismo tenant + mismo período + mismo ResultSet + misma evidencia
→ mismo memory_record_id
→ replay idempotente

mismo período + ResultSet diferente
→ memory_record_id diferente
→ snapshot histórico adicional
```

F13 nunca reemplaza silenciosamente un snapshot anterior.

## 4. Período longitudinal

La memoria no se persiste si no puede establecer un período trazable.

V1 deriva el período sólo desde una columna `operation_date` aprobada por P6 y observable en la ingesta canónica.

```text
start_date = mínimo valor observado
end_date   = máximo valor observado
period_ref = start_date/end_date
```

Ejemplo físico `cafeteria_abc.xlsx`:

```text
Ventas.Fecha
→ operation_date confirmado
→ 2026-01-01 / 2026-05-25
```

Si falta fecha confirmada, existe más de una fuente no resoluble o aparece un valor no fecha:

```text
RESULT_MEMORY_PERIOD_EVIDENCE_REQUIRED
or
RESULT_MEMORY_PERIOD_EVIDENCE_INVALID
```

El análisis F12 puede seguir siendo matemáticamente válido; lo que queda bloqueado es su incorporación a memoria longitudinal.

## 5. Versionado matemático

Cada snapshot conserva:

```text
__analysis_math_runtime__ = SERVICE_1_ANALYSIS_MATH_EXECUTION_V1
```

Y, para cada fórmula empresarial realmente usada por F9:

```text
formula_ref -> formula_version
```

La versión se obtiene exclusivamente de `SUPPORTED_FORMULAS`, cargado desde la fuente canónica `pymia/contracts/formula_rules_v1.json`.

F13 no define fórmulas nuevas.

## 6. Integridad del ResultSet

El snapshot almacena el ResultSet F9 completo y valida nuevamente:

```text
scope = SERVICE_1_RESULT_SET_CANONICAL_PAYLOAD_V1
SHA-256(canonical ResultSet payload) == F9 integrity digest
```

El artifact es content-addressed:

```text
resultset:sha256:<F9 digest>
```

Una alteración posterior del payload produce:

```text
RESULT_MEMORY_RESULT_SET_DRIFT
```

La digest no afirma autenticidad criptográfica ni non-repudiation; conserva exactamente la semántica F9.

## 7. Evidencia

`evidence_refs` resume las fuentes físicas utilizadas por el ResultSet y sus relaciones.

`owner_evidence_refs` conserva las referencias a confirmaciones P6 y relaciones owner-confirmed que soportan los bindings P8.

Cuando P8 conserva un nombre de columna no sheet-qualified y existe la misma semántica en más de una hoja, F13 conserva todas las confirmaciones owner relevantes en lugar de inventar qué confirmación fue “la verdadera”.

## 8. Persistencia Supabase

Se reutiliza `Service1SupabasePersistenceAdapterV1`; no se crea un segundo persistence engine.

Tabla V1:

```sql
create table if not exists public.service1_analysis_result_memory (
    memory_record_id text primary key,
    identity_contract_id text not null,
    tenant_id text not null,
    cliente_id text,
    case_id text not null,
    analysis_id text not null,
    period_ref text not null,
    period_start date not null,
    period_end date not null,
    grain_payload jsonb not null,
    formula_versions jsonb not null,
    result_set_integrity_digest text not null check (length(result_set_integrity_digest) = 64),
    evidence_refs jsonb not null,
    owner_evidence_refs jsonb not null,
    executed_at timestamptz not null,
    artifact_ref text not null,
    record_payload jsonb not null,
    created_at timestamptz not null default now(),
    check (period_start <= period_end)
);

create index if not exists service1_analysis_result_memory_tenant_analysis_period_idx
    on public.service1_analysis_result_memory
    (tenant_id, analysis_id, period_start, period_end);

create index if not exists service1_analysis_result_memory_tenant_case_idx
    on public.service1_analysis_result_memory
    (tenant_id, case_id);

alter table public.service1_analysis_result_memory enable row level security;
```

El backend productivo usa `service_role`. No se crea policy permisiva para clientes directos.

## 9. Append-only físico

Para impedir modificación accidental de memoria histórica:

```sql
create or replace function public.service1_reject_result_memory_mutation()
returns trigger
language plpgsql
as $$
begin
    raise exception 'service1_analysis_result_memory is append-only';
end;
$$;

drop trigger if exists service1_analysis_result_memory_no_mutation
on public.service1_analysis_result_memory;

create trigger service1_analysis_result_memory_no_mutation
before update or delete on public.service1_analysis_result_memory
for each row execute function public.service1_reject_result_memory_mutation();
```

El adapter sólo usa:

```text
UPSERT ignore_duplicates on memory_record_id
SELECT tenant-scoped
```

Nunca ejecuta UPDATE o DELETE.

## 10. Lectura longitudinal

El adapter expone:

```text
persist_result_memory(record)
list_result_memory(tenant_id, analysis_id?, limit)
load_result_memory_record(tenant_id, memory_record_id)
```

Toda lectura valida nuevamente el payload y la frontera tenant.

`list_result_memory` ordena por período y ejecución. No calcula tendencia, deterioro o mejora.

Esas comparaciones futuras deben consumir snapshots F13 explícitos; nunca reabrir el Excel histórico ni usar memoria de un LLM.

## 11. Wiring workbook-first

Después de una ejecución F12/F9 `READY`, el journey intenta construir el snapshot F13.

```text
F9 ResultSet READY
→ tenant identity
→ confirmed semantic run
→ observed period
→ owner evidence refs
→ immutable memory record
→ durable adapter
```

El packet de resultado reporta explícitamente:

```text
PERSISTED
NOT_PERSISTED
NEEDS_EVIDENCE
PERSISTENCE_ERROR
```

Nunca se informa persistencia si el adapter no la confirmó.

## 12. Límites F13

F13 NO implementa:

```text
LLM memory
causal interpretation
trend diagnosis
severity
recommendations
historical recalculation
silent normalization of old results
cross-tenant comparison
result rewriting
```

## 13. Gate local

Evidencia implementada:

```text
REAL_CAFETERIA_PERIOD_DERIVATION
IMMUTABLE_RESULT_MEMORY_CONTRACT
CONTENT_ADDRESSED_IDEMPOTENCY
FORMULA_VERSION_CAPTURE
RESULTSET_TAMPER_DETECTION
OWNER_EVIDENCE_TRACEABILITY
SUPABASE_ADAPTER_APPEND_ONLY_CONTRACT
TENANT_ANALYSIS_HISTORY_READ
CROSS_TENANT_FAIL_CLOSED
WORKBOOK_FIRST_AUTO_PERSIST_WIRING
```

## 14. Gate remoto Supabase

El gate físico remoto F13 fue ejecutado contra Supabase con credenciales cargadas sólo en el proceso, sin persistir ni exponer secretos.

Resultado:

```text
REMOTE_TABLE_EXISTS = PASS
PRIMARY_KEY_MEMORY_RECORD_ID = PASS
REQUIRED_COLUMNS = PASS
TENANT_ANALYSIS_PERIOD_INDEX = PASS
TENANT_CASE_INDEX = PASS
RLS_ENABLED = PASS
PERMISSIVE_CLIENT_POLICY = 0
APPEND_ONLY_TRIGGER = PASS
PHYSICAL_INSERT = PASS
PHYSICAL_IDEMPOTENT_REPLAY = PASS
PHYSICAL_LOAD = PASS
PHYSICAL_LIST_BY_TENANT_ANALYSIS = PASS
PAYLOAD_ROUNDTRIP_VALIDATION = PASS
TENANT_ISOLATION = PASS
UPDATE_REJECTED = PASS
DELETE_REJECTED = PASS
APPEND_ONLY_PHYSICAL = PASS
```

El smoke remoto no modificó archivos tracked ni requirió cambios en el contrato F13.

## 15. Invariantes

```text
ONE_CANONICAL_PRODUCT_ROOT = PRESERVED
NO_SECOND_XLSX_PARSER = PASS
NO_PARALLEL_PRODUCTIVE_PIPELINE = PASS
NO_LLM_RUNTIME_AUTHORITY = PASS
OWNER_CONFIRMATION_IS_EVIDENCE_NOT_PERMISSION = PASS
P6_P7_P8_REMAIN_SEPARATE = PASS
P8_IS_COMPUTABILITY_AUTHORITY = PASS
FAIL_CLOSED = PASS
NO_UI_BUSINESS_MATH = PASS
NO_CAFETERIA_HARDCODE = PASS
NO_RUBRO_HARDCODE = PASS
NO_SECOND_MATH_AUTHORITY = PASS
RESULT_MEMORY_IS_NOT_AUTHORITY = PASS
