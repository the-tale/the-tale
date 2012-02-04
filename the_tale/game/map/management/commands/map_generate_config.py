# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from dext.jinja2 import render

from ...conf import map_settings

from ...roads.prototypes import get_road_by_model
from ...roads.models import Road

from ...places.prototypes import get_place_by_model
from ...places.models import Place, PLACE_TYPE

class Command(BaseCommand):

    help = 'generate config file for map generation on base of database data'

    option_list = BaseCommand.option_list + ( make_option('--config',
                                                          action='store',
                                                          type=str,
                                                          dest='config',
                                                          help='path to generated file'),
                                              )

    def handle(self, *args, **options):

        CONFIG = options['config']

        map_width = map_settings.WIDTH
        map_height = map_settings.HEIGHT

        places_list = [get_place_by_model(place_model)
                       for place_model in list(Place.objects.all()) ]

        roads_list = [get_road_by_model(road_model)
                      for road_model in list(Road.objects.all()) ]

        config_content = render('map/management/commands/config.py', 
                                {'map_width': map_width,
                                 'map_height': map_height,
                                 'places_list': places_list,
                                 'roads_list': roads_list,
                                 'PLACE_TYPE': PLACE_TYPE})

        with open(CONFIG, 'w') as region_config_file:
            region_config_file.write(config_content)
