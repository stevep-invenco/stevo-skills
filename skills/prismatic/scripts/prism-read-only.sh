#!/usr/bin/env bash
set -euo pipefail

# The environment guard also applies if arguments contain a flag terminator.
# exec preserves Prism's exit status and signals for the calling agent.
export PRISM_READ_ONLY=true
exec prism "$@" --read-only
