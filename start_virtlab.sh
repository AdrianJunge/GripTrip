#!/usr/bin/env bash
set -euo pipefail

export VIRT_LAB_DB="1"

venv_dir="/tmp/test_env_$(python3 --version 2>&1)"

if [ ! -d "$venv_dir" ]; then
    echo "Virtual environment not found — creating one..."
    python3 -m venv "$venv_dir"
else
    echo "Virtual environment already exists — reusing it."
fi

source "$venv_dir/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
python3 init_db.py

echo "Starting Flask (debug) — if you want this to run in background, run it separately."
flask --debug --app=server run
