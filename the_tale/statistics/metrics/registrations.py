# coding: utf-8
import datetime
import collections

from the_tale.common.utils.logic import days_range

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics.metrics.base import BaseMetric
from the_tale.statistics import relations
from the_tale.statistics.metrics import exceptions



class RegistrationsCompleted(BaseMetric):

    TYPE = relations.RECORD_TYPE.REGISTRATIONS_COMPLETED

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        registrations_dates = AccountPrototype._db_filter(created_at__gt=last_date.date()+datetime.timedelta(days=1), is_fast=False, is_bot=False).values_list('created_at', flat=True)
        registrations_count = collections.Counter(date.date() for date in registrations_dates)

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, registrations_count.get(date, 0))


class AccountsTotal(BaseMetric):

    TYPE = relations.RECORD_TYPE.REGISTRATIONS_TOTAL

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)

        count = query.filter(created_at__lte=last_date.date()+datetime.timedelta(days=1)).count()

        registrations_dates = query.filter(created_at__gt=last_date.date()+datetime.timedelta(days=1)).values_list('created_at', flat=True)
        registrations_count = collections.Counter(date.date() for date in registrations_dates)

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            count += registrations_count.get(date, 0)
            cls.store_value(date, count)


class RegistrationsTries(BaseMetric):

    TYPE = relations.RECORD_TYPE.REGISTRATIONS_TRIES

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        registrations_dates = AccountPrototype._db_filter(created_at__gt=last_date.date()+datetime.timedelta(days=1),
                                                          is_bot=False).order_by('created_at').values_list('created_at', 'id')
        registrations_count = {}

        last_id = 0
        for date, id_ in registrations_dates:
            registrations_count[date.date()] = registrations_count.get(date.date(), 0) + (id_-last_id)
            last_id = id_

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, registrations_count.get(date, 0))


class RegistrationsCompletedPercents(BaseMetric):

    TYPE = relations.RECORD_TYPE.REGISTRATIONS_COMPLETED_PERCENTS

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        registrations_completed = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REGISTRATIONS_COMPLETED,
                                                             date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        registrations_tires = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REGISTRATIONS_TRIES,
                                                         date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for completed, tries in zip(registrations_completed, registrations_tires):
            completed_date, completed_count = completed
            tries_date, tries_count = tries

            if completed_date != tries_date:
                raise exceptions.UnequalDatesError()

            if tries_count:
                cls.store_value(completed_date, float(completed_count * 100) / tries_count)
            else:
                cls.store_value(completed_date, 0.0)




class Referrals(BaseMetric):

    TYPE = relations.RECORD_TYPE.REFERRALS

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        referrals_dates = AccountPrototype._db_filter(created_at__gt=last_date.date()+datetime.timedelta(days=1),
                                                      is_fast=False, is_bot=False).exclude(referral_of=None).values_list('created_at', flat=True)
        referrals_count = collections.Counter(date.date() for date in referrals_dates)

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            cls.store_value(date, referrals_count.get(date, 0))


class ReferralsTotal(BaseMetric):

    TYPE = relations.RECORD_TYPE.REFERRALS_TOTAL

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        query = AccountPrototype._db_filter(is_fast=False, is_bot=False).exclude(referral_of=None)

        count = query.filter(created_at__lte=last_date.date()+datetime.timedelta(days=1)).count()

        referrals_dates = query.filter(created_at__gt=last_date.date()+datetime.timedelta(days=1)).values_list('created_at', flat=True)
        referrals_count = collections.Counter(date.date() for date in referrals_dates)

        for date in days_range(last_date+datetime.timedelta(days=1), datetime.datetime.now()):
            count += referrals_count.get(date, 0)
            cls.store_value(date, count)


class ReferralsPercents(BaseMetric):

    TYPE = relations.RECORD_TYPE.REFERRALS_PERCENTS

    @classmethod
    def complete_values(cls):
        last_date = cls.last_date()

        registrations_total = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REGISTRATIONS_TOTAL,
                                                         date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')

        referrals_total = RecordPrototype._db_filter(type=relations.RECORD_TYPE.REFERRALS_TOTAL,
                                                     date__gt=last_date.date()).order_by('date').values_list('date', 'value_int')


        for registrations, referrals in zip(registrations_total, referrals_total):
            registrations_date, registrations_count = registrations
            referrals_date, referrals_count = referrals

            if registrations_date != referrals_date:
                raise exceptions.UnequalDatesError()

            if registrations_count:
                cls.store_value(registrations_date, float(referrals_count * 100) / registrations_count)
            else:
                cls.store_value(registrations_date, 0.0)
