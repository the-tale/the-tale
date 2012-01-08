#coding: utf-8
import math

from django.core.management.base import BaseCommand

from .... import settings as map_settings

from ...prototypes import Place
from ...prototypes import get_place_by_model
from ... import settings as places_settings

E = 0.01

def dst(x, y, x2, y2):
    return math.sqrt((x-x2)**2 + (y-y2)**2)

class Command(BaseCommand):

    help = 'for each place calculate nearest map cells'

    def handle(self, *args, **options):

        places = [get_place_by_model(model) for model in Place.objects.all()]

        for place in places:
            place.nearest_cells = []

        for x in xrange(0, map_settings.WIDTH):
            for y in xrange(0, map_settings.HEIGHT):
                nearest_place = None
                nearest_power = 0

                for place in places:
                    cur_dst = dst(x, y, place.x, place.y)

                    if cur_dst < E:
                        place_power = places_settings.MAX_SIZE**2
                    else:
                        place_power = place.size / (cur_dst**2)

                    if nearest_power < place_power:
                        nearest_place = place
                        nearest_power = place_power

                if nearest_place:
                    nearest_place.nearest_cells.append((x, y))


        for place in places:
            place.save()
                

