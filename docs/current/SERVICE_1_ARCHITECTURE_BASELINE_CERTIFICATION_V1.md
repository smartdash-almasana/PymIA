# SERVICE 1 ARCHITECTURE BASELINE CERTIFICATION V1

## Purpose

Provide one repeatable, automated certification command for the Servicio 1 architecture baseline. The certifier separates functional behavior from architectural convergence.

A green functional suite is necessary but is not sufficient for architectural certification.

## Command

Strict certification:

```powershell
python tools/service_1_architecture_baseline_v1.py
```

- exit code `0`: `PASS_ARCHITECTURE_BASELINE_V1`
- exit code `1`: `BLOCK_ARCHITECTURE_BASELINE_V1`

Report without failing the shell/CI step:

```powershell
python tools/service_1_architecture_baseline_v1.py --report-only
```

Machine-readable structural report:

```powershell
python tools/service_1_architecture_baseline_v1.py --report-only --skip-behavior --json
```

## Behavioral baseline

The certifier executes a curated set of existing real tests rather than creating a second testing framework:

- product pipeline: clean/owner-confirmed, ambiguous owner loop, invalid/incomplete inputs and governed computation plan;
- Package 1 Region/physical-evidence adapter, including provenance and adversarial invariants;
- PYME_011 productive-root path;
- REN_001 productive-root path.

These cover the intended architectural pressure points: clean usable evidence, ambiguity requiring owner input, incomplete/blocked evidence, and reuse across more than one pathology/capability.

## Structural acceptance rules

Certification requires all of the following:

1. exactly one canonical product root: `service_1_product_pipeline_v1`;
2. the Package 1 temporary adapter has zero productive importers;
3. no semantic rebinding after the P6 boundary;
4. P7 and P8 are not owned as one fused computation-plan boundary;
5. owner-question construction is not owned by the controlled-execution gate;
6. P6 does not perform P7 variable-family matching;
7. capability extension does not proliferate capability-specific branches in the product root.

The current branch-count threshold is `<= 2`. This is deliberately architectural: adding a pathology should primarily extend governed catalog/requirements/execution data, not create another mini-pipeline in the root.

## Current baseline at creation

Behavioral baseline: `PASS`.

Architecture verdict: `BLOCK_ARCHITECTURE_BASELINE_V1`.

Observed blockers:

- `NO_SEMANTIC_REBIND_AFTER_P6`
- `P7_P8_BOUNDARIES_NOT_FUSED`
- `OWNER_CONFIRMATION_NOT_OWNED_BY_CONTROLLED_EXECUTION_GATE`
- `P6_GATE_DOES_NOT_OWN_P7_FAMILY_MATCHING`
- `CAPABILITY_EXTENSION_WITHOUT_ROOT_BRANCH_PROLIFERATION`

At creation, the product root contains 14 `requested_capability == ...` branches. This is treated as convergence debt, not a functional failure.

## Governance

The certifier must not be weakened merely to make the verdict green. A rule may change only when the architecture authority changes explicitly and the replacement rule preserves the same product invariant.

The target closure verdict is:

`PASS_ARCHITECTURE_BASELINE_V1`

Once reached with the behavioral baseline passing, the Servicio 1 base architecture is considered frozen for ordinary capability expansion. Subsequent architectural changes require evidence from a real case that the frozen baseline cannot represent correctly.
