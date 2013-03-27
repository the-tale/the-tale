# coding: utf-8

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'clean database'

    def handle(self, *args, **options):
        from common.postponed_tasks.prototypes import PostponedTaskPrototype
        from game.bundles import BundlePrototype
        from game.pvp.prototypes import Battle1x1Prototype

        BundlePrototype.remove_unused_bundles()
        PostponedTaskPrototype.remove_old_tasks()
        Battle1x1Prototype.remove_unprocessed_battles()
