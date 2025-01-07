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
    databases="$TT_DATABASES"
fi

sql_clean="SELECT 'DROP TABLE IF EXISTS \"' || tablename || '\" CASCADE;' FROM pg_tables WHERE schemaname = 'public'"

for db_name in $databases;
do
    backup_file="$backup_dir/$db_name.gz"

    if [ ! -f "$backup_file" ];
    then
        echo "ERROR: no backup found for $db_name"
        exit 1
    fi

    PASSWORD_VAR="PG_${db_name}_PASSWORD"

    if [ -n "${!PASSWORD_VAR}" ]; then
        export PGPASSWORD="${!PASSWORD_VAR}"
    else
        export PGPASSWORD="${db_name}"
    fi

    USER_VAR="PG_${db_name}_USER"

    if [ -n "${!USER_VAR}" ]; then
        export PGUSER="${!USER_VAR}"
    else
        export PGUSER="${db_name}"
    fi

    echo "clean $db_name"

    # TODO: fix "ERROR:  must be owner of extension plpgsql"
    # that error does not break restoration, but is annoying
    # it caused by dumping db extensions, which is created by root user, not by db owner

    psql -U "$PGUSER" "$db_name" --quiet -t -c "$sql_clean" | psql -U "$PGUSER" --quiet "$db_name"

    echo "restore backup of $db_name"

    gunzip -c "$backup_file" | psql -U "$PGUSER" --quiet "$db_name"

    echo "restored"
done
