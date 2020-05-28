
from django.db import models

from django.contrib.postgres import fields as postgres_fields


MAX_SOURCE_NAME_LENGTH = 32
MAX_CORE_ID_LENGTH = 32


class Report(models.Model):

    id = models.UUIDField(primary_key=True)

    state = models.IntegerField()

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    completed_at = models.DateTimeField(null=True)

    expire_at = models.DateTimeField(null=True)

    class Meta:
        db_table = 'reports'


class SubReport(models.Model):

    id = models.BigAutoField(primary_key=True)

    report = models.ForeignKey(Report, on_delete=models.CASCADE, db_column='report')

    source = models.CharField(max_length=MAX_SOURCE_NAME_LENGTH)

    state = models.IntegerField(db_index=True)

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subreports'


class DeletionRequest(models.Model):

    id = models.BigAutoField(primary_key=True)

    core_id = models.CharField(max_length=MAX_CORE_ID_LENGTH)

    source = models.CharField(max_length=MAX_SOURCE_NAME_LENGTH)

    data = postgres_fields.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deletion_requests'


class DeletionHistory(models.Model):

    id = models.BigAutoField(primary_key=True)

    core_id = models.CharField(max_length=MAX_CORE_ID_LENGTH)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'deletion_history'
