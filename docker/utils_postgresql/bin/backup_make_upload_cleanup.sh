#!/bin/bash

set -e

trap 'echo "\"${last_command}\" command failed with exit code $?."' ERR

stamp=$(date +"%FT%T")

echo "Backup and upload with stamp: $stamp"

backup_make.sh "$stamp"
backup_upload.sh "$stamp"
backup_cleanup.sh
