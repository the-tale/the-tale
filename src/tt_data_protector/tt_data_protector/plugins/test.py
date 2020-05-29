
import copy

from .. import relations


class Plugin:
    __slots__ = ('presets', 'report_counters', 'deletion_counters', 'uid')

    def __init__(self, presets):
        self.presets = presets
        self.report_counters = {}
        self.deletion_counters = {}

    def get_presets(self, id):
        return self.presets.get(str(id), {'report': [('xxx', id)],
                                          'success_on_step': 1})

    async def fill_subreport(self, subreport):
        data = copy.copy(subreport.data)

        id = (subreport.id, data['id'])

        self.report_counters[id] = self.report_counters.get(id, 0) + 1

        presets = self.get_presets(data['id'])

        if self.report_counters[id] != presets['success_on_step']:
            return None

        new_data = [(subreport.source, data_type, data_value)
                    for data_type, data_value in presets['report']]

        data['report'].extend(new_data)

        return subreport.replace(state=relations.REPORT_STATE.READY,
                                 data=data)

    async def process_deletion_request(self, request):

        data = copy.copy(request.data)

        id = (request.id, data['id'])

        self.deletion_counters[id] = self.deletion_counters.get(id, 0) + 1

        presets = self.get_presets(data['id'])

        if self.deletion_counters[id] != presets['success_on_step']:
            data['counter'] = self.deletion_counters[id]
            return False, request.replace(data=data)

        return True, None


async def construct_plugin(config):
    return Plugin(presets=config['presets'])
