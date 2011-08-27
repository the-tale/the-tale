# -*- coding: utf-8 -*-
import subprocess
import tempfile

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'update map on base of current database state'

    requires_model_validation = False

    def handle(self, *args, **options):
        config_file = tempfile.NamedTemporaryFile()

        subprocess.call(['./manage.py', 'roads_update_roads'])

        subprocess.call(['./manage.py', 'roads_update_waymarks'])

        subprocess.call(['./manage.py', 'map_generate_config',
                         '--config', config_file.name])

        subprocess.call(['./manage.py', 'map_generate_map',
                         '--config', config_file.name])
