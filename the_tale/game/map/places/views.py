# -*- coding: utf-8 -*-

from dext.views.resources import handler
from common.utils.resources import Resource

from game.map.places.storage import places_storage

class PlaceResource(Resource):

    def __init__(self, request, place_id, *args, **kwargs):
        super(PlaceResource, self).__init__(request, *args, **kwargs)
        self.place_id = int(place_id)

    @property
    def place(self): return places_storage[self.place_id]

    @handler('#place_id', 'map-info', method='get')
    def map_info(self):
        return self.template('places/map_info.html',
                             {'place': self.place,
                              'hero': self.account.angel.get_hero() if self.account else None} )
