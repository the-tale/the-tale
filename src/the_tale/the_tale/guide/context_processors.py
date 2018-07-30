
import smart_imports

smart_imports.all()


def guide_context(request):
    return {'guide_settings': conf.settings}
