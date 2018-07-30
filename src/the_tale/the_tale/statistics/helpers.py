
import smart_imports

smart_imports.all()


class TestMetric(statistics_metrics_base.BaseMetric):
    TYPE = relations.RECORD_TYPE.TEST_INT

    def __init__(self):
        super(TestMetric, self).__init__()
        self.value_counter = 0

    def get_value(self, date):
        self.value_counter += 1
        return self.value_counter
