# PymIA Hybrid Intelligence Governance V1

**Status:** architectural design authority; does not authorize runtime capabilities by itself.

## Purpose

Preserve the architectural lessons extracted from the study of `alosno-dev/aplicacion-ia-a-procesos-administrativos-y-logisticos-en-pymes` and adapt them to PymIA without copying its implementation.

The central conclusion is that PymIA must not treat an LLM as the generic intelligence layer of the system. Different classes of uncertainty require different mechanisms.

## Governing principle

> PymIA should use the minimum mechanism capable of resolving each uncertainty with evidence, limits and traceability.

The preferred resolution order is:

```text
evidence
→ extraction
→ deterministic validation
→ specialized classification
→ contextual LLM only when ambiguity remains
→ human confirmation when uncertainty persists
→ deterministic calculation / controlled execution
```

A model output is never equivalent to confirmed business truth by itself.

## 1. Perception is not truth

For document-oriented inputs the reference architecture separates:

```text
physical evidence
≠ extracted text
≠ structured candidate data
≠ confirmed business fact
```

OCR, layout analysis and multimodal extraction may produce candidate evidence. PymIA must preserve provenance and allow validation before any downstream accounting, financial or operational conclusion.

## 2. Deterministic rules before semantic escalation

When information can be checked through explicit invariants, PymIA should prefer deterministic mechanisms such as:

- required-field checks;
- arithmetic identities and tolerances;
- duplicate detection;
- row/column consistency;
- date and state constraints;
- scope and identity validation;
- reconciliation rules.

The LLM must not bypass a deterministic validation layer that can resolve the same question more reliably.

## 3. Specialized models for narrow recurring problems

Not every semantic task requires a general-purpose LLM.

For narrow, repetitive classification problems PymIA may use specialized classifiers combining structured features and semantic representations.

Decision rule:

```text
narrow and repetitive pattern
→ specialized classifier

contextual ambiguity
→ controlled LLM
```

This reduces cost, latency, provider dependence and output variability.

## 4. LLM as contextual resolution, not authority

The LLM is reserved for ambiguity that remains after extraction, validation and classification.

Allowed conceptual role:

- interpret uncertain field meaning;
- resolve context among bounded candidates;
- explain results;
- translate owner intent into candidate structured meaning;
- support conversation around already governed facts.

The LLM must not directly establish accounting truth, financial truth, execution authority or irreversible actions.

Preferred escalation:

```text
clear case
→ deterministic resolution

ambiguous case
→ LLM candidate interpretation

persistent ambiguity
→ human confirmation
```

## 5. Prediction, optimization and explanation are separate responsibilities

The reference study separates demand forecasting from schedule optimization. PymIA adopts the same architectural principle.

```text
predictive model
→ estimates future state

optimization engine
→ selects a feasible solution under explicit constraints

LLM
→ explains or contextualizes the result
```

Prediction does not authorize a decision. Optimization does not invent constraints. Explanation does not modify the result.

This pattern can later apply to:

- replenishment;
- purchases;
- cash planning;
- production capacity;
- staffing;
- routes;
- pricing under constraints.

## 6. Human escalation is a first-class mechanism

Human confirmation is not a failure mode. It is the terminal resolution mechanism for uncertainty that cannot be safely resolved automatically.

PymIA should make uncertainty explicit and escalate only the unresolved portion.

```text
machine resolves what is certain
→ machine narrows what is ambiguous
→ owner confirms only what remains uncertain
```

This is the basis for a mayeutic interaction model.

## 7. Conversation and tool use must remain governed

A future conversational or agentic layer may:

```text
conversation
→ identify intent
→ query governed state
→ request an authorized tool
→ record execution
→ respond with evidence
```

The conversational model does not become the source of state, the business rule engine or the authorization boundary.

External orchestrators, event buses or automation frameworks may be adapters, never the business authority of PymIA.

## 8. Knowledge bank implications

The PymIA knowledge bank should evolve beyond formulas and pathologies. It should be able to classify knowledge by mechanism, for example:

```text
DETERMINISTIC
CLASSIFICATION
PREDICTION
OPTIMIZATION
SEMANTIC_RESOLUTION
HUMAN_CONFIRMATION
```

Candidate organizational families include:

```text
business_knowledge/
  formulas/
  reconciliations/
  controls/
  constraints/
  classifiers/
  prediction_models/
  optimization_models/
  semantic_resolution/
```

This document does not require those directories to exist immediately; they express the intended knowledge taxonomy.

## 9. Service 1 implication

The current Service 1 productive root remains governed by its existing deterministic contracts and authorization gates.

Near-term Service 1 should continue prioritizing:

```text
structured evidence
→ normalization
→ reconciliation
→ controls
→ deterministic calculation
```

The architectural value of this document is to prevent future AI integration from forcing a redesign of those guarantees.

## 10. Non-goals

This document does not authorize:

- introducing an LLM into the current Service 1 runtime;
- OCR/PDF ingestion into the current productive path;
- replacing deterministic calculations with model outputs;
- autonomous financial or fiscal decisions;
- automatic write actions without explicit authorization;
- copying code from the reference repository.

## Source-derived architectural lesson

The reference project is a modular academic prototype combining document perception, deterministic rules, a specialized classifier, contextual LLM use, predictive modeling, mathematical optimization and human involvement.

PymIA adopts the architectural lesson, not the implementation:

> intelligent systems for SMEs should compose specialized mechanisms according to the type of uncertainty instead of delegating perception, prediction, decision and explanation to one general-purpose model.
