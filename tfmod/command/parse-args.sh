TF_LOG="${TF_LOG:-WARN}"
# Save arguments to pass directly to tfmod
ARGV="$*"
COMMAND=''
SHOW_HELP=''

# TODO: Populate template with output from python entrypoint
# TODO: Make behavior match python entrypoint as close as possible
# TODO: Leverage tfmod in python for most help text

HELP='Usage: tfmod [OPTIONS] [COMMAND]

Commands:
  version          Show the current TfMod version
  init             Initialize a new project
  config           Configure TfMod
  update           Install or update TfMod and its dependencies
  unwise           Remove TfMod and its files.

Global options (use these before the subcommand, if any):
  -version      An alias for the "version" subcommand.'

UNWISE_HELP='Usage: TfMod unwise

Remove TfMod and its files.'

UPDATE_HELP='Usage: TfMod update

Install or update TfMod and its dependencies.'

while [[ $# -gt 0 ]]; do
  case "${1}" in
    -h|-help|--help)
      SHOW_HELP=1
      shift
      ;;
    update|unwise)
      if [ -z "${COMMAND}" ]; then
        COMMAND="${1}"
      fi
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "${COMMAND}" ]; then
  echo "${HELP}"
  exit 0
fi

if [ -n "${SHOW_HELP}" ]; then
  case "${COMMAND:-}" in
    update)
      echo "${UPDATE_HELP}"
    ;;
    unwise)
      echo "${UNWISE_HELP}"
    ;;
    *)
      echo "${HELP}"
    ;;
  esac
  exit 0
fi
