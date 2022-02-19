#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

export PGPASSWORD=$BACKUP_PASSWORD
export PGUSER=$BACKUP_USER
export PGHOST=core-postgresql

export AWS_SHARED_CREDENTIALS_FILE=/root/aws.config

wait-for-it $PGHOST:5432 -t $TT_WAIT_TIMEOUT

exec "$@"
