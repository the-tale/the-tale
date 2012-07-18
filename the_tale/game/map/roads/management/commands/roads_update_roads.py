# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from game.map.roads.storage import roads_storage

class Command(BaseCommand):

    help = 'update roads data'

    def handle(self, *args, **options):

        for road in roads_storage.all():
            road.update()
