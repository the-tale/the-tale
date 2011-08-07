# -*- coding: utf-8 -*-
import json
from optparse import make_option

from django.core.management.base import BaseCommand
# from django.conf import settings as project_settings

from .map import Map
from . import places
from . import constants

from .... import settings as map_settings

class Command(BaseCommand):

    help = 'generate css from less sources'

    option_list = BaseCommand.option_list + ( make_option('--config',
                                                          action='store',
                                                          type=str,
                                                          default=map_settings.GEN_CONFIG_FILE,
                                                          dest='config',
                                                          help='path to file with all needed configuration'),
                                              )

    def handle(self, *args, **options):

        CONFIG = options['config']

        local_vars = {'places': places,
                      'constants': constants}
        global_vars = {}

        execfile(CONFIG, local_vars, global_vars) 

        config = global_vars

        game_map = Map(config['map_width'], config['map_height'])

        for map_place in config['places_list']:
            game_map.add_place(map_place)

        game_map.prepair_terrain()

        with open(map_settings.GEN_REGION_OUTPUT, 'w') as region_json_file:
            text = json.dumps(game_map.get_json_region_data(), indent=2)
            region_json_file.write(text)
