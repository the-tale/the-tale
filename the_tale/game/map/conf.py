# coding: utf-8

import os

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

from game.balance import constants as c

map_settings = app_settings('MAP',
                            WIDTH=36,
                            HEIGHT=22,
                            CELL_SIZE=20,
                            CELL_LENGTH=c.MAP_CELL_LENGTH,

                            # map generation settings
                            GEN_CONFIG_FILE='./game/map/management/commands/map_generator/config.py',
                            GEN_REGION_OUTPUT=os.path.join(project_settings.DCONT_DIR, './map/region.js')
                            )
