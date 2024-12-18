#!/usr/bin/env bash

STATE_DIR="${HOME}/.local/state"
TFMOD_HOME="${STATE_DIR}/tfmod"

UPDATE_OK='TfMod has been successfully updated!

You may now begin working with TfMod. Try running "tfmod init" to create
your first project. All TfMod commands should now work.

To update TfMod in the future, run "tfmod update"!'

function update-ok {
  echo -e "${COLOR_GREEN}${UPDATE_OK}${COLOR_RESET}"
}

ERR_UPDATE='Failed to install or update TfMod'
ERR_UPDATE_MSG='This is probably a bug in TfMod. File an issue at:

    https://github.com/jfhbrook/tfmod/issues
'

function fatal-update {
  fatal "${ERR_UPDATE}" "${ERR_UPDATE_MSG}"
}

# OS detection

function is-macos {
  if [[ "${OSTYPE}" == "darwin"* ]]; then
    debug 'MacOS detected'
    return 0
  fi
  return 1
}

# Check if a bin is installed

# We check for terraform twice on MacOS, so this helps cut down on the
# logging
TERRAFORM_IN_PATH=''

function has-bin {
  if [ "${1}" == 'terraform' ] && [ -n "${TERRAFORM_IN_PATH}" ]; then
    return 0
  fi

  if which "${1}" > /dev/null 2>&1; then
    info "Found ${1} at $(which "${1}")"
    if [ "${1}" == 'terraform' ]; then
      TERRAFORM_IN_PATH=1
    fi
    return 0
  fi

  info "Could not find ${1}"
  return 1
}

PACKAGES=()

function use-package {
  local cmd
  local pkg

  cmd="${1}"
  pkg="${2:-${1}}"

  if ! has-bin "${cmd}"; then
    PACKAGES+=("${pkg}")
  fi
}

function no-packages {
  [ ${#PACKAGES[@]} -eq 0 ]
}

# homebrew based installs

function install-homebrew {
  if confirm 'Would you like to install homebrew?'; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" | quote 'homebrew installer' || fatal-update
    info 'Homebrew installed'
    return 0
  fi
  return 1
}

function brew-install {
  if no-packages; then return 0; fi

  if ! has-bin brew; then
    install-homebrew
  fi

  echo 'Installing the following homebrew formulas:'
  for formula in "${HOMEBREW_FORMULAS[@]}"; do
    echo "- ${formula}"
  done

  # Homebrew doesn't prompt by default
  if confirm 'Would you like to install these formulas with homebrew?'; then
    brew install "${HOMEBREW_FORMULAS[@]}" | quote 'brew install' || fatal-update
    return 0
  fi
  return 1
}

# linux-based installs

function apt-install {
  if no-packages; then return 0; fi
  sudo apt install "${PACKAGES[@]}" | quote 'apt install' || fatal-update
}

function dnf-install {
  if no-packages; then return 0; fi
  sudo dnf install "${PACKAGES[@]}" | quote 'dnf install' || fatal-update
}

# do it up

function install-brew-packages {
  use-package git
  use-package python
  use-package terraform hashicorp/tap/terraform
  brew-install
}

function install-apt-packages {
  use-package git
  use-package python3
  apt-install
}

function install-dnf-packages {
  use-package git
  use-package python3
  dnf-install
}

function install-packages {
  if is-macos; then
    install-brew-packages
  elif has-bin apt; then
    install-apt-packages
  elif has-bin dnf; then
    install-dnf-packages
  else
    fatal 'Do not know how to install packages'
  fi
}

# uv related shenanigans

UV_BIN=''

function find-uv {
  if [ -n "${UV_BIN}" ]; then
    return 0
  fi

  if which uv &> /dev/null; then
    UV_BIN="$(which uv)"
  elif [ -f "${XDG_BIN_HOME}/uv" ]; then
    UV_BIN="${XDG_BIN_HOME}/uv"
  elif [ -f "${XDG_DATA_HOME}/../bin/uv" ]; then
    UV_BIN="$(realpath "${XDG_DATA_HOME}/../bin/uv")"
  elif [ -f "${HOME}/.local/bin/uv" ]; then
    UV_BIN="${HOME}/.local/bin/uv"
  fi

  if [ -n "${UV_BIN}" ]; then
    info "found uv at ${UV_BIN}"
    return 0
  fi
  return 1
}

function assert-uv {
  if [ -z "${UV_BIN}" ]; then
    fatal 'Could not find uv'
  fi
}

function install-uv {
  if find-uv; then
    return 0
  fi

  echo 'uv is installed with the following command:'
  echo
  echo '    curl -LsSf https://astral.sh/uv/install.sh | sh'
  echo

  if confirm 'Would you like to install uv?'; then
    curl -LsSf https://astral.sh/uv/install.sh | sh | quote 'curl -LsSf https://astral.sh/uv/install | sh' || fatal-update
    return 0
  fi
  return 1
}

function install-terraform {
  if has-bin terraform; then
    return 0
  fi

  fatal 'Without terraform, TfMod can not continue' \
'In order to use TfMod, you need to install terraform. You may find instructions
here:

    https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
alternately, consider the tool '\'tfswitch\'':

    https://tfswitch.warrensbox.com/'
}

CLONED=""

function clone-tfmod {
  mkdir -p "${STATE_DIR}"

  if [ ! -d "${TFMOD_HOME}" ]; then
    echo -e "${COLOR_BOLD}Cloning TfMod source...${COLOR_RESET}"
    (cd "${STATE_DIR}" && git clone git@github.com:jfhbrook/tfmod.git 1>&1 | quote 'git clone') || fatal-update
    CLONED=1
  else
    echo -e "${COLOR_BOLD}Pulling TfMod source...${COLOR_RESET}"
    (cd "${TFMOD_HOME}" && git pull origin 2>&1 | quote 'git pull') || fatal-update
  fi
}

function update-module {
  local module
  module="${1}"
  echo -e "${COLOR_BOLD}• modules/${module}:${COLOR_RESET}"
  
  terraform -chdir="${TFMOD_HOME}/modules/${module}" init -upgrade | quote 'terraform init -upgrade' || fatal-update
}

function update-all-modules {
  if [ -n "${CLONED}" ]; then
    echo -e "${COLOR_BOLD}Initializing Terraform modules...${COLOR_RESET}"
  else
    echo -e "${COLOR_BOLD}Updating Terraform modules...${COLOR_RESET}"
  fi

  update-module init
  update-module spec
}

function update-python {
  if [ -n "${CLONED}" ]; then
    echo -e "${COLOR_BOLD}Installing Python libraries..."
  else
    echo -e "${COLOR_BOLD}Updating Python libraries..."
  fi

  (cd "${TFMOD_HOME}" && rm -rf .venv) || fatal-update
  (cd "${TFMOD_HOME}" && "${UV_BIN}" sync 2>&1 | quote 'uv sync') || fatal-update
}

function setup-bin-script {
  if [ -z "${CALLED_FROM_INSTALLER:-}" ]; then
    echo -e "${COLOR_BOLD}Copying TfMod to ~/.local/bin/tfmod...${COLOR_RESET}"
    mkdir -p ~/.local/bin
    cp ~/.local/state/tfmod/bin/tfmod ~/.local/bin/tfmod
  fi
  chmod +x ~/.local/bin/tfmod
}

function check-path {
  if ! which TfMod &> /dev/null; then
    warn 'TfMod not found on your PATH. you may need to add the following to your'
    warn 'shell profile (ie ~/.bashrc, ~/.zshrc):'
    warn
    # shellcheck disable=SC2016
    warn '    export PATH="${PATH}:${HOME}/.local/bin"'
    warn
  fi
}

function install {
  install-packages
  install-terraform
  install-uv

  clone-tfmod
  find-uv
  assert-uv
  update-all-modules
  update-python
  setup-bin-script

  check-path
  update-ok
}

install || fatal-update
