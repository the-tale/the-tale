#!/bin/bash

databases=${@:1}

if [ -z $databases ];
then
    databases=$TT_DATABASES
fi

stamp=$(date +"%FT%T")

backup_dir="/backups/$stamp"

mkdir -p "$backup_dir"

for db_name in $databases;
do
    backup_file="$backup_dir/$db_name.gz"

    echo "start backup of $db_name at $(date) to $backup_file"

    export PGPASSWORD="$db_name"

    pg_dump -U $db_name $db_name | gzip > "$backup_file"

    echo "backuped at $(date)"
done
