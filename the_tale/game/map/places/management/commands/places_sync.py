# coding: utf-8

from django.core.management.base import BaseCommand

from game.map.places.storage import places_storage

class Command(BaseCommand):

    help = 'sync persons for every place'

    requires_model_validation = False

    def handle(self, *args, **options):

        for place in places_storage.all():
            place.sync_persons()
            place.save()
