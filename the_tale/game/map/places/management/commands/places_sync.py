# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.game.map.places.storage import places_storage

class Command(BaseCommand):

    help = 'sync places parameters'

    requires_model_validation = False

    def handle(self, *args, **options):

        for place in places_storage.all():
            place.sync_persons(force_add=True)
            place.sync_habits()

            place.sync_parameters() # must be last operation to display and use real data

            place.update_heroes_number()
            place.update_heroes_habits()

            place.save()
