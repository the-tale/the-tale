# coding: utf-8

from the_tale.market import exceptions


_GOODS_TYPES = {}


def get_type(type):
    return _GOODS_TYPES[type]


class BaseGoodType(object):

    def __init__(self, uid, name, description):
        self.uid = uid
        self.name = name
        self.description = description

    def register(self):
        if self.uid in _GOODS_TYPES:
            raise exceptions.DuplicateGoodTypeUIDError(good_type=self.__class__, uid=self.uid)

        _GOODS_TYPES[self.uid] = self

    def unregister(self):
        if self.uid in _GOODS_TYPES:
            del _GOODS_TYPES[self.uid]

    def deserialize_item(self, data):
        raise NotImplementedError()

    def has_good(self, container, good_uid):
        raise NotImplementedError()

    def extract_good(self, container, good_uid):
        raise NotImplementedError()

    # def get_goods(self, account_id):
    #     raise NotImplementedError()
