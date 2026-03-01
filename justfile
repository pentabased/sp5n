venv_bin := ".venv/bin"

# list available recipes
default:
    @just --list

# create venv and install dependencies
init:
    python3 -m venv .venv
    {{venv_bin}}/pip install -e '.[dev]'

# run sp5n tui
run:
    {{venv_bin}}/python3 -m sp5n.hexes

# start a python repl inside the virtual environment
repl:
    {{venv_bin}}/python3

# autoformat code
format:
    {{venv_bin}}/ruff format .
    {{venv_bin}}/ruff check --fix .

# run static type checking
typecheck:
    {{venv_bin}}/ty check sp5n

# run unit tests
test:
    {{venv_bin}}/pytest -vv -s

# run all validation checks
validate: && typecheck test
    {{venv_bin}}/ruff format --check .
    {{venv_bin}}/ruff check .

# remove venv dir and other build artifacts
clean:
    @rm -rf .venv
    @rm -rf sp5n.egg-info
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @rm -rf sp5n/__pycache__
    @rm -rf tests/__pycache__
