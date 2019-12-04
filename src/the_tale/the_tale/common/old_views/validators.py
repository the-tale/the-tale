
import smart_imports

smart_imports.all()


def validator(code=None, message=None, response_type=None, status_code=200, raw=False):

    @functools.wraps(validator)
    def validator_decorator(checker):

        @functools.wraps(checker)
        def validator_wrapper(code=code, message=message, response_type=response_type, status_code=status_code):

            @functools.wraps(validator_wrapper)
            def view_decorator(view):

                @functools.wraps(view)
                def view_wrapper(resource, **kwargs):

                    if not checker(resource, **kwargs):
                        if raw:
                            return resource.error(code=code, messages=message)
                        return resource.auto_error(code=code, message=message,  response_type=response_type, status_code=status_code)

                    return view(resource, **kwargs)

                return view_wrapper

            return view_decorator

        return validator_wrapper

    return validator_decorator


def validate_argument(argument_name, checker, code_prefix=None, message=None, response_type=None, raw=False, required=False):

    wrong_format = '%s.%s.wrong_format' % (code_prefix, argument_name)
    not_found = '%s.%s.not_found' % (code_prefix, argument_name)
    not_specified = '%s.%s.not_specified' % (code_prefix, argument_name)

    @functools.wraps(validate_argument)
    def view_decorator(view):

        @functools.wraps(view)
        def view_wrapper(resource, **kwargs):

            if argument_name not in kwargs:
                if required:
                    if raw:
                        return resource.error(code=not_specified, messages=message)
                    return resource.auto_error(code=not_specified, message=message, response_type=response_type)
                return view(resource, **kwargs)

            try:
                value = checker(kwargs[argument_name])
            except:
                if raw:
                    return resource.error(code=wrong_format, messages=message)
                return resource.auto_error(code=wrong_format, message=message, response_type=response_type)

            if value is None:
                if raw:
                    return resource.error(code=not_found, messages=message)
                return resource.auto_error(code=not_found, message=message, response_type=response_type, status_code=404)

            kwargs[argument_name] = value

            return view(resource, **kwargs)

        return view_wrapper

    return view_decorator


def validate_argument_with_resource(argument_name, checker, code_prefix=None, message=None, response_type=None, raw=False):

    wrong_format = '%s.%s.wrong_format' % (code_prefix, argument_name)
    not_found = '%s.%s.not_found' % (code_prefix, argument_name)

    @functools.wraps(validate_argument_with_resource)
    def view_decorator(view):

        @functools.wraps(view)
        def view_wrapper(resource, **kwargs):

            if argument_name not in kwargs:
                return view(resource, **kwargs)

            try:
                value = checker(resource, kwargs[argument_name])
            except:
                if raw:
                    return resource.error(code=wrong_format, messages=message)
                return resource.auto_error(code=wrong_format, message=message, response_type=response_type)

            if value is None:
                if raw:
                    return resource.error(code=not_found, messages=message)
                return resource.auto_error(code=not_found, message=message, response_type=response_type, status_code=404)

            kwargs[argument_name] = value

            return view(resource, **kwargs)

        return view_wrapper

    return view_decorator
