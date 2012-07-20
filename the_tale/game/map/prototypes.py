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


    ######################
    # object operations
    ######################

    @classmethod
    def create(cls, turn_number, width, height, terrain):

        model = MapInfo.objects.create(turn_number=turn_number,
                                       width=width,
                                       height=height,
                                       terrain=s11n.to_json(terrain))
        return cls(model)
