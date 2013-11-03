# coding: utf-8

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        from the_tale.game.map.places.prototypes import BuildingPrototype

        pos = BuildingPrototype.get_available_positions(24, 13)

        print len(pos)
        print (24, 12) in pos
