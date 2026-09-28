"""Service 1 — LLM direct semantic spike V1.

Measurement-only harness (spike). It compares the current deterministic
column-understanding baseline against a direct LLM interpreter on the same
in-memory corpus, without touching the productive root.

Rules honored:
- Reuses build_default_service_1_column_understanding_corpus_v1() as source.
- Does NOT create a second XLSX parser.
- Does NOT add embeddings, rules or aliases.
- Does NOT touch P6/P7/P8, kernel, delivery or the product root.
- The LLM receives ONLY: business scenario, sheet, column, type, samples,
  neighbor columns and allowed roles. Ground truth is never sent.
- Output per column: semantic_role | unknown, needs_owner_confirmation,
  owner_question | null.
- On doubt the model must abstain (unknown/null role) and ask for
  confirmation; declared confidence is never used as authority.

Runtime: PydanticAI + Google Vertex AI (Gemini), using typed structured output.
No OpenCode, no OpenRouter, no credential inspection.

Metrics reuse the existing corpus evaluator outcome taxonomy so the comparison
is apples-to-apples: EXACT_MATCH / SAFE_QUESTION / SAFE_UNKNOWN /
FALSE_CONFIDENT / MISSED_QUESTION, and dangerous_errors on dangerous columns.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict
from pydantic_ai import Agent
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google_cloud import GoogleCloudProvider

from pymia.smartpyme.service_1_column_understanding_corpus_evaluation_v1 import (
    OUTCOME_EXACT_MATCH,
    OUTCOME_FALSE_CONFIDENT,
    OUTCOME_MISSED_QUESTION,
    OUTCOME_SAFE_QUESTION,
    OUTCOME_SAFE_UNKNOWN,
    ROLE_UNKNOWN,
    Service1ColumnUnderstandingCorpusCaseV1,
    Service1ColumnUnderstandingCorpusColumnV1,
    build_default_service_1_column_understanding_corpus_v1,
    evaluate_service_1_column_understanding_corpus_v1,
    _classify_outcome,
)
from pymia.smartpyme.service_1_column_understanding_engine_v1 import _ROLE_RULES

SPIKE_SCHEMA_VERSION = "SERVICE_1_LLM_SEMANTIC_SPIKE_V1"
MODEL = os.getenv("PYDANTIC_AI_VERTEX_MODEL", "gemini-2.5-flash")
RUNTIME = "pydantic_ai_vertex"


class LLMColumnDecisionV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    column_name: str
    semantic_role: str | None = None
    variable_name: str | None = None
    needs_owner_confirmation: bool
    owner_question: str | None = None


class LLMCaseDecisionBatchV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisions: list[LLMColumnDecisionV1]


def _build_agent() -> Agent[None, LLMCaseDecisionBatchV1]:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ["GOOGLE_CLOUD_LOCATION"]
    model = GoogleModel(
        MODEL,
        provider=GoogleCloudProvider(project=project, location=location),
    )
    return Agent(
        model,
        output_type=LLMCaseDecisionBatchV1,
        instructions=(
            "Interpret business semantics of already-profiled spreadsheet columns. "
            "Do not calculate business results. Use only allowed roles and variables. "
            "If meaning is materially ambiguous, abstain with semantic_role=null, "
            "variable_name=null, needs_owner_confirmation=true, and ask one concise "
            "business question. Return exactly one decision for every supplied column."
        ),
    )


_AGENT: Agent[None, LLMCaseDecisionBatchV1] | None = None


def _agent() -> Agent[None, LLMCaseDecisionBatchV1]:
    global _AGENT
    if _AGENT is None:
        _AGENT = _build_agent()
    return _AGENT


ALLOWED_ROLES: tuple[str, ...] = tuple(
    sorted({rule.semantic_role for rule in _ROLE_RULES})
)
ALLOWED_VARIABLES: tuple[str, ...] = tuple(
    sorted({rule.variable_name for rule in _ROLE_RULES})
)


def _neighbor_columns(
    case: Service1ColumnUnderstandingCorpusCaseV1,
    column: Service1ColumnUnderstandingCorpusColumnV1,
) -> list[str]:
    return [
        other.column_name
        for other in case.columns
        if other.column_name != column.column_name
    ]


def build_llm_prompt(case: Service1ColumnUnderstandingCorpusCaseV1) -> str:
    payload = {
        "business_scenario": case.business_scenario,
        "sheet_name": case.sheet_name,
        "allowed_semantic_roles": ALLOWED_ROLES,
        "allowed_variables": ALLOWED_VARIABLES,
        "columns": [
            {
                "column_name": column.column_name,
                "inferred_type": column.inferred_type,
                "sample_values": list(column.sample_values),
                "neighbor_columns": _neighbor_columns(case, column),
            }
            for column in case.columns
        ],
    }
    return json.dumps(payload, ensure_ascii=False, default=str)


def run_llm_case_interpretation(
    case: Service1ColumnUnderstandingCorpusCaseV1,
) -> tuple[list[dict[str, Any]] | None, str | None]:
    """One typed PydanticAI/Vertex call per corpus case."""
    try:
        result = _agent().run_sync(build_llm_prompt(case))
        batch = result.output
    except Exception as exc:  # noqa: BLE001 - experimental runtime boundary
        return None, f"{type(exc).__name__}: {exc}"

    by_name = {decision.column_name: decision for decision in batch.decisions}
    missing = [column.column_name for column in case.columns if column.column_name not in by_name]
    extras = [name for name in by_name if name not in {column.column_name for column in case.columns}]
    if missing or extras or len(batch.decisions) != len(case.columns):
        return None, f"typed output mismatch missing={missing} extras={extras} count={len(batch.decisions)}"

    predictions = [by_name[column.column_name].model_dump() for column in case.columns]
    return predictions, None


def classify_llm_row(
    expected: Service1ColumnUnderstandingCorpusColumnV1,
    prediction: dict[str, Any],
) -> tuple[str, str, str, bool]:
    role = str(prediction.get("semantic_role") or ROLE_UNKNOWN).strip() or ROLE_UNKNOWN
    variable = str(prediction.get("variable_name") or ROLE_UNKNOWN).strip() or ROLE_UNKNOWN
    needs_confirmation = bool(prediction.get("needs_owner_confirmation"))
    outcome = _classify_outcome(
        expected=expected,
        predicted_role=role,
        predicted_variable=variable,
        owner_question_needed=needs_confirmation,
    )
    return outcome, role, variable, needs_confirmation


def aggregate(outcomes: list[str], dangerous_flags: list[bool]) -> dict[str, Any]:
    counts = {name: outcomes.count(name) for name in (
        OUTCOME_EXACT_MATCH,
        OUTCOME_SAFE_QUESTION,
        OUTCOME_SAFE_UNKNOWN,
        OUTCOME_FALSE_CONFIDENT,
        OUTCOME_MISSED_QUESTION,
    )}
    total = len(outcomes) or 1
    dangerous_errors = sum(
        1
        for outcome, dangerous in zip(outcomes, dangerous_flags)
        if dangerous and outcome in {OUTCOME_FALSE_CONFIDENT, OUTCOME_MISSED_QUESTION}
    )
    return {
        "columns_count": len(outcomes),
        "exact_matches": counts[OUTCOME_EXACT_MATCH],
        "safe_questions": counts[OUTCOME_SAFE_QUESTION],
        "safe_unknowns": counts[OUTCOME_SAFE_UNKNOWN],
        "false_confident": counts[OUTCOME_FALSE_CONFIDENT],
        "missed_questions": counts[OUTCOME_MISSED_QUESTION],
        "dangerous_errors": dangerous_errors,
        "exact_match_rate": round(counts[OUTCOME_EXACT_MATCH] / total, 4),
    }


def run_llm_direct(corpus: tuple[Service1ColumnUnderstandingCorpusCaseV1, ...]) -> dict[str, Any]:
    outcomes: list[str] = []
    dangerous_flags: list[bool] = []
    rows: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for case in corpus:
        predictions, raw = run_llm_case_interpretation(case)
        if predictions is None:
            invalid.append(
                {
                    "case_id": case.case_id,
                    "status": "MODEL_OUTPUT_INVALID",
                    "response_excerpt": (raw or "")[:300],
                }
            )
            continue
        for column, prediction in zip(case.columns, predictions):
            outcome, role, variable, needs_confirmation = classify_llm_row(column, prediction)
            outcomes.append(outcome)
            dangerous_flags.append(column.dangerous_if_wrong)
            rows.append(
                {
                    "case_id": case.case_id,
                    "sheet_name": case.sheet_name,
                    "column_name": column.column_name,
                    "expected_semantic_role": column.expected_semantic_role,
                    "expected_variable_name": column.expected_variable_name,
                    "predicted_semantic_role": role,
                    "predicted_variable_name": variable,
                    "needs_owner_confirmation": needs_confirmation,
                    "owner_question": prediction.get("owner_question"),
                    "outcome": outcome,
                    "dangerous_if_wrong": column.dangerous_if_wrong,
                }
            )
    metrics = aggregate(outcomes, dangerous_flags)
    return {**metrics, "rows": rows, "model_output_invalid": invalid}


def decide(llm: dict[str, Any], baseline: dict[str, Any]) -> str:
    if llm["false_confident"] > baseline["false_confident"]:
        return "LLM_DIRECT_NOT_GOOD_ENOUGH"
    if llm["dangerous_errors"] > baseline["dangerous_errors"]:
        return "LLM_DIRECT_NOT_GOOD_ENOUGH"
    if llm["missed_questions"] > baseline["missed_questions"]:
        return "LLM_DIRECT_NOT_GOOD_ENOUGH"
    if llm["exact_match_rate"] < baseline["exact_match_rate"]:
        return "LLM_DIRECT_NOT_GOOD_ENOUGH"
    if llm["false_confident"] == 0 and llm["dangerous_errors"] == 0:
        return "LLM_DIRECT_PROMISING"
    return "LLM_DIRECT_NOT_GOOD_ENOUGH"


def _report_path(case_id: str) -> Path:
    suffix = f"_{case_id}" if case_id else ""
    return Path(__file__).resolve().parent / f"service_1_llm_semantic_spike_report_v1{suffix}.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-id", default="")
    args = parser.parse_args()

    full_corpus = build_default_service_1_column_understanding_corpus_v1()
    corpus = full_corpus
    if args.case_id:
        corpus = tuple(case for case in full_corpus if case.case_id == args.case_id)
        if not corpus:
            raise ValueError(f"unknown case_id: {args.case_id}")

    baseline_eval = evaluate_service_1_column_understanding_corpus_v1(corpus)
    baseline = {
        "columns_count": baseline_eval.columns_count,
        "exact_matches": baseline_eval.exact_matches,
        "safe_questions": baseline_eval.safe_questions,
        "safe_unknowns": baseline_eval.safe_unknowns,
        "false_confident": baseline_eval.false_confident,
        "missed_questions": baseline_eval.missed_questions,
        "dangerous_errors": baseline_eval.dangerous_errors,
        "exact_match_rate": baseline_eval.exact_match_rate,
    }

    print("=== BASELINE (deterministic engine) ===")
    print(json.dumps(baseline, ensure_ascii=False, indent=2))

    print(f"\n=== LLM DIRECT (PydanticAI/Vertex/{MODEL}) ===")
    llm = run_llm_direct(corpus)
    invalid = llm.get("model_output_invalid", [])
    print(json.dumps({k: v for k, v in llm.items() if k not in {"rows", "model_output_invalid"}}, ensure_ascii=False, indent=2))
    if invalid:
        print("\n=== MODEL_OUTPUT_INVALID CASES ===")
        for entry in invalid:
            print(f"- {entry['case_id']}: {entry['response_excerpt']}")

    decision = decide(llm, baseline)
    print("\n=== DECISION ===")
    print(decision)

    report = {
        "schema_version": SPIKE_SCHEMA_VERSION,
        "model": MODEL,
        "runtime": RUNTIME,
        "baseline": baseline,
        "llm_direct": llm,
        "decision": decision,
    }
    out = _report_path(args.case_id)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nreport written: {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - spike harness boundary
        print(f"SPIKE_ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
