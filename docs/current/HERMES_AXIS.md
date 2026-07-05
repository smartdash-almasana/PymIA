# HERMES_AXIS

## STATUS

```text
CANONICAL_SUBINDEX_CREATED
HERMES_AXIS_STATUS: SEPARATED_FROM_PYMIA_RUNTIME_AUTHORITY
CODE_AUTHORITY: NO
```

## PURPOSE

This file separates Hermes orchestration, gateway, MCP, SCN, sandbox, VM and historical protocol documents from PymIA kernel and Service 1 implementation authority.

Hermes may act as orchestration / HITL / conversational gateway only under explicit contracts and validated gates.
It must not become PymIA's computational authority.

## GOVERNING PRINCIPLE

```text
Hermes may communicate or orchestrate.
PymIA computes.
PymIA contracts validate.
Owner confirms.
```

## CURRENT HERMES DOC CLASSES

```text
Hermes architecture/boundary docs
Hermes VM and sandbox audits
Hermes MCP validation docs
SCN boundary docs
Hermes historical protocols
Hermes local command guides
```

## ACTIVE CAUTION

```text
Do not use Hermes historical docs to authorize runtime.
Do not use Hermes as source of diagnosis.
Do not enable Telegram/productive channel from archived or candidate docs.
Do not treat MCP-1/MCP-2 sandbox success as MCP-3/productive authorization.
Do not let Hermes render new findings or alter OperationalAuditResult.
```

## CANONICAL REFERENCES TO PRESERVE

```text
docs/adr/ADR-008-hermes-mcp-client-pymia-mcp-server.md
docs/hermes/principio-obligatorio-hermes-runtime-orchestrator.md
docs/hermes/boundary-integracion-conversacional.md
docs/arquitectura/orchestration-boundary.md
docs/arquitectura/SCN_001_SOVEREIGN_COMPUTATION_BOUNDARY.md
docs/arquitectura/SCN_002_CONTRACT_VALIDATION_LAYER_DESIGN.md
```

## NON_GOVERNING_HERMES_DOCS

```text
ARCHIVO Hermes protocols
historical incident docs
local command guides
sandbox-only results
candidate integration notes without explicit approval
```

## OPEN GAP

```text
Hermes has many valid historical and sandbox documents.
They need preservation as evidence, but must not guide Service 1 runtime or product commitments.
```

## NEXT SAFE FRONT

```text
HERMES_AXIS_CANONICALIZATION_AUDIT_V1
AUDIT ONLY
```

## FINAL_STATUS

```text
HERMES_AXIS: CREATED
CODE_CHANGE_AUTHORIZED: NO
```
