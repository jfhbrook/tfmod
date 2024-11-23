#!/usr/bin/env bash

set -euo pipefail

TFMOD_URL=https://raw.githubusercontent.com/jfhbrook/tfmod/refs/heads/main/bin/tfmod

echo 'Copying tfmod to ~/.local/bin/tfmod...'
mkdir -p ~/.local/bin

if [ -f "./bin/tfmod" ]; then
  cp "./bin/tfmod" ~/.local/bin/tfmod
else
  curl -LsSf "${TFMOD_URL}" -o ~/.local/bin/tfmod
fi
chmod +x ~/.local/bin/tfmod

CALLED_FROM_INSTALLER=1 ~/.local/bin/tfmod update
