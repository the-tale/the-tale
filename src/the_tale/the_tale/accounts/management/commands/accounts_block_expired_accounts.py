# coding: utf-8
from django.core.management.base import BaseCommand

import psutil

from the_tale.accounts.logic import block_expired_accounts

class Command(BaseCommand):

    help = 'block expired accounts. MUST run only if game stopped'

    requires_model_validation = False

    def handle(self, *args, **options):

        for proc in psutil.process_iter():
            try:
                process_cmdline = ' '.join(proc.cmdline())

                if 'django-admin' in process_cmdline and 'supervisor' in process_cmdline and 'the-tale' in process_cmdline:
                    print('game MUST be stopped befor run this command')
                    return
            except psutil.NoSuchProcess:
                pass

        block_expired_accounts()
