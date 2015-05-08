# coding: utf-8
import datetime

from django.db import models as django_models

from dext.common.utils import jinja2

from the_tale.finances.market import conf
from the_tale.finances.market import models
from the_tale.finances.market import relations


@jinja2.jinjaglobal
def market_settings():
    return conf.settings


@jinja2.jinjaglobal
def gold_for_period():
    gold_for_period_query = models.Lot.objects.filter(state=relations.LOT_STATE.CLOSED_BY_BUYER,
                                                      closed_at__gt=datetime.datetime.now()-datetime.timedelta(days=conf.settings.HISTORY_TIME))
    return gold_for_period_query.aggregate(gold_for_period=django_models.Sum('price'))['gold_for_period']
