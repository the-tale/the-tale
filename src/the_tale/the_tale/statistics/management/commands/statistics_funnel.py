
import smart_imports

smart_imports.all()


class Command(utilities_base.Command):

    help = 'statistics funnel'

    LOCKS = ['portal_commands']

    def print_funnel(self, year, month, new_users):
        DATE_FROM = datetime.datetime(year, month, 1)

        if month == 12:
            year += 1
            month = 0

        DATE_TO = datetime.datetime(year, month + 1, 1)

        fast_registrations = sum(prototypes.RecordPrototype.select_values(relations.RECORD_TYPE.REGISTRATIONS_TRIES, date_from=DATE_FROM, date_to=DATE_TO))

        registrations = sum(prototypes.RecordPrototype.select_values(relations.RECORD_TYPE.REGISTRATIONS_COMPLETED, date_from=DATE_FROM, date_to=DATE_TO))

        new_accounts_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM, created_at__lte=DATE_TO).values_list('id', flat=True))
        all_payers_ids = set(bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                                         sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                                         currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', flat=True))

        payers = len(new_accounts_ids & all_payers_ids)

        alive_after_week_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                   created_at__lte=DATE_TO,
                                                                                   active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=7)).values_list('id', flat=True))

        alive_after_week = len(alive_after_week_ids & new_accounts_ids)

        alive_after_1_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=30)).values_list('id', flat=True))
        alive_after_2_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=60)).values_list('id', flat=True))
        alive_after_3_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=90)).values_list('id', flat=True))
        alive_after_4_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=120)).values_list('id', flat=True))
        alive_after_5_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=150)).values_list('id', flat=True))
        alive_after_6_month_ids = set(accounts_prototypes.AccountPrototype._db_filter(created_at__gte=DATE_FROM,
                                                                                      created_at__lte=DATE_TO,
                                                                                      active_end_at__gte=django_models.F('created_at') + datetime.timedelta(days=180)).values_list('id', flat=True))

        alive_after_1_month = len(alive_after_1_month_ids & new_accounts_ids)
        alive_after_2_month = len(alive_after_2_month_ids & new_accounts_ids)
        alive_after_3_month = len(alive_after_3_month_ids & new_accounts_ids)
        alive_after_4_month = len(alive_after_4_month_ids & new_accounts_ids)
        alive_after_5_month = len(alive_after_5_month_ids & new_accounts_ids)
        alive_after_6_month = len(alive_after_6_month_ids & new_accounts_ids)

        self.logger.info('--------------------------------------')
        self.logger.info('from %s to %s' % (DATE_FROM.date(), DATE_TO.date()))
        self.logger.info('visitors: %d' % new_users)
        self.logger.info('registration tries %d (%.3f from visitors)' % (fast_registrations, float(fast_registrations) / new_users))
        self.logger.info('registration completed %d (%.3f from visitors)' % (registrations, float(registrations) / new_users))
        self.logger.info('payers %d (%.3f from registrations)' % (payers, float(payers) / registrations))
        self.logger.info('alive after week %d (%.3f from registrations)' % (alive_after_week, float(alive_after_week) / registrations))
        self.logger.info('alive after 1_month %d (%.3f from registrations)' % (alive_after_1_month, float(alive_after_1_month) / registrations))
        self.logger.info('alive after 2 month %d (%.3f from registrations)' % (alive_after_2_month, float(alive_after_2_month) / registrations))
        self.logger.info('alive after 3 month %d (%.3f from registrations)' % (alive_after_3_month, float(alive_after_3_month) / registrations))
        self.logger.info('alive after 4 month %d (%.4f from registrations)' % (alive_after_4_month, float(alive_after_4_month) / registrations))
        self.logger.info('alive after 5 month %d (%.5f from registrations)' % (alive_after_5_month, float(alive_after_5_month) / registrations))
        self.logger.info('alive after 6 month %d (%.6f from registrations)' % (alive_after_6_month, float(alive_after_6_month) / registrations))

    def _handle(self, *args, **options):

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
