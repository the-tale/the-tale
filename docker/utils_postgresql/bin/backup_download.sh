#!/bin/bash

stamp=$1

if [ -z "$stamp" ];
then
    echo "ERROR: backup stamp must be specified"
    exit 1
fi

databases="${@:2}"

if [ -z "$databases" ];
then
    databases=$TT_DATABASES
    echo "Databases has not specified, backup all: $databases"
fi

backup_dir="/backups/$stamp"

mkdir -p "$backup_dir"

for db_name in $databases;
do
    aws --output text --no-paginate s3 cp "s3://$TT_S3_BACKET/$stamp/$db_name.gz" "$backup_dir"
done
