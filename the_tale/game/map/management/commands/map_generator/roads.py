# -*- coding: utf-8 -*-

class Road(object):

    def __init__(self, road_id, point_1, point_2, length):
        self.id = road_id 
        self.point_1 = point_1
        self.point_2 = point_2
        self.length = length

    @property
    def key(self):
        return (self.point_1, self.point_2)

    def get_json_data(self):
        return {'id': self.id, 
                'point_1_id': self.point_1,
                'point_2_id': self.point_2,
                'length': self.length}
