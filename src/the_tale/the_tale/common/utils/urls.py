import copy

import urllib.request
import urllib.parse
import urllib.error

from django.core.urlresolvers import reverse
from django.conf import settings as project_settings


class UrlBuilder(object):

    def __init__(self, base, protocol='https', arguments=None):
        self.base = base
        self.default_arguments = arguments if arguments is not None else {}
        self.protocol = protocol

    @property
    def arguments_names(self):
        return list(self.default_arguments.keys())

    def __call__(self, **kwargs):
        if not len(self.default_arguments) and not len(kwargs):
            return self.base

        arguments = copy.copy(self.default_arguments)
        arguments.update(kwargs)

        arguments = [(key, value) for key, value in arguments.items() if value is not None]
        arguments.sort()

        query = urllib.parse.urlencode(arguments)

        return self.base + '?' + query


def url(*args, **kwargs):
    base_url = reverse(args[0], args=args[1:])

    if kwargs:
        arguments = list(kwargs.items())
        arguments.sort()

        query = urllib.parse.urlencode(arguments)

        base_url = '%s?%s' % (base_url, query)

    return base_url


def full_url(protocol, *args, **kwargs):
    return protocol + '://' + project_settings.SITE_URL + url(*args, **kwargs)


def absolute_url(relative_url, protocol='https'):
    return protocol + '://' + project_settings.SITE_URL + relative_url


def modify_url(url, query=()):
    hash = None

    if '#' in url:
        url, hash = url.split('#')

    if query:
        query = urllib.parse.urlencode(query)

        url += '&' if '?' in url else '?'

        url += query

    if hash:
        url += '#' + hash

    return url
