# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

from game.models import Time

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

        if not Time.objects.all().exists():
            print
            print 'CREATE TIME OBJECT'
            print
            Time.objects.create()

            print
            print 'CREATE TEST MAP'
            print
            subprocess.call(['./manage.py', 'map_create_test_map'])

            print
            print 'CREATE_PERSONS'
            print

            subprocess.call(['./manage.py', 'places_sync'])


        print
        print 'CLEAR TEXTGEN TEXTS'
        print

        subprocess.call(['./manage.py', 'textgen_clear_database'])

        print
        print 'LOAD TEXTGEN TEXTS'
        print

        subprocess.call(['./manage.py', 'game_load_texts'])

        print
        print 'LOAD QUEST WRITERS'
        print

        subprocess.call(['./manage.py', 'quests_load_writers'])

        print
        print 'UPDATE MAP'
        print

        subprocess.call(['./manage.py', 'map_update_map'])
