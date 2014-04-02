# coding: utf-8
import datetime
import collections

from django.db import models

from the_tale.common.utils.logic import days_range

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.accounts.payments.relations import GOODS_GROUP

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics.metrics.base import BaseMetric
from the_tale.statistics import relations
from the_tale.statistics.metrics import exceptions
from the_tale.statistics.conf import statistics_settings


class Payers(BaseMetric):

    TYPE = relations.RECORD_TYPE.PAYERS

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()
        # TODO: probably error created_at__GT????
        query = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                            created_at__gt=last_date.date()+datetime.timedelta(days=1),
                                            sender_type=ENTITY_TYPE.XSOLLA,
                                            currency=CURRENCY_TYPE.PREMIUM).values_list('created_at', 'id')
        invoice_dates = zip(*sorted({(created_at.date(), id_): True for created_at, id_ in query}.keys()))[0]
        invoices_count = collections.Counter(invoice_dates)

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, invoices_count.get(date, 0))


class Income(BaseMetric):

    TYPE = relations.RECORD_TYPE.INCOME

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        query = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                            created_at__gt=last_date.date()+datetime.timedelta(days=1),
                                            sender_type=ENTITY_TYPE.XSOLLA, currency=CURRENCY_TYPE.PREMIUM).values_list('created_at', 'amount')
        invoices = [(created_at.date(), amount) for created_at, amount in query]

        invoices_values = {}
        for created_at, amount in invoices:
            invoices_values[created_at] = invoices_values.get(created_at, 0) + amount

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, invoices_values.get(date, 0))


class IncomeTotal(BaseMetric):

    TYPE = relations.RECORD_TYPE.INCOME_TOTAL

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        query = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                            created_at__gt=last_date.date()+datetime.timedelta(days=1),
                                            sender_type=ENTITY_TYPE.XSOLLA, currency=CURRENCY_TYPE.PREMIUM).values_list('created_at', 'amount')
        invoices = [(created_at.date(), amount) for created_at, amount in query]

        invoices_values = {}
        for created_at, amount in invoices:
            invoices_values[created_at] = invoices_values.get(created_at, 0) + amount

        income = 0

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            income += invoices_values.get(date, 0)
            cls.store_value(date, income)


class ARPPU(BaseMetric):

    TYPE = relations.RECORD_TYPE.ARPPU


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        payers = RecordPrototype._db_filter(type=relations.RECORD_TYPE.PAYERS,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        incomes = RecordPrototype._db_filter(type=relations.RECORD_TYPE.INCOME,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for payer, income in zip(payers, incomes):
            payer_date, payer_count = payer
            income_date, income_count = income

            if payer_date != income_date:
                raise exceptions.UnequalDatesError()

            if payer_count:
                cls.store_value(payer_date, float(income_count) / payer_count)
            else:
                cls.store_value(payer_date, 0.0)


class ARPU(BaseMetric):

    TYPE = relations.RECORD_TYPE.ARPU


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        actives = RecordPrototype._db_filter(type=relations.RECORD_TYPE.DAU,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        incomes = RecordPrototype._db_filter(type=relations.RECORD_TYPE.INCOME,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for active, income in zip(actives, incomes):
            active_date, active_count = active
            income_date, income_count = income

            if active_date != income_date:
                raise exceptions.UnequalDatesError()

            if active_count:
                cls.store_value(active_date, float(income_count) / active_count)
            else:
                cls.store_value(active_date, 0.0)


class DaysBeforePayment(BaseMetric):

    TYPE = relations.RECORD_TYPE.DAYS_BEFORE_PAYMENT
    PERIOD = 1

    @classmethod
    def days(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)

        # do not use accounts registered before payments turn on
        query = query.filter(created_at__gte=max(date-datetime.timedelta(days=cls.PERIOD), statistics_settings.PAYMENTS_START_DATE.date()),
                             created_at__lt=date)
        accounts = dict(query.values_list('id', 'created_at'))

        invoices = list(InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                    sender_type=ENTITY_TYPE.XSOLLA,
                                                    currency=CURRENCY_TYPE.PREMIUM,
                                                    recipient_id__in=accounts.keys()).values_list('created_at', 'recipient_id'))

        account_ids = [id_ for created_at, id_ in invoices]

        if not account_ids:
            return 0

        delays = {account_id: min([(created_at - accounts[account_id]) for created_at, id_ in invoices if id_==account_id])
                  for account_id in account_ids}

        total_time = reduce(lambda s, v: s+v, delays.values(), datetime.timedelta(seconds=0))

        days = float(total_time.total_seconds()) / len(account_ids) / (24*60*60)

        return days

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.days(date))



class ARPNU(BaseMetric):

    TYPE = None
    DAYS = None
    PERIOD = 7

    @classmethod
    def amount(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)
        query = query.filter(created_at__gte=date-datetime.timedelta(days=cls.PERIOD), created_at__lt=date)
        accounts = list(query.values_list('id', 'created_at'))

        if not accounts:
            return 0

        total_income = 0
        for account_id, created_at in accounts:
            income = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                 created_at__lte=created_at + datetime.timedelta(days=cls.DAYS),
                                                 sender_type=ENTITY_TYPE.XSOLLA,
                                                 currency=CURRENCY_TYPE.PREMIUM,
                                                 recipient_id=account_id).aggregate(income=models.Sum('amount'))['income']
            if income is not None:
                total_income += income

        return float(total_income) / len(accounts)

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()-datetime.timedelta(days=cls.DAYS)):
            cls.store_value(date, cls.amount(date))


class ARPNUWeek(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_WEEK
    DAYS = 7

class ARPNUMonth(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_MONTH
    DAYS = 30

class ARPNU3Month(ARPNU):
    TYPE = relations.RECORD_TYPE.APRNU_3_MONTH
    DAYS = 90


class LTV(BaseMetric):
    TYPE = relations.RECORD_TYPE.LTV
    PERIOD = 7

    @classmethod
    def amount(cls, date):
        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)
        query = query.filter(created_at__gte=date-datetime.timedelta(days=cls.PERIOD), created_at__lt=date)
        accounts_ids = list(query.values_list('id', flat=True))

        if not accounts_ids:
            return 0

        total_income = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                   sender_type=ENTITY_TYPE.XSOLLA,
                                                   currency=CURRENCY_TYPE.PREMIUM,
                                                   recipient_id__in=accounts_ids).aggregate(income=models.Sum('amount'))['income']

        if total_income is None:
            return 0

        return float(total_income) / len(accounts_ids)


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.amount(date))



class IncomeFromGroupsBase(BaseMetric):
    TYPE = None
    PERIOD = 30

    @classmethod
    def filter_recipients(cls, ids):
        raise NotImplementedError

    @classmethod
    def amount(cls, date):
        invoices = list(InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                    created_at__lt=date,
                                                    created_at__gte=date-datetime.timedelta(days=cls.PERIOD),
                                                    sender_type=ENTITY_TYPE.XSOLLA,
                                                    currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount'))

        if not invoices:
            return 0

        recipients = set(cls.filter_recipients(zip(*invoices)[0]))

        return sum([amount for recipient_id, amount in invoices if recipient_id in recipients], 0)


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.amount(date))


class IncomeFromForum(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_FORUM

    @classmethod
    def filter_recipients(cls, ids):
        return set(AccountPrototype._db_filter(forum_posts__author__in=ids).values_list('id', flat=True))


class IncomeFromSilent(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SILENT

    @classmethod
    def filter_recipients(cls, ids):
        return set(AccountPrototype._db_exclude(forum_posts__author__in=ids).values_list('id', flat=True))


class IncomeFromGuildMembers(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GUILD_MEMBERS

    @classmethod
    def filter_recipients(cls, ids):
        return set(AccountPrototype._db_filter(membership__account__in=ids).values_list('id', flat=True))


class IncomeFromSingles(IncomeFromGroupsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_SINGLES

    @classmethod
    def filter_recipients(cls, ids):
        return set(AccountPrototype._db_exclude(membership__account__in=ids).values_list('id', flat=True))



class IncomeFromGoodsBase(BaseMetric):
    TYPE = None
    GROUP = None
    DAYS = 1

    @classmethod
    def selector(cls):
        return models.Q(operation_uid__contains='<%s' % cls.GROUP.uid_prefix)

    @classmethod
    def amount(cls, date):
        income = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                             cls.selector(),
                                             created_at__lt=date,
                                             created_at__gte=date-datetime.timedelta(days=cls.DAYS),
                                             sender_type=ENTITY_TYPE.GAME_LOGIC,
                                             currency=CURRENCY_TYPE.PREMIUM).aggregate(income=models.Sum('amount'))['income']

        if income is None:
            return 0

        return -income

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.amount(date))


class IncomeFromGoodsPremium(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREMIUM
    GROUP = GOODS_GROUP.PREMIUM

class IncomeFromGoodsEnergy(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ENERGY
    GROUP = GOODS_GROUP.ENERGY

class IncomeFromGoodsChest(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CHEST
    GROUP = GOODS_GROUP.CHEST

class IncomeFromGoodsPeferences(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCES
    GROUP = GOODS_GROUP.PREFERENCES

class IncomeFromGoodsPreferencesReset(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_PREFERENCE_RESET
    GROUP = GOODS_GROUP.PREFERENCE_RESET

class IncomeFromGoodsHabits(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_HABITS
    GROUP = GOODS_GROUP.HABITS

class IncomeFromGoodsAbilities(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_ABILITIES
    GROUP = GOODS_GROUP.ABILITIES

class IncomeFromGoodsClans(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_CLANS
    GROUP = GOODS_GROUP.CLANS

class IncomeFromGoodsOther(IncomeFromGoodsBase):
    TYPE = relations.RECORD_TYPE.INCOME_FROM_GOODS_OTHER
    GROUP = None

    @classmethod
    def selector(cls):
        return ~(models.Q(operation_uid__contains='<%s' % GOODS_GROUP.PREMIUM.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.ENERGY.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.CHEST.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.PREFERENCES.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.PREFERENCE_RESET.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.HABITS.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.ABILITIES.uid_prefix) |
                 models.Q(operation_uid__contains='<%s' % GOODS_GROUP.CLANS.uid_prefix) )



class PU(BaseMetric):

    TYPE = relations.RECORD_TYPE.PU

    @classmethod
    def get_value(cls, date):
        return InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                           created_at__lte=date+datetime.timedelta(days=1),
                                           sender_type=ENTITY_TYPE.XSOLLA,
                                           currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id').order_by('recipient_id').distinct().count()

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.get_value(date))


class PUPercents(BaseMetric):

    TYPE = relations.RECORD_TYPE.PU_PERCENTS


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        payers = RecordPrototype._db_filter(type=relations.RECORD_TYPE.PU,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        accounts = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REGISTRATIONS_TOTAL,
                                           date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for payer, account in zip(payers, accounts):
            payer_date, payer_count = payer
            account_date, account_count = account

            if payer_date != account_date:
                raise exceptions.UnequalDatesError()

            if payer_count:
                cls.store_value(payer_date, float(payer_count) / account_count * 100)
            else:
                cls.store_value(payer_date, 0.0)


class IncomeGroupBase(BaseMetric):
    TYPE = None
    BORDERS = (None, None)

    @classmethod
    def _get_incomes(cls, date):
        incomes = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                              created_at__lte=date+datetime.timedelta(days=1),
                                              sender_type=ENTITY_TYPE.XSOLLA,
                                              currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount')

        accounts_incomes = {}
        for recipient_id, amount in incomes:
            accounts_incomes[recipient_id] = accounts_incomes.get(recipient_id, 0) + amount

        return len([True
                    for amount in accounts_incomes.itervalues()
                    if cls.BORDERS[0] < amount <= cls.BORDERS[1]])


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls._get_incomes(date))



class IncomeGroup0_500(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500
    BORDERS = (0, 500)

class IncomeGroup500_1000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000
    BORDERS = (500, 1000)

class IncomeGroup1000_2500(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500
    BORDERS = (1000, 2500)

class IncomeGroup2500_10000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000
    BORDERS = (2500, 10000)

class IncomeGroup10000(IncomeGroupBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000
    BORDERS = (10000, 9999999999999)


class IncomeGroupPercentsBase(BaseMetric):
    TYPE = None
    COMPARE_TO = None


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        payers = RecordPrototype._db_filter(type=relations.RECORD_TYPE.PU,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        accounts = RecordPrototype._db_filter(type=cls.COMPARE_TO,
                                              date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for payer, account in zip(payers, accounts):
            payer_date, payer_count = payer
            account_date, account_count = account

            if payer_date != account_date:
                raise exceptions.UnequalDatesError()

            if payer_count:
                cls.store_value(payer_date, float(account_count) / payer_count * 100)
            else:
                cls.store_value(payer_date, 0.0)


class IncomeGroup0_500Percents(IncomeGroupPercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_0_500

class IncomeGroup500_1000Percents(IncomeGroupPercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_500_1000

class IncomeGroup1000_2500Percents(IncomeGroupPercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_1000_2500

class IncomeGroup2500_10000Percents(IncomeGroupPercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_2500_10000

class IncomeGroup10000Percents(IncomeGroupPercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_10000


class IncomeGroupIncomeBase(BaseMetric):
    TYPE = None
    BORDERS = (None, None)

    @classmethod
    def _get_incomes(cls, date):
        incomes = InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                              created_at__lte=date+datetime.timedelta(days=1),
                                              sender_type=ENTITY_TYPE.XSOLLA,
                                              currency=CURRENCY_TYPE.PREMIUM).values_list('recipient_id', 'amount')

        accounts_incomes = {}
        for recipient_id, amount in incomes:
            accounts_incomes[recipient_id] = accounts_incomes.get(recipient_id, 0) + amount

        return sum([amount
                    for amount in accounts_incomes.itervalues()
                    if cls.BORDERS[0] < amount <= cls.BORDERS[1]], 0)


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls._get_incomes(date))



class IncomeGroupIncome0_500(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME
    BORDERS = (0, 500)

class IncomeGroupIncome500_1000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME
    BORDERS = (500, 1000)

class IncomeGroupIncome1000_2500(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME
    BORDERS = (1000, 2500)

class IncomeGroupIncome2500_10000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME
    BORDERS = (2500, 10000)

class IncomeGroupIncome10000(IncomeGroupIncomeBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME
    BORDERS = (10000, 9999999999999)


class IncomeGroupIncomePercentsBase(BaseMetric):
    TYPE = None
    COMPARE_TO = None


    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        payers = RecordPrototype._db_filter(type=relations.RECORD_TYPE.INCOME_TOTAL,
                                            date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        accounts = RecordPrototype._db_filter(type=cls.COMPARE_TO,
                                              date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for payer, account in zip(payers, accounts):
            payer_date, payer_count = payer
            account_date, account_count = account

            if payer_date != account_date:
                raise exceptions.UnequalDatesError()

            if payer_count:
                cls.store_value(payer_date, float(account_count) / payer_count * 100)
            else:
                cls.store_value(payer_date, 0.0)


class IncomeGroupIncome0_500Percents(IncomeGroupIncomePercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_0_500_INCOME

class IncomeGroupIncome500_1000Percents(IncomeGroupIncomePercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_500_1000_INCOME

class IncomeGroupIncome1000_2500Percents(IncomeGroupIncomePercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_1000_2500_INCOME

class IncomeGroupIncome2500_10000Percents(IncomeGroupIncomePercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_2500_10000_INCOME

class IncomeGroupIncome10000Percents(IncomeGroupIncomePercentsBase):
    TYPE = relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME_PERCENTS
    COMPARE_TO = relations.RECORD_TYPE.INCOME_GROUP_10000_INCOME
