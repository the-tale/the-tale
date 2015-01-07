# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.game.heroes import prototypes as heroes_prototypes

from the_tale.market import logic
from the_tale.market import goods_types


class Command(BaseCommand):

    help = 'sync all goods'

    requires_model_validation = False

    def handle(self, *args, **options):

        goods_types.autodiscover()

        for hero in heroes_prototypes.HeroPrototype.from_query(heroes_prototypes.HeroPrototype._db_all()):
            logic.sync_goods(hero.account_id, hero)
