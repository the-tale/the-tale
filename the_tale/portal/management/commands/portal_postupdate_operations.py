# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

from game.prototypes import TimePrototype

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        if TimePrototype.get_current_time().turn_number == 0:

            print
            print 'CREATE TEST MAP'
            print
            subprocess.call(['./manage.py', 'map_create_test_map'])

            print
            print 'CREATE_PERSONS'
            print

            subprocess.call(['./manage.py', 'places_sync'])

        print
        print 'UPDATE PLACES'
        print

        subprocess.call(['./manage.py', 'places_fill_name_forms'])

        print
        print 'UPDATE MAP'
        print

        subprocess.call(['./manage.py', 'map_update_map'])
