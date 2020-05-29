
import smart_imports

smart_imports.all()


class ActiveBase(base.BaseMetric):

    def get_value(self, date):
        if date == self.now_date:
            return self.get_actual_value(date)

        return self.get_restored_value(date)

    def get_actual_value(cls, date):
        raise NotImplementedError()

    def get_restored_value(cls, date):
        raise NotImplementedError()


class Premiums(ActiveBase):
    TYPE = relations.RECORD_TYPE.PREMIUMS

    def get_actual_value(self, date):
        premiums_ids = set(accounts_prototypes.AccountPrototype._db_filter(self.db_date_gte('premium_end_at', date=date)).values_list('id', flat=True))
        infinit_ids = set(bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                                      operation_uid__contains='infinit',
                                                                      sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                                      currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('recipient_id', flat=True))
        return len(premiums_ids | infinit_ids)

    def get_invoice_intervals_count(self, days, date):
        starts = list(bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                                  operation_uid__contains='<%s%d' % (shop_relations.GOODS_GROUP.PREMIUM.uid_prefix, days),
                                                                  sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                                  currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('created_at', flat=True))
        return len([True
                    for created_at in starts
                    if created_at <= datetime.datetime.combine(date, datetime.time()) < created_at + datetime.timedelta(days=days)])

    def get_invoice_infinit_intervals_count(self, date):
        return bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                           self.db_date_lte('created_at', date),
                                                           operation_uid__contains='<%sinfinit' % shop_relations.GOODS_GROUP.PREMIUM.uid_prefix,
                                                           sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                           currency=bank_relations.CURRENCY_TYPE.PREMIUM).count()

    def get_restored_value(self, date):
        # TODO: now this method use euristic which give wrong results when user buy more then one subscription simultaneously
        if conf.settings.PAYMENTS_START_DATE.date() > date:
            return 0

        return (portal_conf.settings.PREMIUM_DAYS_FOR_HERO_OF_THE_DAY +
                self.get_invoice_intervals_count(7, date) +
                self.get_invoice_intervals_count(15, date) +
                self.get_invoice_intervals_count(30, date) +
                self.get_invoice_intervals_count(90, date) +
                self.get_invoice_infinit_intervals_count(date))


class PremiumPercents(base.BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.PREMIUMS_PERCENTS

    SOURCES = [relations.RECORD_TYPE.PREMIUMS,
               relations.RECORD_TYPE.REGISTRATIONS_TOTAL]


class InfinitPremiums(ActiveBase):
    TYPE = relations.RECORD_TYPE.INFINIT_PREMIUMS

    def get_actual_value(self, date):
        return self.get_invoice_infinit_intervals_count(date)

    def get_invoice_infinit_intervals_count(self, date):
        return bank_prototypes.InvoicePrototype._db_filter(django_models.Q(state=bank_relations.INVOICE_STATE.CONFIRMED) | django_models.Q(state=bank_relations.INVOICE_STATE.FORCED),
                                                           self.db_date_lte('created_at', date),
                                                           operation_uid__contains='<%sinfinit' % shop_relations.GOODS_GROUP.PREMIUM.uid_prefix,
                                                           sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                           currency=bank_relations.CURRENCY_TYPE.PREMIUM).values_list('created_at', flat=True).count()

    def get_restored_value(self, date):
        if conf.settings.PAYMENTS_START_DATE.date() > date:
            return 0
        return self.get_invoice_infinit_intervals_count(date)


class ActiveAccountsBase(ActiveBase):
    DAYS = NotImplemented

    def get_actual_value(self, date):
        barrier = (date +
                   datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT) -
                   datetime.timedelta(days=self.DAYS - 1))
        return accounts_prototypes.AccountPrototype._db_filter(self.db_date_gte('active_end_at', date=barrier),
                                                               is_bot=False,
                                                               is_fast=False).count()

    @classmethod
    def get_restored_value(cls, date):
        return 0


class Active(ActiveAccountsBase):
    TYPE = relations.RECORD_TYPE.ACTIVE
    DAYS = accounts_conf.settings.ACTIVE_STATE_TIMEOUT / (24 * 60 * 60)


class DAU(ActiveAccountsBase):
    TYPE = relations.RECORD_TYPE.DAU
    DAYS = 1


class MAU(ActiveAccountsBase):
    TYPE = relations.RECORD_TYPE.MAU
    DAYS = 30


class ActiveOlderBase(ActiveBase):
    DAYS = NotImplemented

    def get_actual_value(self, date):
        barrier = (date +
                   datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT))

        accounts = accounts_prototypes.AccountPrototype._db_filter(self.db_date_gte('active_end_at', date=barrier),
                                                                   is_bot=False,
                                                                   is_fast=False).values_list('created_at', 'active_end_at')
        return len([True
                    for created_at, active_end_at in accounts
                    if (active_end_at - created_at - datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT)).days >= self.DAYS])

    @classmethod
    def get_restored_value(cls, date):
        return 0


class ActiveOlderDay(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_DAY
    DAYS = 1


class ActiveOlderWeek(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_WEEK
    DAYS = 7


class ActiveOlderMonth(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_MONTH
    DAYS = 30


class ActiveOlder3Month(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_3_MONTH
    DAYS = 90


class ActiveOlder6Month(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_6_MONTH
    DAYS = 180


class ActiveOlderYear(ActiveOlderBase):
    TYPE = relations.RECORD_TYPE.ACTIVE_OLDER_YEAR
    DAYS = 360
