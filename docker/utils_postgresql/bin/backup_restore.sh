#!/bin/bash

stamp=$1

if [ -z $stamp ];
then
    echo "ERROR: backup stamp must be specified"
    exit 1
fi

# TODO: remove, when there are no backups with spaces left
stamp="${stamp/SPACE/ }"

backup_dir=/backups/$stamp

if [ ! -d "$backup_dir" ];
then
    echo "ERROR: backup dir must exist"
    exit 1
fi

databases="${@:2}"

if [ -z "$databases" ];
then
    databases=$TT_DATABASES
fi

sql_clean="SELECT 'DROP TABLE IF EXISTS \"' || tablename || '\" CASCADE;' FROM pg_tables WHERE schemaname = 'public'"

for db_name in $databases;
do
    backup_file="$backup_dir/$db_name.gz"

    if [ ! -f $backup_file ];
    then
        echo "ERROR: no backup found for $db_name"
        exit 1
    fi

    export PGPASSWORD="$db_name"

    echo "clean $db_name"

    psql -U $db_name $db_name --quiet -t -c "$sql_clean" | psql -U $db_name --quiet $db_name

    echo "restore backup of $db_name"

    gunzip -c "$backup_file" | psql -U $db_name --quiet $db_name

    echo "restored"
done
