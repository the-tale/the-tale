# coding: utf-8

from dext.utils.exceptions import ExceptionMiddleware as DextExceptionMiddleware

from portal.views import PortalResource

class ExceptionMiddleware(DextExceptionMiddleware):
    EXCEPTION_RESOURCE = PortalResource
