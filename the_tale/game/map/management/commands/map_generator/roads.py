# -*- coding: utf-8 -*-

class PATH_DIRECTION:
    LEFT = 'l'
    RIGHT = 'r'
    UP = 'u'
    DOWN = 'd'

class Road(object):

    def __init__(self, road_id, point_1, point_2, length, exists):
        self.id = road_id
        self.point_1 = point_1
        self.point_2 = point_2
        self.length = length
        self.path = []
        self.exists = exists

    @property
    def key(self):
        return (self.point_1, self.point_2)

    def add_path_direction(self, move_to):
        self.path.append(move_to)

    def get_json_data(self):
        return {'id': self.id,
                'point_1_id': self.point_1,
                'point_2_id': self.point_2,
                'path': ''.join(self.path),
                'length': self.length,
                'exists': self.exists}
