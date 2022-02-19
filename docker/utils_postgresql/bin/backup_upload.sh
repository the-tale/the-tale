#!/bin/bash

stamp=$1

if [ -z $stamp ];
then
    echo "backup stamp must be specified"
    exit 1
fi

databases=${@:1}

if [ ! -z $databases ];
then
    databases=$TT_DATABASES
fi

backup_dir="/backups/$stamp"

for db_name in $databases
do
    backup_file="$backup_dir/$db_name.gz"
    aws --output text --no-paginate s3 mv "$backup_file" "s3://$TT_S3_BACKET/$stamp/"
done
