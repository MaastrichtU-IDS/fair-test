#!/usr/bin/env bash

set -e
set -x

pytest -s --cov=fair_test --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml tests ${@}
