#!/bin/sh -e
set -x

# autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place src example tests --exclude=__init__.py
ruff src tests example --fix
black src example tests
isort src example tests
