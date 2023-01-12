#!/usr/bin/env bash

set -e
set -x

ruff src tests
black src example tests --check
mypy src
