# The essentials for io in the tfmod entry point. Separated out from other io
# ostensibly for performance reasons.

COLOR_RED='\e[0;31m'
COLOR_YELLOW='\e[0;33m'
COLOR_GREEN='\e[0;32m'
COLOR_BOLD='\e[0;1m'
COLOR_RESET='\e[0m'
TOP_BAR='╷'
MIDDLE_BAR='│'
BOTTOM_BAR='╵'

function show {
  local color
  local level
  local title
  local body
  color="${1}"
  level="${2}"
  title="${3}"
  body="${4:-}"

  echo -e "${color}${TOP_BAR}${COLOR_RESET}"
  echo -e "${color}${MIDDLE_BAR} ${level}:${COLOR_RESET}" "${title}"

  if [ -n "${body}" ]; then
    echo -e "${color}${MIDDLE_BAR}${COLOR_RESET}"
    echo "${body}" | while read -r line; do
      echo -e "${color}${MIDDLE_BAR}${COLOR_RESET} " "${line}"
    done
  fi

  echo -e "${color}${BOTTOM_BAR}${COLOR_RESET}"
}

function error {
  show "${COLOR_RED}" 'Error' "$@"
}

function fatal {
  error "$@"
  exit 1
}
