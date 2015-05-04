# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'the_tale.common.utils'
    label = 'the_tale_utils'
    verbose_name = 'The-Tale utils'
