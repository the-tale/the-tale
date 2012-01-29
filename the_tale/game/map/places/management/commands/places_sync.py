# coding: utf-8

from django.core.management.base import BaseCommand

from ...models import Place
from ...prototypes import get_place_by_model

class Command(BaseCommand):

    help = 'sync persons for every place'

    requires_model_validation = False

    def handle(self, *args, **options):

        for place_model in Place.objects.all():
            place = get_place_by_model(place_model)
            place.sync_terrain()
            place.sync_persons()
            place.save()

