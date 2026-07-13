from __future__ import annotations

import json
from pathlib import Path

from .bem_schema_builder import BemSchemaBuilder
from .excel_profile_builder import ExcelProfileBuilder
from .owner_questions_builder import OwnerQuestionsBuilder


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run(excel_path: str | Path) -> dict[str, str]:
    input_path = Path(excel_path).resolve()
    stem = input_path.stem

    profile_builder = ExcelProfileBuilder()
    questions_builder = OwnerQuestionsBuilder()
    schema_builder = BemSchemaBuilder()

    profile = profile_builder.build_profile(input_path)
    profile_payload = profile.to_dict()
    owner_questions = questions_builder.build(profile)
    candidate_schema = schema_builder.build_candidate_schema(profile, owner_questions)

    root = _repo_root()
    profile_path = root / "docs" / "bem_profiles" / f"{stem}.profile.json"
    questions_path = root / "docs" / "bem_profiles" / f"{stem}.owner_questions.json"
    schema_path = root / "docs" / "bem_schemas" / f"{stem}.bem_output_schema.json"

    _write_json(profile_path, profile_payload)
    _write_json(questions_path, owner_questions)
    _write_json(schema_path, candidate_schema)

    return {
        "profile": str(profile_path),
        "owner_questions": str(questions_path),
        "bem_schema": str(schema_path),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Build auditable BEM schema artifacts from complex Excel files")
    parser.add_argument("excel_path", help="Path to .xlsx file")
    args = parser.parse_args()

    outputs = run(args.excel_path)
    print(json.dumps(outputs, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
