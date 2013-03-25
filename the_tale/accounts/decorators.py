# -*- coding: utf-8 -*-
import functools

from django.http import HttpResponseForbidden

def login_required(func):

    @functools.wraps(func)
    def decorator(self, *args, **kwargs):
        if self.account.is_authenticated():
            return func(self, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    return decorator
