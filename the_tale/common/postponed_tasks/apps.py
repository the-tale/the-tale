# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'the_tale.common.postponed_tasks'
    label = 'postponed_tasks'
    verbose_name = 'postponed_tasks'

    def ready(self):
        from the_tale.common.postponed_tasks.prototypes import autodiscover
        autodiscover()
