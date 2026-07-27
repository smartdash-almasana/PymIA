# SERVICE 1 — External Excel Tools and Gold Extraction V1

Status: `IMPLEMENTED_BOUNDED_ADOPTION`

## Purpose

Record the Excel-related external tools reviewed around the LobeHub ecosystem and extract only the practices that improve PymIA without creating a second XLSX authority, LLM runtime authority, or parallel product path.

## Architectural boundary

```text
P1-P9 business truth and computation
= PymIA canonical authorities only

P10 artifact QA / engineering laboratory
= may use external ideas and optional inspectors
```

External Excel tools must never become:

```text
canonical XLSX ingestion
semantic authority
P6 authority
P7 authority
P8 authority
business computation authority
runtime authorization
delivery authorization
```

## Tool inventory

| Tool / resource | Type | Value for PymIA | Decision | Gold extracted |
|---|---|---:|---|---|
| IgorWarzocha `excel` skill (`Opencode-Workflows`) | Agent skill | 9/10 | ADOPT PRINCIPLES | zero formula errors; no derived hardcodes when formulas are required; assumptions separated; mandatory verify-after-save loop; visual verification |
| BenchFlow `SkillsBench` + spreadsheet/xlsx task patterns | Benchmark + skill/task ecosystem | 9/10 | ADOPT METHOD | skills as instructions/scripts/resources; oracle/verifier task structure; adversarial spreadsheet task design; measurable verification |
| `xlsx-parsing` style skills / spreadsheet parsing playbooks | Agent skill pattern | 8/10 | TEST-IDEAS ONLY | multi-sheet, empty cells, merged cells, irregular headers, workbook-shape adversarial cases |
| `negokaz/excel-mcp-server` | MCP server | 9/10 | EXPERIMENTAL P10 INSPECTOR | read values/formulas/styles, list sheets, edit workbook, Windows live editing and screen capture; useful for external visual QA |
| `amanarneja/XSpreadsheet` | MCP server | 6/10 | DO NOT ADOPT NOW | broad CRUD/formula/formatting feature reference; redundant with chosen QA stack and lower maturity signal |
| LobeHub Excel Data Analysis Expert | Agent | 4/10 | DO NOT INTEGRATE | useful UX ideas around formula debugging, Power Query/VBA explanation, reproducible instructions; no deterministic authority value |
| LobeHub Excel Formula Master | Agent | 3/10 | DO NOT INTEGRATE | formula explanation and formula-design UX patterns; redundant with PymIA governed formula kernel |
| LobeHub Data Entry Clerk | Agent | 7/10 | ADOPT QA PATTERNS | deterministic normalization, arithmetic reconciliation, identifier validation, deduplication, anomaly reason codes, remediation, data-quality report, audit log |

## Source references

### IgorWarzocha excel skill

Repository/ecosystem reference:

```text
https://github.com/IgorWarzocha/Opencode-Workflows
https://agent-skills.md/skills/IgorWarzocha/Opencode-Workflows/excel
```

Observed useful rules:

```text
zero #REF! / #DIV/0! / #VALUE!
use formulas instead of hardcoded derived values when the workbook is a model
separate assumptions
mandatory recalculation/verification before delivery
visual verification
```

### BenchFlow SkillsBench

```text
https://github.com/benchflow-ai/skillsbench
```

Useful pattern:

```text
task
→ environment/skills
→ oracle
→ verifier
```

PymIA adoption: use this as inspiration for physical/adversarial XLSX corpora and objective pass/fail verification, not as a runtime parser.

### negokaz Excel MCP Server

```text
https://github.com/negokaz/excel-mcp-server
```

Useful capabilities:

```text
excel_describe_sheets
excel_read_sheet
showFormula
showStyle
excel_screen_capture (Windows)
excel_write_to_sheet
excel_create_table
excel_copy_sheet
```

PymIA policy: optional external P10 inspector only. It may inspect a delivered workbook but may never supply semantic evidence to P6/P7/P8.

### XSpreadsheet MCP

```text
https://github.com/amanarneja/XSpreadsheet
```

Observed scope includes read/write, worksheet management, formulas and formatting. It is not adopted because it overlaps heavily with existing Python/OpenPyXL tooling and the negokaz inspector experiment.

### LobeHub agents

```text
https://lobehub.com/agent/15tnol4r
https://lobehub.com/en/agent/excel-formula-master
https://lobehub.com/agent/1u87xwbv
```

These are treated as workflow/UX references only.

## Gold implemented in PymIA

### 1. Internal XLSX quality skill

```text
.skills/pymia-xlsx-quality/SKILL.md
```

Encodes the engineering workflow:

```text
build
→ save
→ deterministic QA
→ inspect failures
→ deliver only after PASS
```

### 2. Deterministic P10 XLSX quality gate

```text
pymia/smartpyme/service_1_xlsx_quality_gate_v1.py
```

Checks:

```text
file exists
valid XLSX ZIP/package
archive CRC integrity
openpyxl workbook readability
expected sheet coverage
formula-cell count
visible/cached Excel error cells
external-link count
macro archive presence
```

The QA result explicitly keeps:

```text
runtime_authorized = false
delivery_authorized = false
product_ready = false
```

Artifact QA is evidence about the file, not business truth.

### 3. Delivery integration

`service_1_xlsx_delivery_v1` runs the quality gate immediately after saving the workbook and fails closed if QA does not PASS.

### 4. Adversarial verification cases

Permanent tests include:

```text
valid workbook
corrupt ZIP disguised as XLSX
missing expected sheet
Excel #REF! error cell
valid workbook containing formula cells
```

Future corpus extensions should include:

```text
merged headers
irregular header rows
hidden sheets
cross-sheet formulas
large/wide sheets
empty-cell patterns
external links
formula-error caches
```

## What was deliberately NOT implemented

```text
no second XLSX parser
no direct MCP integration into Service 1 runtime
no LLM formula authority
no external skill dependency in production
no XSpreadsheet dependency
no automatic formula reconstruction
no business-result validation delegated to Excel
```

## MCP experiment registration

The negokaz inspector is registered in:

```text
.opencode/opencode.json
```

under:

```text
excel_qa
```

with:

```text
enabled = false
permission = ask
EXCEL_MCP_PAGING_CELLS_LIMIT = 4000
```

This is deliberate. The repository knows how to launch the inspector, but it does not start automatically and is not a product dependency.

When explicitly enabled on Windows, evaluate only:

```text
sheet inventory parity
formula visibility
style visibility
screen capture usefulness
large-sheet pagination
local-only handling
```

Acceptance condition:

```text
useful P10 observability without becoming a productive dependency
```

If that condition fails, remove the MCP experiment; the local deterministic quality gate remains sufficient for structural QA.
