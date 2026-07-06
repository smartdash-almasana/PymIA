from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Sequence

HashlineOperation = Literal["replace", "insert_after", "delete"]


class HashlineEditError(ValueError):
    """Raised when a hashline edit cannot be applied safely."""


@dataclass(frozen=True)
class HashlineRef:
    line_number: int
    line_hash: str


def line_hash(line: str) -> str:
    """Return a short stable hash for one physical line including its newline if present."""
    return hashlib.sha256(line.encode("utf-8")).hexdigest()[:10]


def split_lines(text: str) -> list[str]:
    """Split text preserving line endings; represent empty files as an empty list."""
    return text.splitlines(keepends=True)


def render_hashlines(text: str) -> str:
    """Render text as line-numbered, hash-addressable lines.

    Format:
        0001:<hash> <line content without trailing newline marker>

    The hash is computed over the exact physical line, including the newline byte
    sequence when present. This allows a later edit to fail closed if the file
    changed after reading.
    """
    rendered: list[str] = []
    for index, line in enumerate(split_lines(text), start=1):
        visible = line.rstrip("\r\n")
        rendered.append(f"{index:04d}:{line_hash(line)} {visible}")
    return "\n".join(rendered)


def parse_ref(value: str) -> HashlineRef:
    """Parse refs like '12:abc123def0' or '0012:abc123def0'."""
    raw_line, sep, raw_hash = value.partition(":")
    if sep != ":" or not raw_line.strip() or not raw_hash.strip():
        raise HashlineEditError("hashline_ref_must_be_LINE:HASH")
    try:
        line_number = int(raw_line)
    except ValueError as exc:
        raise HashlineEditError("hashline_line_number_must_be_integer") from exc
    if line_number < 1:
        raise HashlineEditError("hashline_line_number_must_be_positive")
    cleaned_hash = raw_hash.strip()
    if len(cleaned_hash) != 10 or any(char not in "0123456789abcdef" for char in cleaned_hash):
        raise HashlineEditError("hashline_hash_must_be_10_lower_hex_chars")
    return HashlineRef(line_number=line_number, line_hash=cleaned_hash)


def _line_at(lines: Sequence[str], ref: HashlineRef) -> str:
    index = ref.line_number - 1
    if index >= len(lines):
        raise HashlineEditError("hashline_ref_out_of_range")
    current_line = lines[index]
    current_hash = line_hash(current_line)
    if current_hash != ref.line_hash:
        raise HashlineEditError("hashline_ref_hash_mismatch")
    return current_line


def _normalize_new_line(value: str) -> str:
    return value if value.endswith(("\n", "\r\n")) else value + "\n"


def replace_line(text: str, ref: HashlineRef, new_line: str) -> str:
    lines = split_lines(text)
    _line_at(lines, ref)
    lines[ref.line_number - 1] = _normalize_new_line(new_line)
    return "".join(lines)


def insert_after(text: str, ref: HashlineRef, new_line: str) -> str:
    lines = split_lines(text)
    _line_at(lines, ref)
    lines.insert(ref.line_number, _normalize_new_line(new_line))
    return "".join(lines)


def delete_line(text: str, ref: HashlineRef) -> str:
    lines = split_lines(text)
    _line_at(lines, ref)
    del lines[ref.line_number - 1]
    return "".join(lines)


def apply_hashline_edit(
    *,
    text: str,
    operation: HashlineOperation,
    ref: HashlineRef,
    new_line: str | None = None,
) -> str:
    if operation == "replace":
        if new_line is None:
            raise HashlineEditError("replace_requires_new_line")
        return replace_line(text, ref, new_line)
    if operation == "insert_after":
        if new_line is None:
            raise HashlineEditError("insert_after_requires_new_line")
        return insert_after(text, ref, new_line)
    if operation == "delete":
        return delete_line(text, ref)
    raise HashlineEditError("unsupported_hashline_operation")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fail-closed hashline file viewer/editor.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    view = subparsers.add_parser("view", help="Print file with hashline refs.")
    view.add_argument("path")

    edit = subparsers.add_parser("edit", help="Apply one hashline edit to a file.")
    edit.add_argument("path")
    edit.add_argument("operation", choices=["replace", "insert_after", "delete"])
    edit.add_argument("ref", help="LINE:HASH, e.g. 12:abc123def0")
    edit.add_argument("--line", default=None, help="New line for replace/insert_after.")
    edit.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    path = Path(args.path)
    text = path.read_text(encoding="utf-8")

    if args.command == "view":
        print(render_hashlines(text))
        return 0

    ref = parse_ref(args.ref)
    updated = apply_hashline_edit(
        text=text,
        operation=args.operation,
        ref=ref,
        new_line=args.line,
    )
    if args.dry_run:
        print(updated, end="")
        return 0
    path.write_text(updated, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
