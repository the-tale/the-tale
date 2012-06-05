# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

from meta_config import meta_config

class Command(BaseCommand):

    help = 'prepair all generated static files'

    requires_model_validation = False

    def handle(self, *args, **options):

        print
        print 'GENEREATE ABILITIES JS'
        print

        subprocess.call(['./manage.py', 'abilities_create_abilities_js'])

        print
        print 'GENERATE CSS'
        print

        subprocess.call(['./manage.py', 'less_generate_css'])

        print
        print 'LOAD TEXTGEN TEXTS'
        print

        subprocess.call(['./manage.py', 'game_load_texts'])

        print
        print 'GENERATE META CONFIG'
        print

        meta_config.increment_static_data_version()
        meta_config.save_config()
