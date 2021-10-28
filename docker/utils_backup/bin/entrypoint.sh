#!/bin/bash

export PGPASSWORD=$BACKUP_PASSWORD
export PGUSER=$BACKUP_USER
export PGHOST=core_postgresql

export AWS_SHARED_CREDENTIALS_FILE=/root/aws.config

exec "$@"
