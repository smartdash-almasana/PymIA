#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install hermes-agent==0.14
./.venv/bin/python smoke_test.py

echo "BOOTSTRAP_OK"
