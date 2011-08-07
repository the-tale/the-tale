# -*- coding: utf-8 -*-
from optparse import make_option

from django.core.management.base import BaseCommand

from django_next.jinja2 import render

from ... import settings as map_settings
from ...places.prototypes import get_place_by_model
from ...places.models import Place, PLACE_TYPE

class Command(BaseCommand):

    help = 'generate config file for map generation on base of database data'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('--config',
                                                          action='store',
                                                          type=str,
                                                          default=map_settings.GEN_CONFIG_FILE,
                                                          dest='config',
                                                          help='path to generated file'),
                                              )

    def handle(self, *args, **options):

        CONFIG = options['config']

        map_width = 30 # TODO
        map_height = 20 # TODO

        places_list = [get_place_by_model(place_model)
                       for place_model in list(Place.objects.all()) ]

        config_content = render('map/management/commands/config.py', 
                                {'map_width': map_width,
                                 'map_height': map_height,
                                 'places_list': places_list,
                                 'PLACE_TYPE': PLACE_TYPE})

        with open(CONFIG, 'w') as region_config_file:
            region_config_file.write(config_content)
