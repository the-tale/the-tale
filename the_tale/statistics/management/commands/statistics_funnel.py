# coding: utf-8

import datetime

from django.core.management.base import BaseCommand
from django.db import models


from the_tale.accounts.prototypes import AccountPrototype

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations


class Command(BaseCommand):

    help = 'statistics funnel'

    option_list = BaseCommand.option_list

    def handle(self, *args, **options):

        # APRIL
        # DATE_FROM = datetime.datetime(2014, 4, 1)
        # DATE_TO = datetime.datetime(2014, 5, 1)
        # new_users = 3711

        # MART
        # DATE_FROM = datetime.datetime(2014, 3, 1)
        # DATE_TO = datetime.datetime(2014, 4, 1)
        # new_users = 8764

        # FEBRUARY
        # DATE_FROM = datetime.datetime(2014, 2, 1)
        # DATE_TO = datetime.datetime(2014, 3, 1)
        # new_users = 2057

        # HABRAHABR
        DATE_FROM = datetime.datetime(2014, 3, 5)
        DATE_TO = datetime.datetime(2014, 3, 8)
        new_users = 4554

        fast_registrations = sum(RecordPrototype.select_values(relations.RECORD_TYPE.REGISTRATIONS_TRIES, date_from=DATE_FROM, date_to=DATE_TO))

        registrations = sum(RecordPrototype.select_values(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED, date_from=DATE_FROM, date_to=DATE_TO))

        new_accounts_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM, created_at__lte=DATE_TO).values_list('id', flat=True))
        all_payers_ids = set(InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                         sender_type=ENTITY_TYPE.XSOLLA,
                                                         currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id', flat=True))

        payers = len(new_accounts_ids & all_payers_ids)

        alive_after_week_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                created_at__lte=DATE_TO,
                                                                active_end_at__gte=models.F('created_at')+datetime.timedelta(days=7)).values_list('id', flat=True))

        alive_after_week = len(alive_after_week_ids & new_accounts_ids)

        alive_after_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                created_at__lte=DATE_TO,
                                                                active_end_at__gte=models.F('created_at')+datetime.timedelta(days=30)).values_list('id', flat=True))

        alive_after_month = len(alive_after_month_ids & new_accounts_ids)

        print '--------------------------------------'
        print 'from %s to %s' % (DATE_FROM.date(), DATE_TO.date())
        print 'new users: %d' % new_users
        print 'registration tries %d (%.3f)' % (fast_registrations, float(fast_registrations)/new_users)
        print 'registration completed %d (%.3f)' % (registrations, float(registrations)/new_users)
        print 'payers %d (%.3f)' % (payers, float(payers)/new_users)
        print 'alive after week %d (%.3f)' % (alive_after_week, float(alive_after_week)/new_users)
        print 'alive after month %d (%.3f)' % (alive_after_month, float(alive_after_month)/new_users)
