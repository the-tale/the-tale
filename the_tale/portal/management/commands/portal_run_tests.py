# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from the_tale.common.utils.logic import run_django_command

class Command(BaseCommand):

    help = 'run all non-django tests'

    requires_model_validation = False

    def handle(self, *args, **options):

        subprocess.call("rm -f `find ./ -name '*.pyc'`", shell=True)

        tests = []
        for app_label in project_settings.INSTALLED_APPS:
            label = app_label.split('.')

            if label[0] == 'django':
                continue

            tests.append(label[-1])

        run_django_command(['test'] + tests)
