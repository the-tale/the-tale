# coding: utf-8

import functools

from the_tale.accounts.third_party.conf import third_party_settings


def refuse_third_party(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if third_party_settings.ACCESS_TOKEN_SESSION_KEY in resource.request.session:
            return resource.auto_error('third_party.access_restricted', u'Доступ к этому функционалу запрещён для сторонних приложений')

        return func(resource, *argv, **kwargs)

    return wrapper
