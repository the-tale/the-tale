# coding: utf-8

import datetime

from django.core.management.base import BaseCommand
from django.db import models


from the_tale.accounts.prototypes import AccountPrototype

from the_tale.finances.bank.prototypes import InvoicePrototype
from the_tale.finances.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations


class Command(BaseCommand):

    help = 'statistics funnel'

    option_list = BaseCommand.option_list


    def print_funnel(self, year, month, new_users):
        DATE_FROM = datetime.datetime(year, month, 1)

        if month == 12:
            year += 1
            month = 0

        DATE_TO = datetime.datetime(year, month+1, 1)

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

        alive_after_1_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=30)).values_list('id', flat=True))
        alive_after_2_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=60)).values_list('id', flat=True))
        alive_after_3_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=90)).values_list('id', flat=True))
        alive_after_4_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=120)).values_list('id', flat=True))
        alive_after_5_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=150)).values_list('id', flat=True))
        alive_after_6_month_ids = set(AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                  created_at__lte=DATE_TO,
                                                                  active_end_at__gte=models.F('created_at')+datetime.timedelta(days=180)).values_list('id', flat=True))

        alive_after_1_month = len(alive_after_1_month_ids & new_accounts_ids)
        alive_after_2_month = len(alive_after_2_month_ids & new_accounts_ids)
        alive_after_3_month = len(alive_after_3_month_ids & new_accounts_ids)
        alive_after_4_month = len(alive_after_4_month_ids & new_accounts_ids)
        alive_after_5_month = len(alive_after_5_month_ids & new_accounts_ids)
        alive_after_6_month = len(alive_after_6_month_ids & new_accounts_ids)


        print '--------------------------------------'
        print 'from %s to %s' % (DATE_FROM.date(), DATE_TO.date())
        print 'visitors: %d' % new_users
        print 'registration tries %d (%.3f from visitors)' % (fast_registrations, float(fast_registrations)/new_users)
        print 'registration completed %d (%.3f from visitors)' % (registrations, float(registrations)/new_users)
        print 'payers %d (%.3f from registrations)' % (payers, float(payers)/registrations)
        print 'alive after week %d (%.3f from registrations)' % (alive_after_week, float(alive_after_week)/registrations)
        print 'alive after 1_month %d (%.3f from registrations)' % (alive_after_1_month, float(alive_after_1_month)/registrations)
        print 'alive after 2 month %d (%.3f from registrations)' % (alive_after_2_month, float(alive_after_2_month)/registrations)
        print 'alive after 3 month %d (%.3f from registrations)' % (alive_after_3_month, float(alive_after_3_month)/registrations)
        print 'alive after 4 month %d (%.4f from registrations)' % (alive_after_4_month, float(alive_after_4_month)/registrations)
        print 'alive after 5 month %d (%.5f from registrations)' % (alive_after_5_month, float(alive_after_5_month)/registrations)
        print 'alive after 6 month %d (%.6f from registrations)' % (alive_after_6_month, float(alive_after_6_month)/registrations)


    def handle(self, *args, **options):

        # FEBRUARY
        # self.print_funnel(2014, 2, 2057)

        # MART
        # self.print_funnel(2014, 3, 8764)

        # HABRAHABR
        # DATE_FROM = datetime.datetime(2014, 3, 5)
        # DATE_TO = datetime.datetime(2014, 3, 8)
        # new_users = 4554

        # APRIL
        self.print_funnel(2014, 4, 3711)

        #  may
        self.print_funnel(2014, 5, 9935)

        # june
        self.print_funnel(2014, 6, 7603)

        # july
        self.print_funnel(2014, 7, 5497)

        # august
        self.print_funnel(2014, 8, 4198)

        # september
        self.print_funnel(2014, 9, 4597)

        # october
        self.print_funnel(2014, 10, 5864)
