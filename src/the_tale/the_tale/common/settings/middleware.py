
import smart_imports
smart_imports.all()


class SettingsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from . import settings

        settings.refresh()

        return self.get_response(request)
