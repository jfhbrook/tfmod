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
