#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

tt_render_configuration

postmap /etc/postfix/virtual

exec "$@"
