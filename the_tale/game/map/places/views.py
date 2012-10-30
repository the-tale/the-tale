# -*- coding: utf-8 -*-

from dext.views.resources import handler
from common.utils.resources import Resource

from game.heroes.prototypes import HeroPrototype

from game.map.places.storage import places_storage

class PlaceResource(Resource):

    def initialize(self, place_id, *args, **kwargs):
        super(PlaceResource, self).initialize(*args, **kwargs)
        self.place_id = int(place_id)

    @property
    def place(self): return places_storage[self.place_id]

    @handler('#place_id', 'map-info', method='get')
    def map_info(self):
        return self.template('places/map_info.html',
                             {'place': self.place,
                              'hero': HeroPrototype.get_by_account_id(self.account.id) if self.account else None} )
