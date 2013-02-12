# coding: utf-8

import copy

def create_mob_for_hero(hero):
    from game.mobs.storage import mobs_storage
    return mobs_storage.get_random_mob(hero)


class ValuesDict(object):

    def __init__(self):
        self.data = {}
        self.updated = False

    def __setitem__(self, key, value):
        self.updated = True
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def __delitem__(self, key):
        self.updated = True
        del self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)

    def serialize(self):
        return copy.copy(self.data)

    def items(self):
        return self.data.items()

    @classmethod
    def deserialize(cls, data):
        obj = cls()
        obj.data = copy.copy(data)
        obj.updated = False
        return obj
