#!/usr/bin/env bash

set -e
set -x

mypy src
flake8 src example tests
black src example tests --check
isort src example tests --check-only
