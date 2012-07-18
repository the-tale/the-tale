# coding: utf-8

from dext.utils.exceptions import ExceptionMiddleware as DextExceptionMiddleware

from game.map.places.storage import places_storage
from game.map.roads.storage import roads_storage

from portal.views import PortalResource

class ExceptionMiddleware(DextExceptionMiddleware):
    EXCEPTION_RESOURCE = PortalResource


class StorageMiddleware(object):
    '''
    MUST be places AFTER settings middleware
    '''

    def process_request(self, request):
        places_storage.sync()
        roads_storage.sync()
