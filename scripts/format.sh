#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place fair_test example tests --exclude=__init__.py
black fair_test example tests
isort fair_test example tests
