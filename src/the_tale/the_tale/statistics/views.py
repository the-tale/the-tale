# coding: utf-8

from dext.views import handler

from the_tale.common.utils.resources import Resource


from the_tale.statistics import relations
from the_tale.statistics import models
from the_tale.statistics.dygraph import PLOTS_GROUPS


class StatisticsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(StatisticsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def index(self):
        return self.template('statistics/index.html',
                             {'RECORD_TYPE': relations.RECORD_TYPE,
                              'PLOTS_GROUPS': PLOTS_GROUPS,
                              'statistics_data': models.FullStatistics.objects.latest('created_at').data})
