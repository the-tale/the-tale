# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'do post update operations'

    requires_model_validation = False

    def handle(self, *args, **options):
        
        print
        print 'LOAD ARTIFACT CONSTRUCTORS'
        print 

        subprocess.call(['./manage.py', 'artifacts_refresh_database'])

        print
        print 'LOAD MOBS CONSTRUCTORS'
        print 

        subprocess.call(['./manage.py', 'mobs_refresh_database'])

        print
        print 'LOAD JOURNAL TEXTS'
        print 

        subprocess.call(['./manage.py', 'journal_refresh_database'])

        print
        print 'LOAD JOURNAL TEXTS'
        print 

        subprocess.call(['./manage.py', 'map_update_map'])            


