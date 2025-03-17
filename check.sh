#!/usr/bin/env bash
set -euo pipefail

uv run mypy .
uv run pylint hexsweeper/
