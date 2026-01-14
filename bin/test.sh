#!/bin/bash -e

THIS_DIR=$(dirname "${BASH_SOURCE[0]}")
PROJECT_ROOT=$(realpath "${THIS_DIR}/..")
cd "${PROJECT_ROOT}"

exec pdm run pytest \
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
    "${@:-tests/}"