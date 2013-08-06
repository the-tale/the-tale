# coding: utf-8
import datetime

from django.core.management.base import BaseCommand
from django.db import models

from dext.utils import pid

from accounts.models import Account, Award
from accounts.prototypes import AccountPrototype
from accounts.relations import AWARD_TYPE
from accounts.logic import get_system_user

from accounts.payments.conf import payments_settings
from accounts.payments.logic import transaction_gm

from bank.models import Account as BankAccount, Invoice as BankInvoice
from bank.models.relations import INVOICE_STATE
from bank.dengionline.models import Invoice as DOInvoice
from bank.xsolla.models import Invoice as XsollaInvoice

from game.heroes.models import Hero
from game.workers.environment import workers_environment

class Command(BaseCommand):

    help = 'reset all payments, bank accounts and other things'

    requires_model_validation = False

    def handle(self, *args, **options):

        if payments_settings.ENABLE_REAL_PAYMENTS:
            print u'can not reset payments: first disable payments_settings.ENABLE_REAL_PAYMENTS'
            return

        if pid.check(workers_environment.supervisor.pid):
            print u'stop game before reseting payments'
            return

        BankAccount.objects.all().delete()
        BankInvoice.objects.exclude(id=446).delete()
        BankInvoice.objects.filter(id=446).update(state=INVOICE_STATE.FORCED)

        DOInvoice.objects.all().delete()
        XsollaInvoice.objects.exclude(id=19).delete()

        BASE_PREMIUM_DAYS_LENGTH = 3
        MAX_PREMIUM_DAYS_FOR_MIGHT = 30

        max_might = float(Hero.objects.all().aggregate(models.Max('might'))['might__max'])

        for hero in Hero.objects.filter(premium_state_end_at__gt=datetime.datetime.now()):
            hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(days=hero.might / max_might * MAX_PREMIUM_DAYS_FOR_MIGHT + BASE_PREMIUM_DAYS_LENGTH)
            hero.save()

            Account.objects.filter(id=hero.account_id).update(premium_end_at=hero.premium_state_end_at)

        REWARDS = {AWARD_TYPE.CONTEST_1_PLACE: 800,
                   AWARD_TYPE.CONTEST_2_PLACE: 600,
                   AWARD_TYPE.CONTEST_3_PLACE: 400}

        for award in Award.objects.filter(type__in=[AWARD_TYPE.CONTEST_1_PLACE, AWARD_TYPE.CONTEST_2_PLACE, AWARD_TYPE.CONTEST_3_PLACE]):
            transaction_gm(account=AccountPrototype.get_by_id(award.account_id),
                           amount=REWARDS[award.type],
                           description=u'Награда за победу в конкурсе.',
                           game_master=get_system_user())

        # give money for emblem
        transaction_gm(account=AccountPrototype.get_by_id(1124),
                       amount=5000,
                       description=u'За эмблему «Сказки» и портреты монстров ;-)',
                       game_master=get_system_user())

        for developer_id in (1, 5, 209, 1022):
            transaction_gm(account=AccountPrototype.get_by_id(developer_id),
                           amount=5000,
                           description=u'Начисления разработчикам.',
                           game_master=get_system_user())
