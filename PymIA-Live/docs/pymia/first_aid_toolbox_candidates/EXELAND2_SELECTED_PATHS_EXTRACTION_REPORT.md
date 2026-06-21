# EXELAND2 Selected Paths Extraction Report

## Scope of work
- **Source Paths Used**:
  - `formulas`: E:\BuenosPasos\exeland2\catalog\formulas.yaml
  - `templates`: E:\BuenosPasos\exeland2\warehouse\templates
  - `specs`: E:\BuenosPasos\exeland2\specs
- **Destination**: E:\BuenosPasos\smartbridge\PymIA\PymIA-Live\docs\pymia\first_aid_toolbox_candidates

## Metrics & Totals
- **Formulas Extracted**: 15
- **Templates Inventoried**: 13
- **Specs Extracted**: 14
- **Tool Candidates Created**: 14

## Created Artifacts
1. [EXELAND2_SELECTED_PATHS_EXTRACTION_REPORT.md](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/EXELAND2_SELECTED_PATHS_EXTRACTION_REPORT.md) - This summary report.
2. [exeland2_selected_paths_inventory.json](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/exeland2_selected_paths_inventory.json) - Complete JSON catalog of all extracted data.
3. [all_formula_refs_candidate.yaml](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/all_formula_refs_candidate.yaml) - Extracted formula structures.
4. [all_template_refs_candidate.yaml](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/all_template_refs_candidate.yaml) - Inventoried templates metadata.
5. [all_spec_refs_candidate.yaml](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/all_spec_refs_candidate.yaml) - Flattened spec definitions including sheets, fields, and bound formulas.
6. [all_tool_refs_candidate.yaml](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/all_tool_refs_candidate.yaml) - Mechanical tool candidate specifications.
7. [source_integrity_notes.md](file:///E:/BuenosPasos/smartbridge/PymIA/PymIA-Live/docs/pymia/first_aid_toolbox_candidates/source_integrity_notes.md) - Observations on potential overlaps and filename-slug inconsistencies.

## Integrity Observations
- auto_ganancia.yaml and caja_diaria.yaml: filename and slug may require later review. Both share the slug 'caja_diaria'.
- auto_stock.yaml and stock_control.yaml: possible overlap to review later.
- compras_y_proveedores.yaml: formula bindings may require semantic review later.

## Declarations & Confirmations
- **Filtering done**: NO (all formulas, templates, and specs from the source directories were included).
- **Activation decisions made**: NO (all items were set to `candidate_status: UNDECIDED` and `activation_status: NOT_DECIDED`).
- **Runtime touched**: NO (no changes made to `PymIA-Live/pymia/`, `pymia/`, or other executable files).
- **Files copied**: NO (xlsx files were only referenced and never copied).
- **Macros executed**: NO (no Excel operations were run).
