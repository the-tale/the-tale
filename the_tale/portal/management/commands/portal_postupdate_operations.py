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

        subprocess.call(['./manage.py', 'textgen_refresh_database'])

        print
        print 'LOAD QUEST WRITERS'
        print 

        subprocess.call(['./manage.py', 'quests_load_writers'])
        
        print
        print 'LOAD ARTIFACT CONSTRUCTORS'
        print 

        subprocess.call(['./manage.py', 'artifacts_refresh_database'])

        print
        print 'LOAD MOBS CONSTRUCTORS'
        print 

        subprocess.call(['./manage.py', 'mobs_refresh_database'])

        print
        print 'UPDATE MAP'
        print 

        subprocess.call(['./manage.py', 'map_update_map'])            


