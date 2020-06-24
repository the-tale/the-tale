
import smart_imports

smart_imports.all()


class NoCacheMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        response.setdefault('Cache-Control', 'no-store, max-age=0, no-cache, must-revalidate, private')

        return response
