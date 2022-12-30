#!/bin/bash

cd "$(dirname "$0")"

pipenv run python launcher.py "$@"

