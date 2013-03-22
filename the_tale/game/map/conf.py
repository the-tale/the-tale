# coding: utf-8

import os

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

from game.balance import constants as c

map_settings = app_settings('MAP',
                            WIDTH=36 if not project_settings.TESTS_RUNNING else 4,
                            HEIGHT=26 if not project_settings.TESTS_RUNNING else 4,
                            CELL_SIZE=20,
                            CELL_LENGTH=c.MAP_CELL_LENGTH,
                            CHRONICLE_RECORDS_NUMBER=10,

                            CELL_RANDOMIZE_FRACTION=0.1,

                            # map generation settings
                            GEN_WORLD_PROGRESSION=os.path.join(project_settings.DCONT_DIR, './map/progression'),
                            GEN_REGION_OUTPUT=os.path.join(project_settings.DCONT_DIR, './map/region.js'),
                            TERRAIN_PRIORITIES_FIXTURE=os.path.join(os.path.dirname(__file__), 'fixtures', 'bioms.xls')
    )
