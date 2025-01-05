
import copy

from .. import relations


class Plugin:
    __slots__ = ()

    def __init__(self):
        pass

    async def fill_subreport(self, subreport):
        data = copy.copy(subreport.data)

        new_data = []

        data['report'].extend(new_data)

        return subreport.replace(state=relations.REPORT_STATE.READY,
                                 data=data)

    async def process_deletion_request(self, request):
        return True, None


async def construct_plugin(config):
    return Plugin()
