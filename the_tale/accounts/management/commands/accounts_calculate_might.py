# coding: utf-8

from django.core.management.base import BaseCommand

from the_tale.accounts.might import recalculate_accounts_might

class Command(BaseCommand):

    help = 'Recalculate mights of accounts'

    requires_model_validation = False

    def handle(self, *args, **options):
        recalculate_accounts_might()
