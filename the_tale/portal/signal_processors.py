# coding: utf-8
import random
import datetime

from django.dispatch import receiver

from dext.settings import settings

from game import signals as game_signals

from portal.conf import portal_settings


@receiver(game_signals.day_started, dispatch_uid='portal_day_started')
def portal_day_started(sender, **kwargs): # pylint: disable=W0613
    from game.heroes.prototypes import HeroPrototype

    heroes_query = HeroPrototype.live_query().filter(active_state_end_at__gt=datetime.datetime.now(), ban_state_end_at__lt=datetime.datetime.now())

    heroes_number = heroes_query.count()

    if heroes_number < 1:
        return

    hero_model = heroes_query[random.randint(0, heroes_number-1)]

    hero = HeroPrototype(model=hero_model)

    settings[portal_settings.SETTINGS_ACCOUNT_OF_THE_DAY_KEY] = str(hero.account_id)
