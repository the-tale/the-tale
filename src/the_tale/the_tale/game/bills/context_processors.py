
import smart_imports

smart_imports.all()


def bills_context(request):
    return {'bills_settings': conf.settings}
