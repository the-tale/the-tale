# -*- coding: utf-8 -*-
import functools

def login_required(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if resource.account is not None:
            return func(resource, *argv, **kwargs)
        else: 
            if resource.request.is_ajax() or resource.request.method.lower() == 'post':
                return resource.json(status='error',
                                     error=u'У Вас нет прав для проведения данной операции')
            return resource.redirect('accounts:login')

    return wrapper

