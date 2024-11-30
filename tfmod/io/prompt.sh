# Confirm y/N
function confirm {
  local choice

  echo -e "${COLOR_BOLD}${1}${COLOR_RESET}"
  echo '  TfMod will perform the actions described above.'
  echo "  Only 'yes' will be accepted to approve."
  echo ''

  read -r -p "Enter a value: " choice
  case "${choice}" in
    y|yes|Y|YES)
      return 0
      ;;
    *)
      fatal 'Action canceled.'
      ;;
  esac
}
