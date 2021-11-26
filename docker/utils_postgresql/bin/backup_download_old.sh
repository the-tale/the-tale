#!/bin/bash

stamp=$1

if [ -z "$stamp" ];
then
    echo "ERROR: backup stamp must be specified"
    exit 1
fi

# TODO: remove, when there are no backups with spaces left
stamp="${stamp/SPACE/ }"

databases="${@:2}"

if [ -z "$databases" ];
then
    databases=$TT_DATABASES
fi

backup_dir="/backups/$stamp"

mkdir -p "$backup_dir"

for db_name in $databases;
do
    backup_file="$backup_dir/$db_name.gz"
    aws --output text --no-paginate s3 cp "s3://$TT_S3_BACKET/$db_name/$stamp.gz" "$backup_file"
done
