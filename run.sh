#!/bin/bash

curdir="$(pwd)"

cd "$(dirname "$0")"

exec pipenv run python launcher.py --curdir "$curdir" "$@"

