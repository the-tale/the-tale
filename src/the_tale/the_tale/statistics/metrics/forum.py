# coding: utf-8

import datetime
import collections

from the_tale.common.utils.logic import days_range

from the_tale.statistics.metrics.base import BaseMetric, BaseFractionCombination
from the_tale.statistics import relations

from the_tale.forum import models



class Posts(BaseMetric):
    TYPE = relations.RECORD_TYPE.FORUM_POSTS
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Posts, self).initialize()
        posts_dates = models.Post.objects.all().values_list('created_at', flat=True)
        self.posts_dates = collections.Counter(date.date() for date in posts_dates)

    def get_value(self, date):
        return self.posts_dates.get(date, 0)


class PostsInMonth(Posts):
    TYPE = relations.RECORD_TYPE.FORUM_POSTS_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.posts_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class PostsTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FORUM_POSTS_TOTAL

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



class Threads(BaseMetric):
    TYPE = relations.RECORD_TYPE.FORUM_THREADS
    FULL_CLEAR_RECUIRED = True

    def initialize(self):
        super(Threads, self).initialize()
        threads_dates = models.Thread.objects.all().values_list('created_at', flat=True)
        self.threads_dates = collections.Counter(date.date() for date in threads_dates)

    def get_value(self, date):
        return self.threads_dates.get(date, 0)


class ThreadsInMonth(Threads):
    TYPE = relations.RECORD_TYPE.FORUM_THREADS_IN_MONTH
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        return sum(self.threads_dates.get(date - datetime.timedelta(days=i), 0) for i in range(30) )


class ThreadsTotal(BaseMetric):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FORUM_THREADS_TOTAL

    def initialize(self):
        super(ThreadsTotal, self).initialize()

        query = models.Thread.objects.all()

        count = query.filter(self.db_date_lt('created_at')).count()

        threads_dates = query.filter(self.db_date_gte('created_at')).values_list('created_at', flat=True)
        threads_count = collections.Counter(date.date() for date in threads_dates)

        self.counts = {}
        for date in days_range(*self._get_interval()):
            count += threads_count.get(date, 0)
            self.counts[date] = count

    def get_value(self, date):
        return self.counts.get(date, 0)



class PostsPerThreadInMonth(BaseFractionCombination):
    FULL_CLEAR_RECUIRED = True
    TYPE = relations.RECORD_TYPE.FORUM_POSTS_PER_THREAD_IN_MONTH
    SOURCES = [relations.RECORD_TYPE.FORUM_POSTS_IN_MONTH, relations.RECORD_TYPE.FORUM_THREADS_IN_MONTH]
