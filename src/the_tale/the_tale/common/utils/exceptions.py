# coding: utf-8

from dext.common.utils import exceptions


class TheTaleError(exceptions.DextError):
    pass


class TTAPIError(TheTaleError):
    pass


class TTAPIUnexpectedHTTPStatus(TTAPIError):
    MSG = 'Unexpected http status %(status)s for url "%(url)s"'


class TTAPIUnexpectedAPIStatus(TTAPIError):
    MSG = 'Unexpected api status %(status)s for url "%(url)s" with code "%(code)s", message: "%(message)s", details: %(details)s'
