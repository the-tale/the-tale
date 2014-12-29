# coding: utf-8

from dext.common.utils import s11n


class Good(object):
    __slots__ = ('type', 'name', 'uid', 'item')

    def __init__(self, type, name, uid, item):
        self.type = type
        self.name = name
        self.uid = uid
        self.item = item

    def serialize(self):
        return {'type': self.type,
                'name': self.name,
                'uid': self.uid,
                'item': self.item.serialize()}

    @classmethod
    def deserialize(cls, data):
        from the_tale.market import goods_types
        obj = cls(type=data['type'],
                  name=data['name'],
                  uid=data['uid'],
                  item=goods_types.get_type(data['type']).deserialize_item(data['item']))
        return obj



class Lot(object):

    __slots__ = ('id', 'type', 'name', 'seller_id', 'buyer_id', 'state', 'good', 'price')

    def __init__(self, id, type, name, seller_id, buyer_id, state, good, price):
        self.id = id
        self.type = type
        self.name = name
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.state = state
        self.good = good
        self.price = price

    @classmethod
    def from_model(cls, model):
        data = s11n.from_json(model.data)

        return cls(id=model.id,
                   type=model.type,
                   name=model.name,
                   seller_id=model.seller_id,
                   buyer_id=model.buyer_id,
                   state=model.state,
                   good=Good.deserialize(data['good']),
                   price=model.price)


class Goods(object):
    __slots__ = ('id', 'account_id', '_goods')

    def __init__(self, id, account_id, goods):
        self.id = id
        self.account_id = account_id
        self._goods = goods


    @classmethod
    def from_model(cls, model):
        data = s11n.from_json(model.data)

        goods = {}
        for good_data in data.get('goods', ()):
            good = Good.deserialize(good_data)
            goods[good.uid] = good

        return cls(id=model.id,
                   account_id=model.account_id,
                   goods=goods)

    def to_model_fields(self):
        goods = [good.serialize() for good in self._goods.itervalues()]
        return {'data': s11n.to_json({'goods': goods})}

    def add_good(self, good):
        self._goods[good.uid] = good

    def get_good(self, good_uid):
        return self._goods.get(good_uid)

    def has_good(self, good_uid):
        return self.get_good(good_uid) is not None

    def remove_good(self, good_uid):
        if self.has_good(good_uid):
            del self._goods[good_uid]

    def goods_count(self):
        return len(self._goods)
