#!/usr/bin/env bash
# VolGuard AI - one-click backend launcher (macOS / Linux).
# Usage: ./run_server.sh [--reload] [--port 8000]
set -e
cd "$(dirname "$0")"

PORT="${PORT:-8000}"
RELOAD=""
while [ $# -gt 0 ]; do
  case "$1" in
    --reload) RELOAD="--reload" ;;
    --port) PORT="$2"; shift ;;
  esac
  shift
done

PY="$(command -v python3 || command -v python || true)"
[ -z "$PY" ] && { echo "[VolGuard] Python 3.10+ not found. Install it first."; exit 1; }

# 1. virtual environment (reuse .venv / ../.venv / venv, else create backend/.venv)
VENV=""
for d in .venv ../.venv venv ../venv; do
  [ -f "$d/bin/activate" ] && VENV="$d" && break
done
if [ -z "$VENV" ]; then
  echo "[VolGuard] Creating virtual environment .venv ..."
  "$PY" -m venv .venv
  VENV=".venv"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"

# 2. dependencies
if ! python -c "import fastapi, uvicorn, pandas, numpy, arch, yfinance" >/dev/null 2>&1; then
  echo "[VolGuard] Installing dependencies ..."
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r requirements.txt
fi

# 3. offline mode: respect user setting, otherwise auto-detect Yahoo reachability
if [ -z "${VOLGUARD_OFFLINE:-}" ]; then
  if python -c "import socket; socket.create_connection(('query1.finance.yahoo.com', 443), 3).close()" >/dev/null 2>&1; then
    export VOLGUARD_OFFLINE=0
    echo "[VolGuard] Yahoo Finance reachable: live data with CSV fallback."
  else
    export VOLGUARD_OFFLINE=1
    echo "[VolGuard] Yahoo Finance unreachable: using bundled offline CSV."
  fi
fi

# 4. port check
if python -c "import socket,sys; s=socket.socket(); sys.exit(0 if s.connect_ex(('127.0.0.1', $PORT))==0 else 1)"; then
  echo "[VolGuard] Port $PORT already in use. Stop the other process or run: PORT=8001 ./run_server.sh"
  exit 1
fi

echo "[VolGuard] API:  http://localhost:$PORT   Docs: http://localhost:$PORT/docs"
exec python -m uvicorn api:app --host 0.0.0.0 --port "$PORT" $RELOAD
