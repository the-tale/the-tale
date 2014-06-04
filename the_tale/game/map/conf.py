# coding: utf-8

import os

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

GEN_MAP_DIR = os.path.join(project_settings.DCONT_DIR, './map/')

map_settings = app_settings('MAP',
                            WIDTH=70 if not project_settings.TESTS_RUNNING else 4,
                            HEIGHT=56 if not project_settings.TESTS_RUNNING else 4,
                            CHRONICLE_RECORDS_NUMBER=10,

                            CELL_RANDOMIZE_FRACTION=0.1,

                            TEXTURE_PATH=os.path.join(project_settings.STATIC_DIR, 'game', 'images', 'map.png'),

                            CELL_SIZE=32,

                            # map generation settings
                            GEN_MAP_DIR=GEN_MAP_DIR,
                            GEN_WORLD_PROGRESSION=os.path.join(GEN_MAP_DIR, './progression'),
                            GEN_REGION_OUTPUT=os.path.join(GEN_MAP_DIR, './region-%s.js'),
                            TERRAIN_PRIORITIES_FIXTURE=os.path.join(os.path.dirname(__file__), 'fixtures', 'bioms.xls')
    )
