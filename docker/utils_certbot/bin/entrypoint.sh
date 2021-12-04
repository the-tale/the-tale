#!/bin/sh

set -e

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

exec "$@"
