
from . import conf


def guide_context(request):
    return {'guide_settings': conf.settings}
