# coding: utf-8
from datetime import datetime

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'reset all payments, bank accounts and other things'

    requires_model_validation = False

    def handle(self, *args, **options):
        from accounts.models import Account
        from bank.models import Account as BankAccount, Invoice as BankInvoice
        from bank.dengionline.models import Invoice as DOInvoice
        from game.heroes.models import Hero
        from accounts.payments.conf import payments_settings

        if payments_settings.ENABLE_REAL_PAYMENTS:
            print u'can not reset payments: first disable payments_settings.ENABLE_REAL_PAYMENTS'
            return

        Account.objects.all().update(premium_end_at=datetime.now())
        Hero.objects.all().update(premium_state_end_at=datetime.now())
        BankAccount.objects.all().delete()
        BankInvoice.objects.all().delete()
        DOInvoice.objects.all().delete()
