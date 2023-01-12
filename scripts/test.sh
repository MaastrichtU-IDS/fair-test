#!/usr/bin/env bash

set -e
set -x

pytest -s --cov=src --cov=tests --cov-report=term-missing:skip-covered --cov-report=xml tests ${@}
