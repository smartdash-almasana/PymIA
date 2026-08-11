# SERVICE_1_RADAR_SUPABASE_TABLE_V1

Estado: PHYSICAL V1 EXISTS / HARDENING MIGRATION PENDING
Fecha: 2026-08-10

## 1. Estado físico conocido

La tabla remota `public.service1_radar_observation_policies` ya fue creada y probada físicamente en Supabase con INSERT/LOAD/LIST/enabled-only/idempotent replay/tenant isolation.

El primer esquema físico usó:

```text
policy_ref PRIMARY KEY
comparison_value text
RLS no habilitado
```

Después del hardening de dominio, el contrato canónico cambia en dos puntos:

1. identidad de policy tenant-scoped: `(tenant_id, policy_ref)`;
2. `comparison_value` debe soportar V1:
   - `METRIC` -> número finito;
   - `OPERATION` -> booleano.

El código productivo ya espera `on_conflict="tenant_id,policy_ref"`.

---

## 2. Contrato canónico de tabla después del hardening

```sql
create table public.service1_radar_observation_policies (
    tenant_id text not null,
    policy_ref text not null,
    observable_ref text not null,
    enabled boolean not null,
    operator text not null,
    comparison_value jsonb not null,
    communication_level text not null check (
        communication_level in ('REPORT', 'NOTIFICATION', 'ALERT', 'URGENCY')
    ),
    confirmed_by_owner boolean not null check (confirmed_by_owner = true),
    policy_payload jsonb not null,
    created_at timestamptz not null default now(),
    primary key (tenant_id, policy_ref)
);

create index if not exists service1_radar_observation_policies_tenant_idx
    on public.service1_radar_observation_policies (tenant_id);

create index if not exists service1_radar_observation_policies_tenant_enabled_idx
    on public.service1_radar_observation_policies (tenant_id, enabled);
```

`comparison_value jsonb` preserva tipos primitivos sin convertirlos silenciosamente:

```text
METRIC    -> 90 / 97.5 / 100000
OPERATION -> true / false
```

La validación de tipo y semántica sigue perteneciendo al contrato de dominio, no a SQL.

---

## 3. Migración requerida desde el esquema físico V1

Antes de migrar, eliminar las filas técnicas de smoke:

```sql
delete from public.service1_radar_observation_policies
where tenant_id = 'tenant_radar_smoke_a';
```

Aplicar luego:

```sql
alter table public.service1_radar_observation_policies
    drop constraint if exists service1_radar_observation_policies_pkey;

alter table public.service1_radar_observation_policies
    alter column comparison_value type jsonb
    using to_jsonb(comparison_value);

alter table public.service1_radar_observation_policies
    add primary key (tenant_id, policy_ref);
```

Si la tabla contiene únicamente datos técnicos de smoke y no existe información productiva, es aceptable recrearla directamente con el contrato canónico en lugar de migrarla.

---

## 4. RLS

Debe habilitarse RLS como defensa en profundidad:

```sql
alter table public.service1_radar_observation_policies enable row level security;
```

El adapter servidor actual opera con `service_role`, por lo que no requiere una policy abierta para funcionar.

No crear una policy permisiva genérica para usuarios autenticados sin definir antes el contrato de identidad tenant-scoped de esa vía de acceso.

Principio:

```text
service_role backend
→ puede operar

cliente directo
→ deny by default hasta existir policy explícita y tenant-safe
```

---

## 5. Invariantes

- La identidad canónica es `(tenant_id, policy_ref)`.
- Dos tenants pueden reutilizar el mismo `policy_ref` sin colisión.
- La persistencia es idempotente para la misma identidad y payload idéntico.
- Misma identidad con payload diferente debe fallar cerrado.
- Toda lectura/listado debe filtrar por `tenant_id`.
- `confirmed_by_owner` debe ser `true`.
- `enabled` debe ser booleano real.
- El payload recuperado debe reconstruirse estrictamente; no se normaliza basura de DB.
- `METRIC` admite solo comparación numérica finita.
- `OPERATION` admite comparación booleana V1.
- La tabla no contiene riesgo, severidad, positividad o urgencia empresarial implícita.
- `REPORT / NOTIFICATION / ALERT / URGENCY` son niveles de comunicación elegidos por el dueño.

---

## 6. Gate antes de RADAR_ENGINE_V1

No considerar cerrada la persistencia física endurecida hasta verificar:

```text
COMPOSITE_PK: PASS
COMPARISON_VALUE_JSONB: PASS
RLS_ENABLED: PASS
SMOKE_ROWS_REMOVED: PASS
PHYSICAL_INSERT_METRIC: PASS
PHYSICAL_INSERT_OPERATION: PASS
PHYSICAL_ROUNDTRIP: PASS
TENANT_ISOLATION: PASS
IDEMPOTENT_REPLAY: PASS
```
