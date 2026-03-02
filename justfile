venv_bin := ".venv/bin"

# list available recipes
default:
    @just --list

# create venv and install dependencies
init:
    python3 -m venv .venv
    {{venv_bin}}/pip install -e '.[dev]'

# run charkha tui
run:
    {{venv_bin}}/python3 -m charkha.hexes

# start a python repl inside the virtual environment
repl:
    {{venv_bin}}/python3

# autoformat code
format:
    {{venv_bin}}/ruff format .
    {{venv_bin}}/ruff check --fix .

# run static type checking
typecheck:
    {{venv_bin}}/ty check charkha

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
    @rm -rf charkha.egg-info
    @rm -rf .pytest_cache
    @rm -rf .ruff_cache
    @rm -rf charkha/__pycache__
    @rm -rf tests/__pycache__
