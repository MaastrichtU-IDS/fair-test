#!/usr/bin/env bash

set -e

cd example
uvicorn main:app --reload
