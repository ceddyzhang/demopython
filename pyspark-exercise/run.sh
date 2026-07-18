#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
source ../.venv-wsl/bin/activate
python exercises.py
