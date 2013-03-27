# coding: utf-8

import subprocess

from django.conf import settings as project_settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        vacuum_result = subprocess.call(['vacuumdb', '-q',
                                         '-U', project_settings.DATABASES['default']['USER'],
                                         '-d', project_settings.DATABASES['default']['NAME']])

        print vacuum_result
