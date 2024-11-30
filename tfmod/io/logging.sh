#!/usr/bin/env bash

# Full shell logging abstractions

TF_LOG="${TF_LOG:-WARN}"

function log {
  local ts
  local level
  local message

  level="${1}"
  shift

  message="$(echo "$@")"

  # NOTE: Terraform shows fractional seconds. We don't have that, so we
  # cheese it.
  if [[ "${TF_LOG}" == 'JSON' ]]; then
    ts="$(date +"%Y-%m-%dT%H:%M:%S.000000%z")"
    message="$(echo "${message}" | sed 's/"/\\"/g')"
    echo '{"@level":"'"${level}"'","@message":"'"${message}"',"@timestamp":'"${ts}"'}'
  else
    ts="$(date +"%Y-%m-%dT%H:%M:%S.000%z")"
    level="
    "
    echo "${TS} $(printf %-7s "[${1}]")" "${message}"
  fi
}

function is-json {
  [[ "${TF_LOG}" == 'JSON' ]]
}

function is-trace {
  [[ "${TF_LOG}" == 'TRACE' ]] || is-json
}

function is-debug {
  [[ "${TF_LOG}" == 'DEBUG' ]] || is-trace
}

function is-info {
  [[ "${TF_LOG}" == 'INFO' ]] || is-debug
}

function is-warn {
  [[ "${TF_LOG}" == 'WARN' ]] || is-info
}

function debug {
  if is-debug; then
    log DEBUG "$@"
  fi
}

function info {
  if is-info; then
    log INFO "$@"
  fi
}

function warn {
  if is-warn; then
    show "${COLOR_YELLOW}" 'Error' "$@"
  fi
}

# Ensure log level is set correctly
case "${TF_LOG}" in
  JSON|TRACE|DEBUG|INFO|WARN|ERROR)
    ;;
  *)
    TF_LOG='TRACE'
esac

# TODO: Implement in python? Remove?
function quote {
  if ! is-info; then
    return 0
  fi
  while read -r line; do
    echo "  │ ${line}"
  done
}


