# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

from meta_config import meta_config

class Command(BaseCommand):

    help = 'prepair all generated static files'

    requires_model_validation = False

    def handle(self, *args, **options):

        subprocess.call(['./manage.py', 'abilities_create_abilities_js'])

        subprocess.call(['./manage.py', 'less_generate_css'])

        meta_config.increment_static_data_version()
        meta_config.save_config()
