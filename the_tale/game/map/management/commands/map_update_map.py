# coding: utf-8
import subprocess

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'update map on base of current database state'

    requires_model_validation = False

    def handle(self, *args, **options):
        subprocess.call(['./manage.py', 'roads_update_roads'])

        subprocess.call(['./manage.py', 'roads_update_waymarks'])

        subprocess.call(['./manage.py', 'places_update_nearest_cells'])

        subprocess.call(['./manage.py', 'map_generate_map'])
