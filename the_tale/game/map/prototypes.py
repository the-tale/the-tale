# coding: utf-8

from dext.utils import s11n

from game.map.models import MapInfo

class MapInfoPrototype(object):

    def __init__(self, model):
        self.model = model

    @property
    def turn_number(self): return self.model.turn_number

    @property
    def terrain(self):
        if not hasattr(self, '_terrain'):
            self._terrain = s11n.from_json(self.model.terrain)
        return self._terrain

    @property
    def terrain_percents(self):
        if not hasattr(self, '_terrain_percents'):
            self._terrain_percents = s11n.from_json(self.model.terrain_percents)
        return self._terrain_percents


    ######################
    # object operations
    ######################

    @classmethod
    def create(cls, turn_number, width, height, terrain):

        terrain_squares = {}

        for row in terrain:
            for cell in row:
                terrain_squares[cell] = terrain_squares.get(cell, 0) + 1

        total_cells = sum(terrain_squares.values())

        terrain_percents = dict( (cell, float(square) / total_cells) for cell, square in terrain_squares.items())

        model = MapInfo.objects.create(turn_number=turn_number,
                                       width=width,
                                       height=height,
                                       terrain=s11n.to_json(terrain),
                                       terrain_percents=s11n.to_json(terrain_percents))
        return cls(model)
