#!/usr/bin/env bash

set -e
set -x

ruff src tests
black src example tests --check
isort src example tests --check-only
mypy src
