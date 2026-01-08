SHELL := /bin/bash

PACKAGE_NAME := fca-api
BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
HEAD := $(shell git rev-parse --short=8 HEAD)
PACKAGE_VERSION := $(shell grep __version__ src/fca_api/__version__.py | cut -d '=' -f 2 | xargs)
PROJECT_ROOT := $(PWD)

TESTS_ROOT := $(PROJECT_ROOT)/tests

.PHONY: docs

# Make everything (possible)
all:

# Housekeeping
clean:
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Deleting all temporary files\n"
	rm -fr docs/_build/* .pytest_cache *.pyc *__pycache__* ./dist/* ./build/* *.egg-info*

version_extract:
	echo "$(PACKAGE_VERSION)"

docs:
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Building documentation\n"
	cd "$(PROJECT_ROOT)" && \
	sphinx-build -b html -W -T -E ./docs ./dist/docs/html

doc: docs

# Dependency management
update_deps:
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Update all development dependencies, including documentation and production dependencies\n"
	pdm self update && pdm update -v --dev --no-editable --no-self --update-all && pdm export -v -f requirements --dev -o docs/requirements.txt

autoformat: clean
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Autoformatting source code with Black\n"
	cd "$(PROJECT_ROOT)" && ruff format src tests && ruff check src tests --fix

# Linting
lint: clean
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Linting source code with Ruff\n"
	cd "$(PROJECT_ROOT)" && ruff check src tests

# Running tests

unittests: clean
	@echo "\n$(PACKAGE_NAME)[$(BRANCH)@$(HEAD)]: Running package unit tests + measuring coverage\n"
	cd "$(PROJECT_ROOT)" && \
	python3 -m pytest \
				--cache-clear \
				--capture=no \
				--code-highlight=yes \
				--color=yes \
				--cov=src \
				--cov-report=term-missing:skip-covered \
				-ra \
				-x \
				--tb=native \
				--verbosity=3 \
				tests/units
