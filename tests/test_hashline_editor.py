from __future__ import annotations

import pytest

from scripts.hashline_editor import (
    HashlineEditError,
    apply_hashline_edit,
    line_hash,
    parse_ref,
    render_hashlines,
)


def _ref_for(text: str, line_number: int) -> str:
    line = text.splitlines(keepends=True)[line_number - 1]
    return f"{line_number}:{line_hash(line)}"


def test_render_hashlines_includes_line_numbers_and_hashes() -> None:
    text = "alpha\nbeta\n"

    rendered = render_hashlines(text)

    assert "0001:" in rendered
    assert " alpha" in rendered
    assert "0002:" in rendered
    assert " beta" in rendered


def test_replace_line_succeeds_when_hash_matches() -> None:
    text = "alpha\nbeta\ngamma\n"

    updated = apply_hashline_edit(
        text=text,
        operation="replace",
        ref=parse_ref(_ref_for(text, 2)),
        new_line="BETA",
    )

    assert updated == "alpha\nBETA\ngamma\n"


def test_insert_after_succeeds_when_hash_matches() -> None:
    text = "alpha\nbeta\n"

    updated = apply_hashline_edit(
        text=text,
        operation="insert_after",
        ref=parse_ref(_ref_for(text, 1)),
        new_line="inserted",
    )

    assert updated == "alpha\ninserted\nbeta\n"


def test_delete_line_succeeds_when_hash_matches() -> None:
    text = "alpha\nbeta\ngamma\n"

    updated = apply_hashline_edit(
        text=text,
        operation="delete",
        ref=parse_ref(_ref_for(text, 2)),
    )

    assert updated == "alpha\ngamma\n"


def test_edit_fails_closed_when_hash_does_not_match() -> None:
    text = "alpha\nbeta\n"
    stale_ref = parse_ref(f"2:{line_hash('old beta\n')}")

    with pytest.raises(HashlineEditError, match="hash_mismatch"):
        apply_hashline_edit(
            text=text,
            operation="replace",
            ref=stale_ref,
            new_line="BETA",
        )


def test_edit_fails_closed_when_ref_is_out_of_range() -> None:
    text = "alpha\n"

    with pytest.raises(HashlineEditError, match="out_of_range"):
        apply_hashline_edit(
            text=text,
            operation="delete",
            ref=parse_ref(f"2:{line_hash('missing\n')}"),
        )


def test_parse_ref_rejects_invalid_shape() -> None:
    with pytest.raises(HashlineEditError):
        parse_ref("not-a-ref")


def test_replace_requires_new_line() -> None:
    text = "alpha\n"

    with pytest.raises(HashlineEditError, match="replace_requires_new_line"):
        apply_hashline_edit(
            text=text,
            operation="replace",
            ref=parse_ref(_ref_for(text, 1)),
        )
