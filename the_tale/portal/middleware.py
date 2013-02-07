# coding: utf-8

from game.map.places.storage import places_storage
# from game.map.roads.storage import roads_storage
from game.persons.storage import persons_storage
from game.map.storage import map_info_storage

class StorageMiddleware(object):
    '''
    MUST be places AFTER settings middleware
    '''

    def process_request(self, request):
        places_storage.sync()
        # roads_storage.sync()
        persons_storage.sync()
        map_info_storage.sync()
