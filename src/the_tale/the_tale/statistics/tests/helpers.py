# coding: utf-8


from the_tale.statistics.metrics.base import BaseMetric
from the_tale.statistics import relations


class TestMetric(BaseMetric):
    TYPE = relations.RECORD_TYPE.TEST_INT

    def __init__(self):
        super(TestMetric, self).__init__()
        self.value_counter = 0

    def get_value(self, date):
        self.value_counter += 1
        return self.value_counter
