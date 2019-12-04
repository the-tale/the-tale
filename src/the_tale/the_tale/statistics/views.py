
import smart_imports

smart_imports.all()


class StatisticsResource(utils_resources.Resource):

    def initialize(self, *args, **kwargs):
        super(StatisticsResource, self).initialize(*args, **kwargs)

    @old_views.handler('', method='get')
    def index(self):
        return self.template('statistics/index.html',
                             {'RECORD_TYPE': relations.RECORD_TYPE,
                              'PLOTS_GROUPS': dygraph.PLOTS_GROUPS,
                              'statistics_data': models.FullStatistics.objects.latest('created_at').data})
