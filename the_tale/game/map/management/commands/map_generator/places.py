# -*- coding: utf-8 -*-

class Place(object):

    def __init__(self, x, y, significance, terrain, place_id=None, name=None, size=None):
        self.x = x
        self.y = y
        self.id = place_id if place_id else '%ix%i' % (x, y)
        self.name = name if name else '%ix%i' % (x, y)
        self.significance = significance
        self.terrain = terrain
        self.size = size

    def get_json_data(self):
        return {'id': self.id,
                'x': self.x,
                'y': self.y,
                'name': self.name,
                'size': self.size}


class City(Place):

    def __init__(self, **kwargs):
        super(City, self).__init__(**kwargs)
