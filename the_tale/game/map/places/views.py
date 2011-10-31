# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource

from .prototypes import get_place_by_id

class PlaceResource(Resource):

    def __init__(self, request, place_id, *args, **kwargs):
        super(PlaceResource, self).__init__(request, *args, **kwargs)
        self.place_id = int(place_id)

    @property
    def place(self):
        if not hasattr(self, '_place'):
            self._place= get_place_by_id(self.place_id)
        return self._place

    @handler('#place_id', 'map_info', method='get')
    def map_info(self):
        return self.template('places/map_info.html',
                             {'place': self.place} )

