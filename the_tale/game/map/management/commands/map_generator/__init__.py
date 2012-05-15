# -*- coding: utf-8 -*-
import os

from optparse import make_option

from django.core.management.base import BaseCommand

from dext.utils import s11n

from game.prototypes import get_current_time

from .map import Map
from . import places
from . import roads

from ....conf import map_settings
from ....prototypes import MapInfoPrototype
from ....places.models import TERRAIN

class ConfigConstants:
    TERRAIN = TERRAIN

class Command(BaseCommand):

    help = 'generate map on base on specified config file'

    requires_model_validation = False

    option_list = BaseCommand.option_list + ( make_option('--config',
                                                          action='store',
                                                          type=str,
                                                          dest='config',
                                                          help='path to file with all needed configuration'),
                                              )

    def handle(self, *args, **options):

        CONFIG = options['config']

        local_vars = {'places': places,
                      'roads': roads,
                      'constants': ConfigConstants}
        global_vars = {}

        execfile(CONFIG, local_vars, global_vars)

        config = global_vars

        game_map = Map(config['map_width'], config['map_height'])

        for map_place in config['places_list']:
            game_map.add_place(map_place)

        for map_road in config['roads_list']:
            game_map.add_road(map_road)

        game_map.prepair_terrain()

        game_map.pave_ways()

        time = get_current_time()
        terrain = game_map.get_terrain_map()
        MapInfoPrototype.create(turn_number=time.turn_number,
                                width=config['map_width'],
                                height=config['map_height'],
                                terrain=terrain)


        output_dir_name = os.path.dirname(map_settings.GEN_REGION_OUTPUT)
        if not os.path.exists(output_dir_name):
            os.makedirs(output_dir_name, 0755)

        with open(map_settings.GEN_REGION_OUTPUT, 'w') as region_json_file:
            text = s11n.to_json(game_map.get_json_region_data())
            region_json_file.write(text)
