# HASHLINE_HARNESS_POC_V1

## VERDICT

```text
STATUS: IMPLEMENTED_POC
SCOPE: LOCAL_SCRIPT_AND_TESTS
RUNTIME_PYMIA_LIVE_TOUCHED: NO
OPERATOR_SEMANTIC: NO
PURPOSE: fail-closed file edit harness primitive
```

## CONTEXT

The harness problem is that LLM coding performance depends heavily on the edit boundary.
Text replacement by exact old_text is brittle. A hash-addressed line edit can fail closed when the file changed after reading.

## IMPLEMENTED FILES

```text
scripts/hashline_editor.py
tests/test_hashline_editor.py
```

## CAPABILITIES

```text
1. Render a text file as hash-addressed physical lines.
2. Parse refs like LINE:HASH.
3. Replace one line only if line number and line hash still match.
4. Insert after one line only if line number and line hash still match.
5. Delete one line only if line number and line hash still match.
6. Fail closed on stale hash, invalid ref, or out-of-range line.
7. Expose a small CLI with view/edit/dry-run.
```

## SAFETY PROPERTIES

```text
- No LLM.
- No agent autonomy.
- No repo-wide mutation.
- No fuzzy patch.
- No old_text block matching.
- No silent write after stale read.
- One addressed line per operation.
```

## TEST RESULT

```text
python -m pytest tests/test_hashline_editor.py -q
8 passed in 0.26s
```

## USAGE EXAMPLES

View refs:

```bash
python scripts/hashline_editor.py view path/to/file.py
```

Dry-run replace:

```bash
python scripts/hashline_editor.py edit path/to/file.py replace 12:abcdef1234 --line "new content" --dry-run
```

Apply replace:

```bash
python scripts/hashline_editor.py edit path/to/file.py replace 12:abcdef1234 --line "new content"
```

## PYMIA RULE

```text
This is not an operator.
This is a deterministic edit boundary primitive.
It may be used by future MCP-local workflows only as a fail-closed helper.
```

## NEXT STEPS

```text
1. Do not wire it into autonomous runtime.
2. Keep it as local deterministic tooling.
3. Later, MCP-local may expose read_hashlines/apply_hashline_patch as first-class tools.
4. Every hashline edit must still be followed by diff and focal tests.
```
