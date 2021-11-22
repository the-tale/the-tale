#!/bin/bash

stamp=$1

if [ ! -z $stamp ];
then
    echo "backup stamp must be specified"
    exit 1
fi

databases=${@:1}

if [ ! -z $databases ];
then
    databases=$TT_DATABASES
fi

backup_dir=/backups/$stamp

for db_name in $backup_dir/*
do
    backup_file="$backup_dir/$db_name.gz"

    aws --output text --no-paginate s3 mv "$backup_file" "s3://$db_name/$stamp.gz"
done
