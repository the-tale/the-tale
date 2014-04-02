# coding: utf-8
import datetime

from dext.views import handler

from the_tale.common.utils.resources import Resource


from the_tale.statistics import relations
from the_tale.statistics.prototypes import RecordPrototype
from the_tale.statistics.dygraph import PLOTS_GROUPS


class StatisticsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(StatisticsResource, self).initialize(*args, **kwargs)

    @handler('', method='get')
    def shop(self):
        return self.template('statistics/index.html',
                             {'RECORD_TYPE': relations.RECORD_TYPE,
                              'PLOTS_GROUPS': PLOTS_GROUPS})

    @handler('data', method='get')
    def data(self):
        data = {record.value: RecordPrototype.select_for_js(record,
                                                            date_from=datetime.datetime.min,
                                                            date_to=datetime.datetime.now()) for record in relations.RECORD_TYPE.records}
        return self.json_ok(data=data)
