#!/usr/bin/env bash

set -e

# uvicorn example.main:app --reload

cd example
uvicorn main:app --reload