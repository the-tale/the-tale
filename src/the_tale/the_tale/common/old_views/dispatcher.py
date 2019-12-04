
import smart_imports

smart_imports.all()


def create_handler_view(resource_class, handler):

    if isinstance(handler, str):
        handler_path = '%s::%s' % (resource_class.__name__, handler)
        result_method_name = handler  # TODO: result_method_name - is some variable name, since 'handler_name' not seen in handler_view
    else:
        handler_path = handler.path[-1]
        result_method_name = None

    def handler_view(request, **kwargs):

        resource = resource_class(request)
        initialize_result = resource.initialize(**kwargs) # *args removeed

        if initialize_result is not None:
            return initialize_result

        if result_method_name is None:
            method_name = handler.dispatch(request)
        else:
            method_name = result_method_name
        method = getattr(resource, method_name, None)

        info = method._handler_info

        args = info['expected']['args']

        arguments = {}

        for arg in args:
            if arg != 'self' and arg in request.GET:
                arguments[arg] = request.GET.get(arg)

        if method:
            return method(**arguments)

        raise resources.ResourceException('can not dispatch url for handler "%s"' % handler_path)

    handler_view.__name__ = '%s_%s' % (resource_class.__name__, handler_path)

    return handler_view


def resource_patterns(resource_class, args={}):
    patterns_args = []

    for handler in resource_class.get_handlers():
        patterns_args.append(django_urls.url(handler.url_regexp,
                                             create_handler_view(resource_class, handler),
                                             name=handler.name,
                                             kwargs=args))
    return patterns_args
