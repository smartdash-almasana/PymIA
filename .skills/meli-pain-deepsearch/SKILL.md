---
name: meli-pain-deepsearch
description: "Trigger: dolores, cuellos de botella, vendedores Mercado Libre. Deepsearch externa triangulada R0-R2, sin diagnostico final."
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "0.1-draft"
---

# meli-pain-deepsearch

## Activation Contract

Activate when the user asks for pains, bottlenecks, or unsolved gaps for Mercado Libre sellers or store admins.
Do not activate for final diagnosis, pricing decisions, or productive pipeline changes. Without case reports, output is hypothesis only.

## Hard Rules

- Traceable evidence only: every claim carries source + date + link, 2024-2026 priority.
- One source equals weak signal. Three or more independent sources equal strong signal.
- Never average conflicting signals; mark the conflict and seek a primary source.
- PymIA does not guess: no diagnosis without case evidence. Mark NEEDS_EVIDENCE explicitly.
- Observational SHADOW_MODE only. Human decides before any promotion.

## Decision Gates

| Situation | Action |
|---|---|
| No real sellers available | External-only rounds R0-R2, hypothesis catalog, stop before diagnosis |
| Sellers plus ML/MP reports available | Hand off to meli-bottleneck-to-evidence for pathology bridge |
| Giant software already covers it | Mark covered with evidence, keep searching the uncovered remainder |
| Conflicting sources | Mark weak, request primary source, never merge numbers |

## Execution Steps

1. R0: fix boundaries and 3-5 pain hypotheses in seller language.
2. R1: search demand and friction in official ML docs, seller communities, forums, video, regulatory press.
3. R2: map giant-software coverage: generic billing, stock, and dashboards versus ML-specific layers.
4. Synthesize gaps with no working solution, each with strength rating and next verification action.

## Output Contract

Return a table: Pain | Who suffers | Evidence (source + date + link) | What giants cover | Unsolved gap | Strength (strong/weak) | Next action.
List weak signals separately. Close with 2-3 top candidates plus evidence gaps.

## References

- `../meli-bottleneck-to-evidence/SKILL.md` — converts strong pains into pathology candidates.
- `../../AGENTS.md` — method chain, PASS rules, and stop conditions.
