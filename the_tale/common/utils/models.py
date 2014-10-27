# coding: utf-8

from django.db import models

from south.modelsinspector import add_introspection_rules


class UUIDField(models.CharField):

    def __init__(self, *argv, **kwargs):
        kwargs['max_length'] = 36
        super(UUIDField, self).__init__(*argv, **kwargs)


add_introspection_rules([], ["^the_tale\.common\.utils\.models\.UUIDField"])
