# coding: utf-8
import functools


def login_required(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        from accounts.logic import login_url

        if resource.account.is_authenticated():
            return func(resource, *argv, **kwargs)
        else:
            from dext.utils.response import content_type_to_response_type
            response_type = content_type_to_response_type(resource.request.META.get('CONTENT_TYPE'))

            if resource.request.is_ajax() or response_type == 'json':
                return resource.auto_error('common.login_required', u'У Вас нет прав для проведения данной операции')
            return resource.redirect(login_url(resource.request.get_full_path()))

    return wrapper

def staff_required(permissions=[]):

    @functools.wraps(staff_required)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, *argv, **kwargs):
            if permissions:
                raise NotImplemented('staff required decorator has not emplimented for working with permissions list')
            else:
                if resource.account.is_authenticated() and resource.account.is_staff:
                    return func(resource, *argv, **kwargs)
                else:
                    return resource.auto_error('common.staff_required', u'У Вас нет прав для проведения данной операции')

        return login_required(wrapper)

    return decorator


def lazy_property(func):

    lazy_name = '_%s__lazy' % func.__name__

    @property
    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, lazy_name):
            setattr(self, lazy_name, func(self))
        return getattr(self, lazy_name)

    return wrapper
