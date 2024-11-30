set dotenv-load := true

root-modules := "./modules/init ./modules/entrypoint"

# By default, run checks and tests, then format and lint
default:
  @just format
  @just check
  @just test
  @just lint

#
# Installing, updating and upgrading dependencies
#

# Setup project
setup:
  for module in {{ root-modules }}; do terraform "-chdir=${module}" init -upgrade; done
  uv sync -U --extra dev
  uv pip install -e .

#
# Development tooling - linting, formatting, etc
#

# Run a command or script
run *argv:
  uv run {{ argv }}

# Run tfmod
tfmod *argv:
  uv run -- python3 -m tfmod {{ argv }}

# Format with black and isort
format:
  terraform fmt -recursive modules
  uv run black ./tfmod ./tests
  uv run isort --settings-file . ./tfmod ./tests

# Lint with flake8
lint:
  for module in ./modules/*; do echo "${module}:" && (cd ${module} && tflint); done
  uv run flake8 ./tfmod ./tests
  uv run validate-pyproject ./pyproject.toml
  shellcheck install.sh
  shellcheck bin/tfmod

# Check type annotations with pyright
check:
  uv run npx pyright@latest
  for module in {{ root-modules }}; do echo "${module}:" terraform "-chdir=${module}" validate; done

# Run tests with pytest
test *argv:
  uv run pytest {{ argv }} ./tests
  @just _clean-test

_clean-test:
  rm -f pytest_runner-*.egg
  rm -rf tests/__pycache__

#
# Shell and console
#

shell:
  uv run bash

console:
  uv run jupyter console

#
# Builds
#

# Build the entrypoint
build:
  uv run terraform -chdir=./modules/entrypoint apply -auto-approve

_clean-build:
  uv run terraform -chdir=./modules/entrypoint destroy -auto-approve

# Clean up loose files
clean: _clean-test _clean-build
  rm -rf go-tfmod.egg-info
  rm -f tfmod/*.pyc
  rm -rf tfmod/__pycache__
