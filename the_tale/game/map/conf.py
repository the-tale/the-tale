# coding: utf-8

import os

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

map_settings = app_settings('MAP', 
                            WIDTH=32,
                            HEIGHT=22,
                            CELL_SIZE=20,
                            CELL_LENGTH=1.0,
                            
                            # map generation settings
                            GEN_CONFIG_FILE='./game/map/management/commands/map_generator/config.py',
                            GEN_REGION_OUTPUT=os.path.join(project_settings.DCONT_DIR, './map/region.js')
                            )
