#!/usr/bin/env bash

set -euo pipefail

RESPONSE='{"help": null}'

if [ -n "${command}" ]; then
  HELP="$(python3 -m tfmod -h "${command}")"
else
  HELP="$(python3 -m tfmod -h)"
fi

jq -cM --arg help "${HELP}" '.help = $help'
