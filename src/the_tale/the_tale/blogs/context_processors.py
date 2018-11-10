
import smart_imports

smart_imports.all()


def blogs_context(request):
    return {'blogs_settings': conf.settings}
