# coding: utf-8
import collections

from the_tale.common.utils.logic import days_range

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.statistics.metrics.base import BaseMetric, BasePercentsCombination
from the_tale.statistics import relations



class RegistrationsCompleted(BaseMetric):
    TYPE = relations.RECORD_TYPE.REGISTRATIONS_COMPLETED
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(RegistrationsCompleted, self).initialize()
        registrations_dates = AccountPrototype._db_filter(is_fast=False, is_bot=False).values_list('created_at', flat=True)
        self.registrations_count = collections.Counter(date.date() for date in registrations_dates)

    def get_value(self, date):
        return self.registrations_count.get(date, 0)


class AccountsTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.REGISTRATIONS_TOTAL

    def initialize(self):
        super(AccountsTotal, self).initialize()

        query = AccountPrototype._db_filter(is_fast=False, is_bot=False)

        count = query.filter(self.db_date_lt('created_at')).count()

        registrations_dates = query.filter(self.db_date_gte('created_at')).values_list('created_at', flat=True)
        registrations_count = collections.Counter(date.date() for date in registrations_dates)

        self.counts = {}
        for date in days_range(*self._get_interval()):
            count += registrations_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts.get(date, 0)


class RegistrationsTries(BaseMetric):
    TYPE = relations.RECORD_TYPE.REGISTRATIONS_TRIES
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(RegistrationsTries, self).initialize()

        registrations_dates = AccountPrototype._db_filter(is_bot=False).order_by('created_at').values_list('created_at', 'id')
        self.registrations_count = {}

        last_id = 0
        for date, id_ in registrations_dates:
            self.registrations_count[date.date()] = self.registrations_count.get(date.date(), 0) + (id_-last_id)
            last_id = id_

    def get_value(self, date):
        return self.registrations_count.get(date, 0)


class RegistrationsCompletedPercents(BasePercentsCombination):
    TYPE = relations.RECORD_TYPE.REGISTRATIONS_COMPLETED_PERCENTS
    FULL_CLEAR_RECUIRED = True
    SOURCES = [relations.RECORD_TYPE.REGISTRATIONS_COMPLETED,
               relations.RECORD_TYPE.REGISTRATIONS_TRIES]


class Referrals(BaseMetric):
    TYPE = relations.RECORD_TYPE.REFERRALS
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Referrals, self).initialize()
        referrals_dates = AccountPrototype._db_filter(is_fast=False, is_bot=False).exclude(referral_of=None).values_list('created_at', flat=True)
        self.referrals_count = collections.Counter(date.date() for date in referrals_dates)

    def get_value(self, date):
        return self.referrals_count.get(date, 0)


class ReferralsTotal(BaseMetric):
    TYPE = relations.RECORD_TYPE.REFERRALS_TOTAL
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(ReferralsTotal, self).initialize()
        referrals_dates = AccountPrototype._db_filter(is_fast=False, is_bot=False).exclude(referral_of=None).values_list('created_at', flat=True)
        referrals_count = collections.Counter(date.date() for date in referrals_dates)

        self.counts = {}

        count = 0
        for date in days_range(*self._get_interval()):
            count += referrals_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts[date]


class ReferralsPercents(BasePercentsCombination):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.REFERRALS_PERCENTS
    SOURCES = [relations.RECORD_TYPE.REFERRALS_TOTAL,
               relations.RECORD_TYPE.REGISTRATIONS_TOTAL ]
