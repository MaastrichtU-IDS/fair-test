#!/usr/bin/env bash

set -e
set -x

mypy fair_test
flake8 fair_test example tests
black fair_test example tests --check
isort fair_test example tests --check-only
