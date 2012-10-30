# -*- coding: utf-8 -*-
import functools

from accounts.logic import login_url

def login_required(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if resource.account is not None:
            return func(resource, *argv, **kwargs)
        else:
            if resource.request.is_ajax() or resource.request.method.lower() == 'post':
                return resource.json_error('common.login_required', u'У Вас нет прав для проведения данной операции')
            return resource.redirect(login_url(resource.request.get_full_path()))

    return wrapper

def staff_required(permissions=[]):

    @functools.wraps(staff_required)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, *argv, **kwargs):
            if permissions:
                raise NotImplemented('staff required decorator has not emplimented for working woth permissions list')
            else:
                if resource.request.user.is_active and resource.request.user.is_staff:
                    return func(resource, *argv, **kwargs)
                else:
                    if resource.request.is_ajax() or resource.request.method.lower() == 'post':
                        return resource.json(status='error',
                                             error=u'У Вас нет прав для проведения данной операции')
                    return resource.redirect(login_url(resource.request.get_full_path()))

        return wrapper

    return decorator
