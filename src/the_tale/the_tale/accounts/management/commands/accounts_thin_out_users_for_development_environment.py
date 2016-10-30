# coding: utf-8
from django.conf import settings as project_settings
from django.core.management.base import BaseCommand

import psutil

from the_tale.accounts import logic

class Command(BaseCommand):

    help = 'Remove most of users from database, reatain only specified amount + all clan users. Also actualize their active states.'

    requires_model_validation = False

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument('-n', '--number', action='store', type=int, dest='accounts_number', default=1000, help='howe many accounts muse be remained')


    def handle(self, *args, **options):

        for proc in psutil.process_iter():
            try:
                process_cmdline = ' '.join(proc.cmdline())

                if 'django-admin' in process_cmdline and 'supervisor' in process_cmdline and 'the-tale' in process_cmdline:
                    print('game MUST be stopped befor run this command')
                    return
            except psutil.NoSuchProcess:
                pass

        if not project_settings.DEBUG:
            print('DEBUG MUST be True to run this command (command must be runned only in development environment)')
            return

        logic.thin_out_accounts(options['accounts_number'], 30*24*60*60)
