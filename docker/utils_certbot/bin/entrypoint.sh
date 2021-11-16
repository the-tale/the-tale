#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

exec "$@"
