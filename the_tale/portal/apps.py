# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'the_tale.portal'
    label = 'portal'
    verbose_name = 'portal'

    def ready(self):
        from the_tale.portal import signal_processors
        pass
