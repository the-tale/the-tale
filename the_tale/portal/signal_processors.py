# coding: utf-8
import random

from django.dispatch import receiver

from dext.settings import settings

from game import signals as game_signals

from portal.conf import portal_settings


@receiver(game_signals.day_started, dispatch_uid='portal_day_started')
def portal_day_started(sender, **kwargs):
    from game.heroes.prototypes import HeroPrototype
    from game.heroes.models import Hero

    heroes_number = Hero.objects.filter(is_fast=False).count()

    if heroes_number < 1:
        return

    hero_model = Hero.objects.filter(is_fast=False)[random.randint(0, heroes_number-1)]

    hero = HeroPrototype(model=hero_model)

    settings[portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY] = str(hero.account_id)
