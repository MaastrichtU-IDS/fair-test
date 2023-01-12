#!/bin/sh -e
set -x

ruff src tests example --fix
black src example tests
isort src example tests
