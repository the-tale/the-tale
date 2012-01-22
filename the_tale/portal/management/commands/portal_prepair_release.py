# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand

class Command(BaseCommand):

    help = 'prepair all generated static files'

    requires_model_validation = False

    def handle(self, *args, **options):

        subprocess.call(['./manage.py', 'abilities_create_abilities_js'])

        subprocess.call(['./manage.py', 'less_generate_css'])
