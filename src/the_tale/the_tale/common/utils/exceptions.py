# coding: utf-8

from dext.common.utils import exceptions


class TheTaleError(exceptions.DextError):
    pass


class TTAPIError(TheTaleError):
    pass


class TTAPIUnexpectedHTTPStatus(TTAPIError):
    MSG = 'Unexpected http status {status} for url "{url}"'


class TTAPIUnexpectedAPIStatus(TTAPIError):
    MSG = 'Unexpected http status {status} for url "{url}"'
