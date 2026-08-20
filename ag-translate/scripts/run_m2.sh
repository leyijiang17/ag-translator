#!/usr/bin/env bash
# Run a Macaulay2 script and capture its output.
#
# Usage: run_m2.sh <script.m2>
#
# Runs the given script in batch mode (no interactive prompts) and
# preserves Macaulay2's exit behavior. Like run_julia.sh, this is
# deliberately a thin wrapper — the pipeline re-runs the whole cumulative
# script each time rather than trying to keep M2 state alive across calls.

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <script.m2>" >&2
  exit 2
fi

SCRIPT="$1"

if ! command -v M2 >/dev/null 2>&1; then
  echo "ERROR: 'M2' not found on PATH. This script must be run in an environment with Macaulay2 installed." >&2
  exit 127
fi

if [ ! -f "$SCRIPT" ]; then
  echo "ERROR: script not found: $SCRIPT" >&2
  exit 2
fi

M2 --script "$SCRIPT"
exit $?
