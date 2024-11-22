#!/usr/bin/env bash

set -euo pipefail

TFMOD_URL=https://raw.githubusercontent.com/jfhbrook/tfmod/refs/heads/main/bin/tfmod

echo 'info: copying tfmod to ~/.local/bin/tfmod'
mkdir -p ~/.local/bin

if [ -f "./bin/tfmod" ]; then
  cp "./bin/tfmod" ~/.local/bin/tfmod
else
  curl -LsSf "${TFMOD_URL}" -o ~/.local/bin/tfmod
fi
chmod +x ~/.local/bin/tfmod

~/.local/bin/tfmod install

if ! which tfmod &> /dev/null; then
  echo 'warn: tfmod not found on your PATH. you may need to add the following to your
warn: shell profile (ie ~/.bashrc, ~/.zshrc):
warn:
warn:    export PATH="${PATH}:${HOME}/.local/bin"
warn:'
fi
