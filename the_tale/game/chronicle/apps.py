# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'the_tale.game.chronicle'
    label = 'chronicle'
    verbose_name = 'chronicle'

    def ready(self):
        from the_tale.game.chronicle import signal_processors
        pass
