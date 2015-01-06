# coding: utf-8

from dext.common.utils import discovering

from the_tale import amqp_environment

from the_tale.market import exceptions


_GOODS_TYPES = {}


def get_type(type):
    return _GOODS_TYPES[type]

def get_types():
    return _GOODS_TYPES.itervalues()


class BaseGoodType(object):

    def __init__(self, uid, name, description, item_uid_prefix):
        self.uid = uid
        self.name = name
        self.description = description
        self.item_uid_prefix = item_uid_prefix

    def register(self):
        if self.uid in _GOODS_TYPES:
            raise exceptions.DuplicateGoodTypeUIDError(good_type=self.__class__, uid=self.uid)

        _GOODS_TYPES[self.uid] = self

    def unregister(self):
        if self.uid in _GOODS_TYPES:
            del _GOODS_TYPES[self.uid]

    def is_item_tradable(self, item):
        raise NotImplementedError()

    def sync_added_item(self, account_id, item):
        if self.is_item_tradable(item):
            amqp_environment.environment.workers.market_manager.cmd_add_item(account_id, self.create_good(item))

    def sync_removed_item(self, account_id, item):
        if self.is_item_tradable(item):
            amqp_environment.environment.workers.market_manager.cmd_remove_item(account_id, self.create_good(item))

    def all_goods(self, container):
        raise NotImplementedError()

    def create_good(self, item):
        raise NotImplementedError()

    def serialize_item(self, item):
        raise NotImplementedError()

    def deserialize_item(self, data):
        raise NotImplementedError()

    def has_good(self, container, good_uid):
        raise NotImplementedError()

    def extract_good(self, container, good_uid):
        raise NotImplementedError()

    def insert_good(self, container, good):
        raise NotImplementedError()

    # def get_goods(self, account_id):
    #     raise NotImplementedError()


@discovering.automatic_discover(_GOODS_TYPES, 'goods_types')
def autodiscover(container, module):
    for obj in (getattr(module, name) for name in dir(module)):
        if isinstance(obj, BaseGoodType):
            obj.register()


class TestGoodItem(object):

    def __init__(self, uid):
        self.uid = uid

    def serialize(self):
        return {'uid': self.uid}

    @classmethod
    def deserialize(cls, data):
        return cls(uid=data['uid'])


class TestHeroGood(BaseGoodType):

    def __init__(self, **kwargs):
        super(TestHeroGood, self).__init__(**kwargs)
        self._clear()

    def _clear(self):
        self._goods = {}
        self.extracted_goods = []
        self.inserted_goods = []
        self.all_goods_for_sync = []

    def serialize_item(self, item):
        return item.serialize()

    def deserialize_item(self, data):
        return TestGoodItem.deserialize(data)

    def all_goods(self, container):
        return self.all_goods_for_sync

    def has_good(self, container, good_uid):
        return good_uid in self._goods

    def extract_good(self, container, good_uid):
        self.extracted_goods.append(good_uid)
        return self._goods[good_uid]

    def insert_good(self, container, good):
        self.inserted_goods.append((container.id, good.uid))

    def create_good(self, uid):
        from the_tale.market import objects
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


test_hero_good = TestHeroGood(uid='test-hero-good', name='test-hero-good-name', description='test-hero-good-description', item_uid_prefix='test#')
