# coding: utf-8
import datetime

from django.db import models

from the_tale.common.utils.logic import days_range

from the_tale.accounts.prototypes import AccountPrototype, RandomPremiumRequestPrototype
from the_tale.accounts.conf import accounts_settings

from the_tale.accounts.payments.relations import GOODS_GROUP

from the_tale.bank.prototypes import InvoicePrototype
from the_tale.bank.relations import INVOICE_STATE, ENTITY_TYPE, CURRENCY_TYPE

from the_tale.statistics.metrics.base import BaseMetric
from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics import relations
from the_tale.statistics import exceptions
from the_tale.statistics.conf import statistics_settings



class ActiveBase(BaseMetric):

    TYPE = None

    @classmethod
    def is_actual_date(cls, date):
        return date == datetime.datetime.now().date() - datetime.timedelta(days=1)

    @classmethod
    def get_value(cls, date):

        if cls.is_actual_date(date):
            return cls.get_actual_value(date)

        return cls.get_restored_value(date)

    def get_actual_value(cls, date):
        raise NotImplementedError()

    def get_restored_value(cls, date):
        raise NotImplementedError()

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, cls.get_value(date))


class Premiums(ActiveBase):
    TYPE = relations.RECORD_TYPE.PREMIUMS

    @classmethod
    def get_actual_value(cls, date):
        return AccountPrototype._db_filter(premium_end_at__gt=date).count()

    @classmethod
    def get_invoice_intervals_count(cls, days, date):
        starts = list(InvoicePrototype._db_filter(models.Q(state=INVOICE_STATE.CONFIRMED)|models.Q(state=INVOICE_STATE.FORCED),
                                                  operation_uid__contains='<%s%d' % (GOODS_GROUP.PREMIUM.uid_prefix, days),
                                                  sender_type=ENTITY_TYPE.GAME_LOGIC,
                                                  currency=CURRENCY_TYPE.PREMIUM).values_list('created_at', flat=True))
        return len([True
                    for created_at in starts
                    if created_at <= datetime.datetime.combine(date, datetime.time()) < created_at + datetime.timedelta(days=days)] )

    @classmethod
    def get_chest_intervals_count(cls, date):
        starts = RandomPremiumRequestPrototype._db_all().values_list('created_at', flat=True)
        return len([True
                    for created_at in starts
                    if created_at <= datetime.datetime.combine(date, datetime.time()) < (created_at + datetime.timedelta(days=30))] )

    @classmethod
    def get_restored_value(cls, date):
        if statistics_settings.PAYMENTS_START_DATE.date() > date:
            return 0
        return ( 30 + # lottery
                 cls.get_chest_intervals_count(date) +
                 cls.get_invoice_intervals_count(7, date) +
                 cls.get_invoice_intervals_count(15, date) +
                 cls.get_invoice_intervals_count(30, date) +
                 cls.get_invoice_intervals_count(90, date) )


class PremiumPercents(BaseMetric):

    TYPE = relations.RECORD_TYPE.PREMIUMS_PERCENTS

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        premiums = RecordPrototype._db_filter(type=relations.RECORD_TYPE.PREMIUMS,
                                              date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        accounts = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REGISTRATIONS_TOTAL,
                                              date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for premium, account in zip(premiums, accounts):
            premium_date, premium_count = premium
            account_date, account_count = account

            if premium_date != account_date:
                raise exceptions.UnequalDatesError()

            if account_count:
                cls.store_value(premium_date, float(premium_count * 100) / account_count)
            else:
                cls.store_value(premium_date, 0.0)


class ActiveBase(ActiveBase):
    TYPE = None
    PERIOD = None

    @classmethod
    def get_actual_value(cls, date):
        barrier = (date +
                   datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT) -
                   datetime.timedelta(days=cls.PERIOD-1))
        return AccountPrototype._db_filter(is_bot=False,
                                           is_fast=False,
                                           active_end_at__gt=barrier).count()

    @classmethod
    def get_restored_value(cls, date):
        return 0


class Active(ActiveBase):
    TYPE = relations.RECORD_TYPE.ACTIVE
    PERIOD = accounts_settings.ACTIVE_STATE_TIMEOUT / (24*60*60)

class DAU(ActiveBase):
    TYPE = relations.RECORD_TYPE.DAU
    PERIOD = 1

class MAU(ActiveBase):
    TYPE = relations.RECORD_TYPE.MAU
    PERIOD = 30
