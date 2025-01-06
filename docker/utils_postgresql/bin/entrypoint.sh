#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

export PGPASSWORD=$BACKUP_PASSWORD
export PGUSER=$BACKUP_USER
export PGHOST=$POSTGRES_HOST
export PGPORT=$POSTGRES_PORT

export AWS_SHARED_CREDENTIALS_FILE=/root/aws.config

wait-for-it $PGHOST:$PGPORT -t $TT_WAIT_TIMEOUT

exec "$@"
