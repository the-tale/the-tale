# coding: utf-8


import datetime
import collections

from the_tale.common.utils.logic import days_range

from the_tale.statistics.metrics.base import BaseMetric, BaseFractionCombination
from the_tale.statistics import relations

from the_tale.blogs import models



class Posts(BaseMetric):
    TYPE = relations.RECORD_TYPE.FOLCLOR_POSTS
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Posts, self).initialize()
        posts_dates = models.Post.objects.all().values_list('created_at', flat=True)
        self.posts_dates = collections.Counter(date.date() for date in posts_dates)

    def get_value(self, date):
        return self.posts_dates.get(date, 0)


class PostsInMonth(Posts):
    TYPE = relations.RECORD_TYPE.FOLCLOR_POSTS_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.posts_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class PostsTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FOLCLOR_POSTS_TOTAL

    def initialize(self):
        super(PostsTotal, self).initialize()

        query = models.Post.objects.all()

        count = query.filter(self.db_date_lt('created_at')).count()

        posts_dates = query.filter(self.db_date_gte('created_at')).values_list('created_at', flat=True)
        posts_count = collections.Counter(date.date() for date in posts_dates)

        self.counts = {}
        for date in days_range(*self._get_interval()):
            count += posts_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts.get(date, 0)



class Votes(BaseMetric):
    TYPE = relations.RECORD_TYPE.FOLCLOR_VOTES
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Votes, self).initialize()
        votes_dates = models.Vote.objects.all().values_list('created_at', flat=True)
        self.votes_dates = collections.Counter(date.date() for date in votes_dates)

    def get_value(self, date):
        return self.votes_dates.get(date, 0)


class VotesInMonth(Votes):
    TYPE = relations.RECORD_TYPE.FOLCLOR_VOTES_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.votes_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class VotesTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FOLCLOR_VOTES_TOTAL

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


class VotesPerPostInMonth(BaseFractionCombination):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FOLCLOR_VOTES_PER_POST_IN_MONTH
    SOURCES = [relations.RECORD_TYPE.FOLCLOR_VOTES_IN_MONTH, relations.RECORD_TYPE.FOLCLOR_POSTS_IN_MONTH]
