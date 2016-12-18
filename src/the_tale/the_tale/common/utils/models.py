# coding: utf-8

from django.db import models


class UUIDField(models.CharField):

    def __init__(self, *argv, **kwargs):
        kwargs['max_length'] = 36
        super(UUIDField, self).__init__(*argv, **kwargs)
