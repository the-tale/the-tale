# coding: utf-8

from django.core.management.base import BaseCommand

from dext.common.utils import pid

from the_tale.accounts.logic import block_expired_accounts

class Command(BaseCommand):

    help = 'block expired accounts. MUST run only if game stopped'

    requires_model_validation = False

    def handle(self, *args, **options):

        if pid.check('game_supervisor'):
            print 'game MUST be stopped befor run this command'
            return

        block_expired_accounts()
