# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.finances.market import logic
from the_tale.finances.market import goods_types

from the_tale.game.heroes import logic as heroes_logic
from the_tale.game.heroes import models as heroes_model


class Command(BaseCommand):

    help = 'sync all goods'

    requires_model_validation = False

    def handle(self, *args, **options):

        for hero_model in heroes_model.Hero.objects.all().iterator():
            hero = heroes_logic.load_hero(hero_model=hero_model)
            logic.sync_goods(hero.account_id, hero)
