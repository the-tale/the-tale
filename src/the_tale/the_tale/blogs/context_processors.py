
from . import conf


def blogs_context(request):
    return {'blogs_settings': conf.settings}
