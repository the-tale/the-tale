# coding: utf-8
import functools


def login_required(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        from the_tale.accounts.logic import login_page_url

        if resource.account.is_authenticated():
            return func(resource, *argv, **kwargs)
        else:
            from dext.common.utils.response import mime_type_to_response_type
            response_type = mime_type_to_response_type(resource.request.META.get('HTTP_ACCEPT'))

            if resource.request.is_ajax() or response_type == 'json':
                return resource.auto_error('common.login_required', u'У Вас нет прав для проведения данной операции')
            return resource.redirect(login_page_url(resource.request.get_full_path()))

    return wrapper

def staff_required(permissions=()):

    @functools.wraps(staff_required)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, *argv, **kwargs):
            if permissions:
                raise NotImplementedError('staff required decorator has not implemented for working with permissions list')
            else:
                if resource.account.is_authenticated() and resource.account.is_staff:
                    return func(resource, *argv, **kwargs)
                else:
                    return resource.auto_error('common.staff_required', u'У Вас нет прав для проведения данной операции')

        return login_required(wrapper)

    return decorator


def superuser_required(permissions=()):

    @functools.wraps(staff_required)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, *argv, **kwargs):
            if permissions:
                raise NotImplementedError('superuser required decorator has not implemented for working with permissions list')
            else:
                if resource.account.is_authenticated() and resource.account.is_superuser:
                    return func(resource, *argv, **kwargs)
                else:
                    return resource.auto_error('common.superuser_required', u'У Вас нет прав для проведения данной операции')

        return login_required(wrapper)

    return decorator


def lazy_property(func):

    lazy_name = '_%s__lazy' % func.__name__

    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, lazy_name):
            setattr(self, lazy_name, func(self))
        return getattr(self, lazy_name)

    def deleter(self):
        if hasattr(self, lazy_name):
            delattr(self, lazy_name)

    return property(fget=wrapper, fdel=deleter)
