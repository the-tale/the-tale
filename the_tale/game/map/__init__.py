# coding: utf-8

import os

from django.conf import settings as project_settings

from django_next.utils.app_settings import app_settings

settings = app_settings('MAP', 
                        WIDTH=30,
                        HEIGHT=20,
                        CELL_SIZE=20,
                        CELL_LENGTH=1.0,
                        
                        # map generation settings
                        GEN_CONFIG_FILE='./game/map/management/commands/map_generator/config.py',
                        GEN_REGION_OUTPUT=os.path.join(project_settings.DCONT_DIR, './map/region.js')
                        )
