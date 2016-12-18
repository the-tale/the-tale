#!/bin/bash

echo "------ start backuping ------"

export AWS_ACCESS_KEY_ID="{{tt_backups['aws_access_key_id']}}"
export AWS_SECRET_ACCESS_KEY="{{tt_backups['aws_secret_acccess_key']}}"
export AWS_DEFAULT_REGION="{{tt_backups['aws_region']}}"

DATE=$(date +"%F %T")

source /root/venv_backups/bin/activate

TMP_BACKUP_FILE="{{tt_backups['tmp_storage']}}postgreql_backup.gz"

{% for db in tt_backups['databases'] %}

now=$(date)
echo "start backup of {{db['name']}} at $now"

echo "tmp backup file: $TMP_BACKUP_FILE"

pg_dump -U "{{db['user']}}" "{{db['name']}}" | gzip > "$TMP_BACKUP_FILE"

now=$(date)
echo "start upload of {{db['name']}} at $now"

aws --output text --no-paginate s3 mv "$TMP_BACKUP_FILE" "s3://{{db['s3_bucket']}}$DATE.gz"

now=$(date)
echo "backup uploaded at $now"

{% endfor %}
