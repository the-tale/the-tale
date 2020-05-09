
import smart_imports
smart_imports.all()


def memclass(function):

    cache_name = '_%s' % function.__name__

    @functools.wraps(function)
    def wrapper(cls, *args, **kwargs):
        if not hasattr(cls, cache_name):
            setattr(cls, cache_name, function(cls, *args, **kwargs))
        return getattr(cls, cache_name)

    return wrapper


class ResourceException(Exception):
    pass


def handler(*path, **params):

    method = params.get('method', ['post', 'get'])
    args = params.get('args', [])
    name = params.get('name', path[-1])

    @functools.wraps(handler)
    def decorator(func):

        if isinstance(method, str):
            methods = [method]
        else:
            methods = list(method)

        expected_args, expected_vargs, expected_kwargs, expected_defaults = inspect.getargspec(func)

        if expected_defaults is not None:
            expected_defaults = dict(zip(expected_args[-len(expected_defaults):], expected_defaults))

        info = {'methods': methods,
                'args': args,
                'path': path,
                'name': name,
                'expected': { 'args': expected_args,
                              'defaults': expected_defaults} }

        func._handler_info = info
        return func

    return decorator


class DispatchInfo(object):

    def __init__(self, handler_name, methods, args=[]):
        self.handler_name = handler_name
        self.methods = methods
        self.args = args

    def check(self, request):
        if request.method.lower() not in self.methods:
            return False

        for arg in self.args:

            if isinstance(arg, str) or not hasattr(arg, '__iter__'):
                key = arg
                if arg not in request.GET: return False

            elif len(arg) == 2:
                key, value = arg
                if key not in request.GET: return False
                if value != request.GET[key]: return False

        return True


@functools.total_ordering
class HandlerInfo(object):

    def __init__(self, method):
        info = method._handler_info

        dispatch_info = DispatchInfo(handler_name=method.__name__,
                                     methods=info['methods'],
                                     args=info['args'])

        self.dispatch_list = [dispatch_info]

        self.path = info['path']
        self.name = info['name']

    def update(self, handler_info):
        if self.path != handler_info.path:
            raise ResourceException('can not merge handlers with different path: ("%s", "%s")' % (self.path, handler_info.path) )

        self.dispatch_list.extend(handler_info.dispatch_list)
        self.dispatch_list.sort(key=lambda x: x.handler_name)

    @property
    def url_regexp(self):
        regex = ''
        for part in self.path:
            if len(part) == 0:
                regex = '%s/' % regex
            elif part[0] == '#':
                regex = '%s/(?P<%s>[^\/]*)' % (regex, part[1:])
            elif part[0] == '^':
                regex = '%s/%s' % (regex, part[1:])
            else:
                regex = '%s/%s' % (regex, part)
        return '^%s$' % regex[1:]

    def dispatch(self, request):
        for dispatch_info in self.dispatch_list:
            if dispatch_info.check(request):
                return dispatch_info.handler_name
        raise django_http.Http404()

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        for l, r in zip(self.path, other.path):
            if not l: return True
            if not r: return False
            if l[0] == r[0] == '#': return l < r
            if l[0] == '#': return False
            if r[0] == '#': return True
            if l[0] != '#' and l != r: return l < r

        return len(self.path) < len(other.path)


class BaseResource(object):

    ERROR_TEMPLATE = NotImplemented
    DIALOG_ERROR_TEMPLATE = NotImplemented

    def __init__(self, request):
        self.request = request
        self.csrf = django_middleware.csrf.get_token(request)

    def initialize(self, *args, **kwargs):
        pass

    @classmethod
    @memclass
    def get_handlers(cls):

        handlers = {}

        for method_name in dir(cls):
            method = getattr(cls, method_name)

            if hasattr(method, '_handler_info'):
                info = HandlerInfo(method)
                if info.path in handlers:
                    handlers[info.path].update(info)
                else:
                    handlers[info.path] = info

        return sorted(handlers.values())

    @property
    def user_ip(self):
        return get_ip_from_request(self.request)

    def string(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='text/html; charset=%s' % charset)

    def js(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='application/x-javascript; charset=%s' % charset)

    def xml(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='text/xml; charset=%s' % charset)

    def atom(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='application/atom+xml; charset=%s' % charset)

    def rss(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='application/rss+xml; charset=%s' % charset)

    def rdf(self, string, charset='utf-8'):
        return django_http.HttpResponse(string, content_type='application/rdf+xml; charset=%s' % charset)

    def template(self, template_name, context={}, status_code=200, charset='utf-8', mimetype='text/html'):
        full_context = {'resource': self}
        full_context.update(context)

        response_class = django_http.HttpResponse

        if status_code == 404:
            response_class = django_http.HttpResponseNotFound

        content_type = '%s; charset=%s' % (mimetype, charset)

        text = utils_jinja2.render(template_name, context=full_context, request=self.request)

        return response_class(text, content_type=content_type)


    def json(self, charset='utf-8', mimetype='application/json', **kwargs):
        response = django_http.HttpResponse(s11n.to_json(kwargs), content_type='%s; charset=%s' % (mimetype, charset))
        return response

    def json_ok(self, data=None, charset='utf-8', mimetype='application/json'):
        return self.json(mimetype=mimetype, charset=charset, **self.ok(data=data))

    def ok(self, data=None):
        if data is None:
            return {'status': 'ok'}
        return {'status': 'ok', 'data': data}

    def processing(self, status_url):
        return {'status': 'processing',
                'status_url': status_url}

    def json_processing(self, status_url, mimetype='application/json', charset='utf-8'):
        return self.json(mimetype=mimetype, charset=charset, **self.processing(status_url=status_url))

    def json_error(self, code, messages=None, mimetype='application/json', charset='utf-8'):
        data = self.error(code=code, messages=messages)
        return self.json(mimetype=mimetype, charset=charset, **data)

    def js_error(self, code, messages=None, mimetype='application/x-javascript', charset='utf-8'):
        data = self.error(code=code, messages=messages)
        response = django_http.HttpResponse('function DextErrorMessage(){return %s;};' % s11n.to_json(data),
                                            content_type='%s; charset=%s' % (mimetype, charset))
        return response

    def error(self, code, messages=None):
        data = {'status': 'error',
                'code': code}

        if isinstance(messages, str):
            data['error'] = messages
        else:
            data['errors'] = messages

        return data

    def auto_error(self, code, message, template=None, status_code=200, response_type=None, charset='utf-8'):

        if response_type is None:
            response_type = utils_views.mime_type_to_response_type(self.request.META.get('HTTP_ACCEPT'))

        if response_type == 'html':
            if self.request.is_ajax():
                return self.template(self.DIALOG_ERROR_TEMPLATE, {'error_message': message, 'error_code': code }, status_code=status_code)
            else:
                return self.template(self.ERROR_TEMPLATE, {'error_message': message, 'error_code': code }, status_code=status_code)

        if response_type == 'js':
            return self.js_error(code, message, charset=charset)

        return self.json_error(code, message, charset=charset)

    def css(self, text, charset='utf-8'):
        response = django_http.HttpResponse(text, content_type='text/css; charset=%s' % charset)
        return response

    def redirect(self, url, permanent=False):
        try:
            if permanent:
                return django_http.HttpResponsePermanentRedirect(url)
            return django_http.HttpResponseRedirect(url)
        except Exception as e:
            return django_http.HttpResponseRedirect('/')


def get_ip_from_request(request):
    """Returns the IP of the request, accounting for the possibility of being
       behind a proxy.
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)

    if ip:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(", ")[0]

    else:
        ip = request.META.get("REMOTE_ADDR", "")

    return ip
