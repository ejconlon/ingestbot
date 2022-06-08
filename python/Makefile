# All common build tasks can be invoked by targets here.
# For example, to setup the virtual environment, use `make venv`.
# Then `make test` to lint, typecheck, and unit test.

# Install system-level dependencies necessary to build the project
.PHONY: deps
deps:
	pip3 install pip-tools

# Remove frozen dependencies for a fresh pipcompile
.PHONY: pipclean
pipclean:
	rm -f requirements.txt dev-requirements.txt

# Freeze dependencies specified in requirements files
.PHONY: pipcompile
pipcompile:
	python3 -m piptools compile requirements.in
	python3 -m piptools compile dev-requirements.in

# Remove the virtual environment
.PHONY: venvclean
venvclean:
	rm -rf .venv

# Create the virtual environment
.PHONY: venv
venv:
	python3 -m venv --upgrade-deps .venv
	.venv/bin/python3 -m pip install wheel
	.venv/bin/python3 -m pip install -r dev-requirements.txt

# Typecheck with mypy
.PHONY: typecheck
typecheck:
	.venv/bin/python3 -m mypy -p ingestbot

# Lint with flake8
.PHONY: lint
lint:
	.venv/bin/python3 -m flake8 ingestbot

# Unit test with pytest - TODO add some tests!
.PHONY: unit
unit:
	.venv/bin/python3 -m pytest .

# Run all tests
.PHONY: test
test: lint typecheck unit

# Run the server locally with the default args.
# Copy the command and run it in bash to pass custom args.
.PHONY: run
run:
	.venv/bin/python3 -m ingestbot.main
