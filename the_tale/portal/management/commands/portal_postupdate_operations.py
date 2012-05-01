# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):

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
