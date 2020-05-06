
import smart_imports

smart_imports.all()

# for external code
ViewError = utils_exceptions.ViewError


class Context(object):

    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise ViewError(code='internal.try_to_reassign_context_value',
                            message=conf.settings.DEFAUL_ERROR_MESSAGE,
                            info={'name': name})
        super().__setattr__(name, value)


class View(object):
    __slots__ = ('processors', 'logic', 'name', 'path', 'resource', '__doc__', 'csrf_exempt', '__name__', '__qualname__')

    def __init__(self, logic):
        self.processors = []
        self.logic = logic
        self.name = None
        self.path = None
        self.resource = None
        self.csrf_exempt = getattr(logic, 'csrf_exempt', False)

        self.__doc__ = logic.__doc__

        self.__name__ = logic.__name__
        self.__qualname__ = logic.__qualname__

    def get_processors(self):
        return self.resource.get_processors() + self.processors

    def add_processor(self, processor):
        self.processors.insert(0, processor)

    def __call__(self, request, *argv, **url_arguments):
        context = Context()

        context.django_request = request
        context.django_url_argumens = url_arguments

        unprocessed_processors = self.get_processors()

        processed_processors = []

        response = None

        try:
            for processor in unprocessed_processors:
                response = processor.preprocess(context)
                processed_processors.append(processor)

                if response:
                    break

            if response is None:
                response = self.logic(context)

            for processor in reversed(processed_processors):
                response = processor.postprocess(context, response)

                if response:
                    break

            return response.complete(context)

        except ViewError as error:
            return self.process_error(error, request, context)

    def _get_error_response_class(self, request):

        accepted_mimetypes = request.META.get('HTTP_ACCEPT')

        if accepted_mimetypes is None:
            return AjaxError

        if any(tp in accepted_mimetypes for tp in ('application/xhtml+xml', 'text/html', 'text/plain', 'text/xml')):
            return PageError

        if any(tp in accepted_mimetypes for tp in ('application/x-javascript',)):
            return NotImplemented

        return AjaxError

    def process_error(self, error, request, context):
        error_response_class = self._get_error_response_class(request)
        info = error.info
        info['resource'] = '%s.%s' % (self.resource.name, self.name)
        return error_response_class(code=error.code,
                                    errors=error.message,
                                    context=context,
                                    http_status=error.http_status,
                                    info=info).complete(context)

    def get_url_record(self):

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

        return django_urls.url('^%s$' % regex[1:],
                               self,
                               name=self.name,
                               kwargs={})

    def __lt__(self, other):
        for l, r in zip(self.path, other.path):
            if not l: return True
            if not r: return False
            if l[0] == r[0] == '#': return l < r
            if l[0] == '#': return False
            if r[0] == '#': return True
            if l[0] != '#' and l != r: return l < r

        return len(self.path) < len(other.path)


class Resource(object):
    __slots__ = ('name', 'processors', 'views', 'parent', 'children')

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.processors = []
        self.views = {}
        self.parent = None
        self.children = []

    def get_processors(self):
        if self.parent:
            return self.parent.get_processors() + self.processors

        return self.processors

    def add_processor(self, processor):
        self.processors.append(processor)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def __call__(self, *argv, **kwargs):

        name = kwargs.get('name', argv[-1])

        methods = kwargs.get('method', ('get',))

        if isinstance(methods, str):
            methods = [methods]

        methods = [m.upper() for m in methods]

        @functools.wraps(self.__call__)
        def decorator(func):

            view = func if isinstance(func, View) else View(logic=func)

            view.name = name
            view.path = argv

            view.add_processor(HttpMethodProcessor(allowed_methods=methods))
            view.add_processor(CSRFProcessor())

            if view.name in self.views:
                raise exceptions.DuplicateViewNameError(name=view.name)

            self.views[view.name] = view
            view.resource = self

            return view

        return decorator

    def get_urls(self):
        urls = []

        for view in sorted(self.views.values()):
            urls.append(view.get_url_record())

        return urls


class ProcessorArgument(object):
    __slots__ = ('default', )

    def __init__(self, default=NotImplemented):
        self.default = default


# TODO: write metaclass for processing processor arguments
class BaseViewProcessor(object):
    __slots__ = ()

    def __init__(self, **kwargs):
        for argument_name in dir(self):
            argument = getattr(self, argument_name)
            if not isinstance(argument, ProcessorArgument):
                continue

            name = argument_name[4:].lower()
            value = kwargs.get(name, getattr(self, name.upper(), argument.default))

            setattr(self, name, value)

        for argument_name, value in kwargs.items():
            argument = getattr(self, 'ARG_%s' % argument_name.upper())

            if not isinstance(argument, ProcessorArgument):
                raise exceptions.WrongProcessorArgumentError(processor=self, argument=argument_name)

            setattr(self, argument_name.lower(), value)

        self.initialize()

    def initialize(self):
        pass

    def preprocess(self, context):
        pass

    def postprocess(self, context, response):
        return response

    def __call__(self, view):
        view = view if isinstance(view, View) else View(logic=view)

        view.add_processor(self)

        return view


class HttpMethodProcessor(BaseViewProcessor):
    __slots__ = ('allowed_methods', )
    ARG_ALLOWED_METHODS = ProcessorArgument()

    def initialize(self):
        super().initialize()
        self.allowed_methods = frozenset(self.allowed_methods)

    def preprocess(self, context):
        if context.django_request.method not in self.allowed_methods:
            raise ViewError(code='common.wrong_http_method',
                            message='К адресу нельзя обратиться с помощью HTTP метода "%(method)s"' % {'method': context.django_request.method})

        context.django_method = getattr(utils_relations.HTTP_METHOD, context.django_request.method)


class CSRFProcessor(BaseViewProcessor):
    def preprocess(self, context):
        context.csrf = django_middleware.csrf.get_token(context.django_request)


class PermissionProcessor(BaseViewProcessor):
    __slots__ = ('permission', 'context_name')
    ARG_PERMISSION = ProcessorArgument()
    ARG_CONTEXT_NAME = ProcessorArgument()

    def preprocess(self, context):
        setattr(context, self.context_name, context.django_request.user.has_perm(self.permission))


class AccessProcessor(BaseViewProcessor):
    __slots__ = ('error_code', 'error_message')
    ARG_ERROR_CODE = ProcessorArgument()
    ARG_ERROR_MESSAGE = ProcessorArgument()

    def check(self, context):
        raise NotImplementedError()

    def preprocess(self, context):
        if not self.check(context):
            raise ViewError(code=self.error_code, message=self.error_message)


class FlaggedAccessProcessor(AccessProcessor):
    __slots__ = ('error_code', 'error_message')
    ARG_ERROR_CODE = ProcessorArgument()
    ARG_ERROR_MESSAGE = ProcessorArgument()
    ARG_ARGUMENT = ProcessorArgument()

    def extract(self, context):
        return getattr(context, self.argument)

    def validate(self, argument):
        return argument

    def check(self, context):
        return self.validate(self.extract(context))


class FormProcessor(BaseViewProcessor):
    __slots__ = ('error_message', 'form_class', 'context_name')
    ARG_FORM_CLASS = ProcessorArgument()
    ARG_ERROR_MESSAGE = ProcessorArgument()
    ARG_CONTEXT_NAME = ProcessorArgument(default='form')

    def preprocess(self, context):

        form = self.form_class(context.django_request.POST)

        if not form.is_valid():
            raise ViewError(code='form_errors', message=form.errors)

        setattr(context, self.context_name, form)


class ArgumentProcessor(BaseViewProcessor):
    __slots__ = ('error_message', 'get_name', 'post_name', 'url_name', 'context_name', 'default_value', 'in_list')
    ARG_CONTEXT_NAME = ProcessorArgument()
    ARG_ERROR_MESSAGE = ProcessorArgument()
    ARG_GET_NAME = ProcessorArgument(default=None)
    ARG_POST_NAME = ProcessorArgument(default=None)
    ARG_URL_NAME = ProcessorArgument(default=None)
    ARG_CONTEXT_NAME = ProcessorArgument()
    ARG_DEFAULT_VALUE = ProcessorArgument()
    ARG_IN_LIST = ProcessorArgument(default=False)

    def initialize(self):
        super().initialize()

        if sum((1 if self.get_name else 0,
                1 if self.post_name else 0,
                1 if self.url_name else 0)) != 1:
            raise exceptions.SingleNameMustBeSpecifiedError()

    def extract(self, context):
        if self.url_name:
            return context.django_url_argumens.get(self.url_name)

        if self.get_name:
            if self.in_list:
                return context.django_request.GET.getlist(self.get_name)
            else:
                return context.django_request.GET.get(self.get_name)

        if self.in_list:
            return context.django_request.POST.getlist(self.post_name)
        else:
            return context.django_request.POST.get(self.post_name)

    def parse(self, context, raw_value):
        return raw_value

    def _argument_name(self):
        if self.url_name:
            return self.url_name
        if self.get_name:
            return self.get_name
        if self.post_name:
            return self.post_name

    def raise_not_specified(self):
        raise ViewError(code='%s.not_specified' % self._argument_name(), message=self.error_message)

    def raise_wrong_format(self):
        raise ViewError(code='%s.wrong_format' % self._argument_name(), message=self.error_message)

    def raise_wrong_value(self):
        raise ViewError(code='%s.wrong_value' % self._argument_name(), message=self.error_message)

    def preprocess(self, context):

        raw_value = self.extract(context)

        if raw_value:
            value = self.parse(context, raw_value)

        elif self.default_value is NotImplemented:
            self.raise_not_specified()

        else:
            value = self.default_value

        setattr(context, self.context_name, value)


class MapArgumentProcessor(ArgumentProcessor):
    __slots__ = ('mapping',)
    ARG_MAPPING = ProcessorArgument()

    def parse(self, context, raw_value):

        mapping = self.mapping if not isinstance(self.mapping, collections.Callable) else self.mapping()

        if raw_value not in mapping:
            self.raise_wrong_value()

        return mapping.get(raw_value)


class IntArgumentProcessor(ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            return int(raw_value)
        except ValueError:
            self.raise_wrong_format()


class IntsArgumentProcessor(ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            return [int(value.strip()) for value in raw_value.split(',')]
        except ValueError:
            self.raise_wrong_format()


class RelationArgumentProcessor(ArgumentProcessor):
    __slots__ = ('relation', 'value_type')
    ARG_RELATION = ProcessorArgument()
    ARG_VALUE_TYPE = ProcessorArgument(default=int)

    def parse(self, context, raw_value):
        from rels import exceptions as rels_exceptions

        try:
            value = self.value_type(raw_value)
        except ValueError:
            self.raise_wrong_format()
        except TypeError:
            self.raise_wrong_format()

        try:
            return self.relation(value)
        except rels_exceptions.NotExternalValueError:
            self.raise_wrong_value()


class DebugProcessor(BaseViewProcessor):
    def preprocess(self, context):
        context.debug = django_settings.DEBUG

        if not context.debug:
            raise ViewError(code='common.debug_required', message='Функционал доступен только в режиме отладки')


class BaseResponse(object):
    __slots__ = ('http_status',
                 'http_mimetype',
                 'http_charset',
                 'content')

    def __init__(self,
                 http_mimetype,
                 http_status=utils_relations.HTTP_STATUS.OK,
                 http_charset='utf-8',
                 content=None):
        self.http_status = http_status
        self.http_mimetype = http_mimetype
        self.http_charset = http_charset
        self.content = content if content is not None else {}

    def complete(self, context):
        return django_http.HttpResponse(self.content,
                                        status=self.http_status.value,
                                        content_type='%s; charset=%s' % (self.http_mimetype, self.http_charset))


class Redirect(BaseResponse):
    __slots__ = ('target_url', 'permanent')

    def __init__(self, target_url, permanent=False, **kwargs):
        super().__init__(http_mimetype=None, **kwargs)
        self.target_url = target_url
        self.permanent = permanent

    def complete(self, context):
        ResponseClass = django_http.HttpResponsePermanentRedirect if self.permanent else django_http.HttpResponseRedirect
        return ResponseClass(self.target_url)


class Page(BaseResponse):
    __slots__ = ('template',)

    def __init__(self, template, http_mimetype='text/html', **kwargs):
        super().__init__(http_mimetype=http_mimetype, **kwargs)
        self.template = template

    def complete(self, context):
        self.content['context'] = context
        self.content = utils_jinja2.render(self.template, context=self.content, request=context.django_request)
        return super().complete(context)


class String(BaseResponse):
    __slots__ = ('text',)

    def __init__(self, text, http_mimetype='text/html', **kwargs):
        super().__init__(http_mimetype=http_mimetype, **kwargs)
        self.text = text

    def complete(self, context):
        self.content['context'] = context
        self.content = self.text
        return super().complete(context)


# TODO: refactor error/errors
class PageError(Page):
    __slots__ = ('code', 'errors', 'context', 'info')

    def __init__(self, code, errors, context, info=None, **kwargs):
        if 'template' not in kwargs:
            if context.django_request.is_ajax():
                kwargs['template'] = conf.settings.DIALOG_ERROR_TEMPLATE
            else:
                kwargs['template'] = conf.settings.PAGE_ERROR_TEMPLATE

        if isinstance(errors, str):
            error = errors
        else:
            error = list(errors.values())[0][0]

        if 'content' not in kwargs:
            kwargs['content'] = {}

        kwargs['content'].update({'error_code': code,
                                  'error_message': error,
                                  'error_info': info,
                                  'context': context,
                                  'resource': context.resource})# TODO: remove resource (added for compartibility with old version)

        super().__init__(**kwargs)

        self.code = code
        self.errors = error
        self.context = context
        self.info = info


class Atom(BaseResponse):
    __slots__ = ('feed',)

    def __init__(self, feed, http_mimetype='application/atom+xml', **kwargs):
        super().__init__(http_mimetype=http_mimetype, **kwargs)
        self.feed = feed

    def complete(self, context):
        self.content = self.feed.writeString(self.http_charset)
        return super().complete(context)


class Ajax(BaseResponse):

    def __init__(self, http_mimetype='application/json', **kwargs):
        super().__init__(http_mimetype=http_mimetype, **kwargs)

    def wrap(self, content):
        return content

    def complete(self, context):
        self.content = s11n.to_json(self.wrap(self.content))
        return super().complete(context)


class AjaxOk(Ajax):
    def wrap(self, content):
        return {'status': 'ok', 'data': content}


# TODO: refactor error/errors
class AjaxError(Ajax):
    __slots__ = ('code', 'errors', 'context', 'info')

    def __init__(self, code, errors, context, info=None, **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.errors = errors
        self.context = context
        self.info = info

    def wrap(self, context):
        data = {'status': 'error',
                'code': self.code,
                'data': self.info}

        if isinstance(self.errors, str):
            data['error'] = self.errors
        else:
            data['errors'] = self.errors

        return data


class AjaxProcessing(Ajax):
    __slots__ = ('status_url',)

    def __init__(self, status_url, **kwargs):
        super().__init__(**kwargs)
        self.status_url = status_url

    def wrap(self, context):
        return {'status': 'processing',
                'status_url': self.status_url}


class FakeResource(object):

    def __init__(self, context):
        self.request = context.django_request
        self.account = context.account
        self.csrf = django_decorators.csrf.get_token(context.django_request)


class FakeResourceProcessor(BaseViewProcessor):
    def preprocess(self, context):
        context.resource = FakeResource(context)


class PageNumberProcessor(ArgumentProcessor):
    CONTEXT_NAME = 'page'
    ERROR_MESSAGE = 'Неверный номер страницы'
    GET_NAME = 'page'
    DEFAULT_VALUE = 0

    def parse(self, context, raw_value):
        try:
            return max(0, int(raw_value) - 1)
        except ValueError:
            self.raise_wrong_format()


class TextFilterProcessor(ArgumentProcessor):
    CONTEXT_NAME = 'filter'
    ERROR_MESSAGE = 'Неверный текст для фильтра'
    GET_NAME = 'filter'
    DEFAULT_VALUE = None

    def parse(self, context, raw_value):
        return raw_value


def mime_type_to_response_type(content_type):
    if content_type is None:
        return 'json'

    if any(tp in content_type for tp in ('application/xhtml+xml', 'text/html', 'text/plain', 'text/xml')):
        return 'html'

    if any(tp in content_type for tp in ('application/x-javascript',)):
        return 'js'

    return 'json'
