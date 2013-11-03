# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.common.utils.logic import run_django_command


class Command(BaseCommand):

    help = 'update map on base of current database state'

    requires_model_validation = False

    def handle(self, *args, **options):
        run_django_command(['roads_update_roads'])

        run_django_command(['roads_update_waymarks'])

        run_django_command(['places_update_nearest_cells'])

        run_django_command(['map_generate_map'])
