# -*- coding: utf-8 -*-

from dext.views.resources import handler
from common.utils.resources import Resource

from .logic import get_map_info

class MapResource(Resource):

    def __init__(self, request, *args, **kwargs):
        super(MapResource, self).__init__(request, *args, **kwargs)

    @handler('', method='get')
    def info(self):
        map_info = get_map_info()
        return self.json(status='ok', data=map_info)


