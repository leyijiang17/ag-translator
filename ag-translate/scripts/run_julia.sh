#!/usr/bin/env bash
# Run a Julia/OSCAR script and capture its output.
#
# Usage: run_julia.sh <script.jl>
#
# Runs the given script with `julia`, printing stdout and stderr, and
# preserving julia's exit code. The script itself is responsible for
# `using Oscar` and any needed `using Pkg; Pkg.add(...)` — this wrapper
# doesn't inject anything, so what you run here is exactly what a user
# would get running the file themselves.
#
# Kept deliberately dumb (just `julia file.jl`) rather than trying to pipe
# commands into a persistent REPL: the pipeline design runs a *cumulative*
# script each time (see SKILL.md step 6), so there's no need for
# session/state management at this layer.

set -uo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <script.jl>" >&2
  exit 2
fi

SCRIPT="$1"

if ! command -v julia >/dev/null 2>&1; then
  echo "ERROR: 'julia' not found on PATH. This script must be run in an environment with Julia and OSCAR.jl installed." >&2
  exit 127
fi

if [ ! -f "$SCRIPT" ]; then
  echo "ERROR: script not found: $SCRIPT" >&2
  exit 2
fi

julia "$SCRIPT"
exit $?
