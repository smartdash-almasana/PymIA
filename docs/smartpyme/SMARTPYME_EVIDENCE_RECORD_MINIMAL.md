# SMARTPYME_EVIDENCE_RECORD_MINIMAL

## 1. Propósito

Definir el contrato mínimo de **EvidenceRecord**: una unidad de metadata que
registra evidencia recibida (o referenciada) por `tenant_id` e `intake_id`.

Este slice es **puramente declarativo**:

- no abre archivos;
- no lee bytes;
- no calcula hash;
- no infiere MIME;
- no valida contenido documental;
- no decide si la evidencia satisface una `IntakeEvidenceRequest`;
- no cambia `intake_state`;
- no ejecuta análisis;
- no despacha microservicios;
- **no persiste** `EvidenceRecord` todavía.

La persistencia queda para el frente posterior
`SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE`.

## 2. Alcance

### Dentro del alcance

- Dataclass `EvidenceRecord` con 15 campos.
- Factory `create_evidence_record(...)` con validación fail-closed.
- `to_dict()` serializable a JSON sin encoder custom.
- Constantes exportadas de estados y source kinds.
- Tests unitarios en `tests/smartpyme/test_evidence.py`.

### Fuera del alcance

- Persistencia (storage).
- Cálculo de `content_hash`.
- Lectura o apertura de archivos.
- Inferencia de `mime_type`.
- Validación de contenido documental (Excel, PDF, etc.).
- Decisión de suficiencia (`SATISFIED` / `REJECTED` como transición automática).
- Cambio de `IntakeRecord.intake_state`.
- Ejecución de clasificaciones reales (`excel_diagnostic`,
  `supplier_duplicate_check`).
- Integración con Telegram, Hermes, Output Gateway.
- Integración con `e2e_cli.py`.

## 3. Contrato EvidenceRecord

```python
@dataclass
class EvidenceRecord:
    evidence_id: str          # "evidence_<uuid4.hex>"
    tenant_id: str            # obligatorio
    intake_id: str            # obligatorio
    request_id: str | None    # opcional: vínculo con IntakeEvidenceRequest
    evidence_type: str        # obligatorio (ej: "excel_proveedores")
    source_kind: str          # obligatorio, uno de ALLOWED_SOURCE_KINDS
    source_ref: str           # obligatorio, referencia opaca
    original_filename: str | None
    mime_type: str | None
    size_bytes: int | None
    content_hash: str | None  # informational, NO calculado por este slice
    status: str               # uno de ALLOWED_EVIDENCE_STATUSES
    received_at: str          # ISO-8601 UTC
    notes: list[str]          # default [], copia defensiva
    metadata: dict            # default {}, copia defensiva
```

### Factory pública

```python
def create_evidence_record(
    *,
    tenant_id: str,
    intake_id: str,
    evidence_type: str,
    source_kind: str,
    source_ref: str,
    request_id: str | None = None,
    original_filename: str | None = None,
    mime_type: str | None = None,
    size_bytes: int | None = None,
    content_hash: str | None = None,
    status: str = "RECEIVED",
    notes: list[str] | None = None,
    metadata: dict | None = None,
) -> EvidenceRecord
```

## 4. Estados permitidos

| Estado      | Significado                                                          |
|-------------|----------------------------------------------------------------------|
| `RECEIVED`  | Evidencia declarada como recibida (default).                         |
| `REGISTERED`| Evidencia registrada formalmente en el sistema.                      |
| `REJECTED`  | Evidencia descartada (fuera de alcance, ilegible, no aplica).        |
| `LINKED`    | Evidencia vinculada a un intake/request específico.                  |
| `SUPERSEDED`| Evidencia reemplazada por una versión más nueva.                     |

Constantes exportadas:

```python
EVIDENCE_STATUS_RECEIVED    = "RECEIVED"
EVIDENCE_STATUS_REGISTERED  = "REGISTERED"
EVIDENCE_STATUS_REJECTED    = "REJECTED"
EVIDENCE_STATUS_LINKED      = "LINKED"
EVIDENCE_STATUS_SUPERSEDED  = "SUPERSEDED"

ALLOWED_EVIDENCE_STATUSES   = (...)
```

## 5. Source kinds permitidos

| Source kind      | Significado                                                |
|------------------|------------------------------------------------------------|
| `uploaded_file`  | Archivo subido por el usuario (ruta física o referencia).  |
| `manual_text`    | Texto provisto inline por el usuario.                      |
| `external_ref`   | Referencia externa (URL, Drive, etc.).                     |
| `generated`      | Archivo generado por el propio sistema.                    |
| `unknown`        | Origen desconocido o no declarado.                         |

Constantes exportadas:

```python
SOURCE_KIND_UPLOADED_FILE = "uploaded_file"
SOURCE_KIND_MANUAL_TEXT   = "manual_text"
SOURCE_KIND_EXTERNAL_REF  = "external_ref"
SOURCE_KIND_GENERATED     = "generated"
SOURCE_KIND_UNKNOWN       = "unknown"

ALLOWED_SOURCE_KINDS      = (...)
```

## 6. Relación con IntakeEvidenceRequest

`IntakeEvidenceRequest` (definido en `pymia/smartpyme/intake.py`) describe
**qué se necesita**:

- `request_id`
- `evidence_type`
- `description`
- `required_fields`
- `reason`
- `blocks_analysis`
- `enables_classification`
- `source_tank`
- `status`

`EvidenceRecord` describe **qué se recibió o se referencia**:

- `evidence_id`
- `tenant_id`, `intake_id`
- `request_id` (vínculo opcional con la request)
- `evidence_type` (idealmente coincide con el de la request)
- `source_kind`, `source_ref`
- metadata física (filename, mime, size, hash) si se conoce
- `status` (ciclo de vida propio)

La vinculación mínima se hace por:

- `tenant_id`
- `intake_id`
- `request_id` (opcional)
- `evidence_type`

**Este slice NO decide si la evidencia satisface la request.** Eso es
responsabilidad de un slice posterior (readiness gate).

## 7. Relación con IntakeRecord

`IntakeRecord` registra contexto semántico previo al análisis:

- qué dijo el usuario;
- qué se interrogó;
- qué tanques aplican;
- qué evidencia se necesita (lista de `IntakeEvidenceRequest`);
- estado del intake.

`EvidenceRecord` registra evidencia concreta vinculada a un intake:

- un intake puede tener 0, 1 o N `EvidenceRecord` asociados;
- los `EvidenceRecord` se vinculan por `tenant_id` + `intake_id` +
  `request_id` (opcional).

**Este slice NO modifica `IntakeRecord`.**
**Este slice NO cambia `intake_state`.**

## 8. Safety gates

### 8.1 NO_FILE_IO

`create_evidence_record`:

- no abre archivos;
- no lee bytes;
- no calcula hash;
- no comprueba existencia física de `source_ref`;
- no infiere `mime_type` desde el filename.

### 8.2 NO_DIAGNOSIS

- no ejecuta análisis;
- no invoca `excel_diagnostic` ni `supplier_duplicate_check`;
- no decide suficiencia;
- no cambia `intake_state`.

### 8.3 FAIL_CLOSED

`create_evidence_record` lanza `ValueError` si:

- `tenant_id`, `intake_id`, `evidence_type`, `source_kind` o `source_ref`
  están vacíos;
- `source_kind` no está en `ALLOWED_SOURCE_KINDS`;
- `status` no está en `ALLOWED_EVIDENCE_STATUSES`;
- `size_bytes` no es `None` y es negativo;
- `size_bytes` no es `None` y no es `int` (rechaza `bool`);
- `notes` no es `None` y no es `list`;
- `metadata` no es `None` y no es `dict`.

### 8.4 DEFENSIVE_COPY

- `notes` se copia con `list(notes)`;
- `metadata` se copia con `dict(metadata)`;
- mutar la entrada del llamante no afecta al `EvidenceRecord`;
- mutar el `EvidenceRecord` no afecta a la entrada original.

### 8.5 NO_RUNTIME

- no toca `e2e_cli.py`;
- no despacha microservicios;
- no integra con Telegram/Hermes/Output Gateway;
- no modifica `storage.py` ni `intake.py`.

## 9. No-goals explícitos

- **No** persiste `EvidenceRecord` (eso es `SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE`).
- **No** calcula `content_hash` (lo conserva si el llamante lo provee).
- **No** infiere `mime_type`.
- **No** valida contenido de Excel/PDF.
- **No** marca `READY_FOR_ANALYSIS` en `IntakeRecord`.
- **No** implementa readiness gate.
- **No** crea loader YAML.
- **No** modifica runtime de diagnóstico.
- **No** asume `--classification auto` ni `--html-out`.

## 10. Tests

Archivo: `tests/smartpyme/test_evidence.py`

Cobertura mínima:

1. `test_create_evidence_record_minimal`
2. `test_to_dict_is_json_serializable`
3. `test_empty_tenant_id_raises`
4. `test_empty_intake_id_raises`
5. `test_empty_evidence_type_raises`
6. `test_empty_source_kind_raises`
7. `test_empty_source_ref_raises`
8. `test_invalid_source_kind_raises`
9. `test_invalid_status_raises`
10. `test_negative_size_bytes_raises`
11. `test_notes_must_be_list`
12. `test_metadata_must_be_dict`
13. `test_notes_are_copied_not_mutated`
14. `test_metadata_is_copied_not_mutated`
15. `test_request_id_optional`
16. `test_file_metadata_optional`
17. `test_uploaded_file_source_kind_allowed`
18. `test_manual_text_source_kind_allowed`
19. `test_external_ref_source_kind_allowed`
20. `test_import_smoke`

Más cobertura adicional:

- `test_allowed_statuses_cover_all_exports`
- `test_allowed_source_kinds_cover_all_exports`
- `test_status_can_be_overridden_to_registered`
- `test_evidence_id_is_unique_per_call`
- `test_received_at_is_iso_format`
- parametrizados de campos vacíos/whitespace
- `test_zero_size_bytes_allowed`
- `test_non_int_size_bytes_raises`
- `test_bool_size_bytes_raises`
- `test_generated_source_kind_allowed`
- `test_unknown_source_kind_allowed`

## 11. Próximo slice recomendado

**`SMARTPYME_EVIDENCE_STORAGE_PERSISTENCE`**

Objetivo:

- persistir `EvidenceRecord` en `<base_dir>/<tenant_id>/evidences.jsonl`;
- proveer `save_evidence_record`, `load_evidence_records`,
  `load_evidence_record_by_id`;
- mantener contrato fail-closed análogo al de
  `SMARTPYME_INTAKE_STORAGE_PERSISTENCE`.

Posteriormente:

1. `SMARTPYME_EVIDENCE_READINESS_GATE` — decidir si la evidencia satisface
   las requests del intake y transicionar `intake_state`.
2. `SMARTPYME_TANK_INTEGRATION_E2E` — integrar el flujo completo en CLI.

## 12. Relación con Git real

Implementado sobre HEAD:

```
9c80a7d test(smartpyme): harden intake storage persistence coverage
43bfcb0 feat(smartpyme): persist intake records by tenant
6fd315d feat(smartpyme): add intake record and evidence request slice
57ef4aa feat(smartpyme): add tank selection slice
```

Capacidades reales actuales:

- `excel_diagnostic`
- `supplier_duplicate_check`
- interrogation slice
- tank_selection slice
- intake slice
- intake storage persistence
- **evidence record contract (este slice)**

Capacidades NO implementadas (y que este slice NO asume):

- `--classification auto`
- `--html-out`
- `report_html.py`
- routing automático complejo
- YAML tank loader
- DomainPack ejecutable
- EvidenceRecord persistence
- readiness gate
- Telegram/Hermes/Output Gateway reales
