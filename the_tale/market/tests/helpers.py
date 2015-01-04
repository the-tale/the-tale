# coding: utf-8

from the_tale.market import goods_types
from the_tale.market import objects


class TestGoodItem(object):

    def __init__(self, uid):
        self.uid = uid

    def serialize(self):
        return {'uid': self.uid}

    @classmethod
    def deserialize(cls, data):
        return cls(uid=data['uid'])


class TestHeroGood(goods_types.BaseGoodType):

    def __init__(self, **kwargs):
        super(TestHeroGood, self).__init__(**kwargs)
        self._clear()

    def _clear(self):
        self._goods = {}
        self.extracted_goods = []
        self.inserted_goods = []

    def deserialize_item(self, data):
        return TestGoodItem.deserialize(data)

    def has_good(self, container, good_uid):
        return good_uid in self._goods

    def extract_good(self, container, good_uid):
        self.extracted_goods.append(good_uid)
        return self._goods[good_uid]

    def insert_good(self, container, good):
        self.inserted_goods.append((container.id, good.uid))

    def create_good(self, uid):
        good = objects.Good(type=self.uid,
                            name=u'name-'+uid,
                            uid=uid,
                            item=TestGoodItem(uid=uid))

        self._goods[uid] = good
        return good

    def remove_good(self, good_uid):
        del self._goods[good_uid]

    def register(self, *argv, **kwargs):
        super(TestHeroGood, self).register(*argv, **kwargs)
        self._clear()




test_hero_good = TestHeroGood(uid='test-hero-good', name='test-hero-good-name', description='test-hero-good-description')
