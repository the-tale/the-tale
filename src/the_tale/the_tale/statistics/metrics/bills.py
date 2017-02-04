# coding: utf-8


import datetime
import collections

from the_tale.common.utils.logic import days_range

from the_tale.statistics.metrics.base import BaseMetric, BaseFractionCombination
from the_tale.statistics import relations

from the_tale.game.bills import models



class Bills(BaseMetric):
    TYPE = relations.RECORD_TYPE.BILLS
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Bills, self).initialize()
        bills_dates = models.Bill.objects.all().values_list('created_at', flat=True)
        self.bills_dates = collections.Counter(date.date() for date in bills_dates)

    def get_value(self, date):
        return self.bills_dates.get(date, 0)


class BillsInMonth(Bills):
    TYPE = relations.RECORD_TYPE.BILLS_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.bills_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class BillsTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.BILLS_TOTAL

    def initialize(self):
        super(BillsTotal, self).initialize()

        query = models.Bill.objects.all()

        count = query.filter(self.db_date_lt('created_at')).count()

        bills_dates = query.filter(self.db_date_gte('created_at')).values_list('created_at', flat=True)
        bills_count = collections.Counter(date.date() for date in bills_dates)

        self.counts = {}
        for date in days_range(*self._get_interval()):
            count += bills_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts.get(date, 0)



class Votes(BaseMetric):
    TYPE = relations.RECORD_TYPE.BILLS_VOTES
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Votes, self).initialize()
        votes_dates = models.Vote.objects.all().values_list('created_at', flat=True)
        self.votes_dates = collections.Counter(date.date() for date in votes_dates)

    def get_value(self, date):
        return self.votes_dates.get(date, 0)


class VotesInMonth(Votes):
    TYPE = relations.RECORD_TYPE.BILLS_VOTES_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.votes_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class VotesTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.BILLS_VOTES_TOTAL

    def initialize(self):
        super(VotesTotal, self).initialize()

        query = models.Vote.objects.all()

        count = query.filter(self.db_date_lt('created_at')).count()

        votes_dates = query.filter(self.db_date_gte('created_at')).values_list('created_at', flat=True)
        votes_count = collections.Counter(date.date() for date in votes_dates)

        self.counts = {}
        for date in days_range(*self._get_interval()):
            count += votes_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts.get(date, 0)


class VotesPerBillInMonth(BaseFractionCombination):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.BILLS_VOTES_PER_BILL_IN_MONTH
    SOURCES = [relations.RECORD_TYPE.BILLS_VOTES_IN_MONTH, relations.RECORD_TYPE.BILLS_IN_MONTH]
