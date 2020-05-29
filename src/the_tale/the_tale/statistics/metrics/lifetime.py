
import smart_imports

smart_imports.all()


class AliveAfterBase(base.BaseMetric):
    TYPE = None
    FULL_CLEAR_RECUIRED = True
    DAYS = NotImplemented

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(self.db_date_day('created_at', date),
                                                                is_fast=False,
                                                                is_bot=False)
        return len([True
                    for active_end_at, created_at in query.values_list('active_end_at', 'created_at')
                    if (active_end_at - created_at - datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT)).days >= self.DAYS])

    def _get_interval(self):
        return (self.free_date, (datetime.datetime.now() - datetime.timedelta(days=self.DAYS)).date())


class AliveAfterDay(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_DAY
    DAYS = 1


class AliveAfterWeek(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_WEEK
    DAYS = 7


class AliveAfterMonth(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_MONTH
    DAYS = 30


class AliveAfter3Month(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_3_MONTH
    DAYS = 90


class AliveAfter6Month(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_6_MONTH
    DAYS = 180


class AliveAfterYear(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_YEAR
    DAYS = 360


class AliveAfter0(AliveAfterBase):
    TYPE = relations.RECORD_TYPE.ALIVE_AFTER_0
    DAYS = 0


class Lifetime(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.LIFETIME
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(self.db_date_day('created_at', date=date),
                                                                is_fast=False,
                                                                is_bot=False)

        lifetimes = [active_end_at - created_at - datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT - 1)
                     for active_end_at, created_at in query.values_list('active_end_at', 'created_at')]

        # filter «strange» lifetimes
        lifetimes = [lifetime for lifetime in lifetimes if lifetime > datetime.timedelta(seconds=0)]

        if not lifetimes:
            return 0

        total_time = functools.reduce(lambda s, v: s + v, lifetimes, datetime.timedelta(seconds=0))
        return float(total_time.total_seconds() / (24 * 60 * 60)) / len(lifetimes)


class LifetimePercent(base.BaseMetric):
    TYPE = relations.RECORD_TYPE.LIFETIME_PERCENT
    FULL_CLEAR_RECUIRED = True

    def get_value(self, date):
        query = accounts_prototypes.AccountPrototype._db_filter(self.db_date_day('created_at', date=date),
                                                                is_fast=False,
                                                                is_bot=False)
        lifetimes = [active_end_at - created_at - datetime.timedelta(seconds=accounts_conf.settings.ACTIVE_STATE_TIMEOUT)
                     for active_end_at, created_at in query.values_list('active_end_at', 'created_at')]

        if not lifetimes:
            return 0

        total_time = functools.reduce(lambda s, v: s + v, lifetimes, datetime.timedelta(seconds=0))
        lifetime = float(total_time.total_seconds()) / len(lifetimes)
        maximum = (datetime.datetime.now().date() - date).total_seconds()
        return lifetime / maximum * 100
