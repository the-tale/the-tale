# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'the_tale.market'
    label = 'market'
    verbose_name = 'market'

    def ready(self):
        from the_tale.market import goods_types
        goods_types.autodiscover()
