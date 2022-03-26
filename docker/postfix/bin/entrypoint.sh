#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

tt_render_configuration

# TODO: move somewere else
service rsyslog start

postmap /etc/postfix/virtual

exec "$@"
