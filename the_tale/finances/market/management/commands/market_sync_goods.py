# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.finances.market import logic
from the_tale.finances.market import goods_types


class Command(BaseCommand):

    help = 'sync all goods'

    requires_model_validation = False

    def handle(self, *args, **options):

        for hero in heroes_prototypes.HeroPrototype.from_query(heroes_prototypes.HeroPrototype._db_all()):
            logic.sync_goods(hero.account_id, hero)
