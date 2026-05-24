# HERMES_LOCAL_INSTANCE_INVENTORY

Status: READ_ONLY_AUDIT
Owner: pending
Last-Updated: 2026-05-24

## Scope
Inventory of local Hermes-related instances and integration touchpoints used by PymIA.

## Runtime Endpoints
- MCP endpoint (primary): https://mcp.pymia.com.ar/mcp
- MCP endpoint (secondary): https://mcp2.pymia.com.ar/mcp

## Local Service Expectations
- Filesystem MCP server package: `pymia-filesystem-mcp`
- Transport: `streamable-http`
- Local bind: `127.0.0.1:8765`
- Cloudflare tunnel: named tunnel configured in local `cloudflared`

## Active Tooling Contract (Audit Baseline)
- list_tree(relative_path, max_entries)
- read_text_file(relative_path, max_bytes)
- search_text(pattern, relative_path, case_sensitive)
- git_status(repo_relative_path)
- git_log(repo_relative_path, limit)
- run_pytest(repo_relative_path)
- run_pymia_demo(message, repo_relative_path="PymIA")
- audit_docs_index(repo_relative_path="PymIA")
- check_forbidden_terms(repo_relative_path)
- create_text_file(relative_path, content)
- write_text_file(relative_path, content)
- patch_text_file(relative_path, old_text, new_text)
- create_directory(relative_path)
- copy_text_file(relative_path, target_relative_path)
- rename_text_file(relative_path, new_relative_path)
- list_large_file_head(relative_path, max_lines)

## Security Guardrails (Expected)
- Allowlist root: `E:\BuenosPasos\smartbridge`
- Denylist enforced for secrets/tokens/credentials and sensitive dirs
- No arbitrary shell exposure through filesystem MCP
- No delete/move recursive operations exposed
- No automatic push/commit required by audit workflow

## Current Audit Notes
- This file is created to satisfy documentary audit dependency.
- Values must be revalidated against live deployment before production decisions.

## Pending Verification Checklist
- [ ] Confirm endpoint reachability from ChatGPT connector
- [ ] Confirm endpoint reachability from Qwen connector
- [ ] Confirm schema parity between both connectors
- [ ] Confirm denylist blocks `.env` and token/secret-like files
- [ ] Confirm repo-scoped git/test tools operate on `PymIA`
