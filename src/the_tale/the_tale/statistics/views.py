# coding: utf-8

from dext.views import handler
from dext.settings import settings

from the_tale.common.utils.resources import Resource


from the_tale.statistics import relations
from the_tale.statistics.dygraph import PLOTS_GROUPS
from the_tale.statistics.conf import statistics_settings


class StatisticsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(StatisticsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def shop(self):
        return self.template('statistics/index.html',
                             {'RECORD_TYPE': relations.RECORD_TYPE,
                              'PLOTS_GROUPS': PLOTS_GROUPS,
                              'js_data_file': statistics_settings.JS_DATA_FILE_URL % settings.get(statistics_settings.JS_DATA_FILE_VERSION_KEY, 0)})
