#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNTIME=""

if command -v podman >/dev/null 2>&1; then
  RUNTIME="podman"
elif command -v docker >/dev/null 2>&1; then
  RUNTIME="docker"
else
  echo "Neither podman nor docker found" >&2
  exit 1
fi

echo "[isfna] container runtime: $RUNTIME"

echo "[isfna] Stage 1: isfna-only smoke"
"$RUNTIME" run --rm -v "$ROOT_DIR:/work" -w /work python:3.12-slim bash -lc '
python -m pip install -q --upgrade pip
python -m pip install -q -e .
python -m py_compile src/isfna/*.py
isfna detect
isfna prompt pi --repo .
isfna init pi --repo . --dry-run
'

echo "[isfna] Stage 2: pi + isfna integration smoke"
"$RUNTIME" run --rm -v "$ROOT_DIR:/work" -w /work node:20-slim bash -lc '
apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv >/dev/null
npm -g i @mariozechner/pi-coding-agent >/dev/null
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -q -U pip
python -m pip install -q -e .
pi --version
isfna init pi --repo .
find /root/.pi/agent/skills -maxdepth 2 -name SKILL.md | sort
'

echo "[isfna] ✅ container smoke passed"
