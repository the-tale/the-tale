# coding: utf-8
import os

from django.conf import settings as project_settings

from dext.utils.app_settings import app_settings

portal_settings = app_settings('PORTAL', 
                               DUMP_EMAIL='a.eletsky@gmail.com',
                               META_CONFIG=os.path.join(project_settings.PROJECT_DIR, 'meta_config.json'))

