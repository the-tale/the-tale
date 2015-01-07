# coding: utf-8
import datetime

from dext.common.utils import s11n

from the_tale.market import conf


class Good(object):
    __slots__ = ('type', 'name', 'uid', 'item')

    def __init__(self, type, name, uid, item):
        self.type = type
        self.name = name
        self.uid = uid
        self.item = item

    def serialize(self):
        from the_tale.market import goods_types
        return {'type': self.type,
                'name': self.name,
                'uid': self.uid,
                'item': goods_types.get_type(self.type).serialize_item(self.item)}

    @classmethod
    def deserialize(cls, data):
        from the_tale.market import goods_types
        obj = cls(type=data['type'],
                  name=data['name'],
                  uid=data['uid'],
                  item=goods_types.get_type(data['type']).deserialize_item(data['item']))
        return obj


    def html_label(self):
        from the_tale.market import goods_types
        return goods_types.get_type(self.type).item_html(self.item)



class Lot(object):

    __slots__ = ('id', 'type', 'name', 'seller_id', 'buyer_id', 'state', 'good', 'price', 'created_at')

    def __init__(self, id, type, name, seller_id, buyer_id, state, good, price, created_at):
        self.id = id
        self.type = type
        self.name = name
        self.seller_id = seller_id
        self.buyer_id = buyer_id
        self.state = state
        self.good = good
        self.price = price
        self.created_at = created_at

    @property
    def time_to_end(self):
        return max(self.created_at + datetime.timedelta(days=conf.settings.LOT_LIVE_TIME) - datetime.datetime.now(), datetime.timedelta(days=0))

    @classmethod
    def from_model(cls, model):
        data = s11n.from_json(model.data)

        return cls(id=model.id,
                   created_at=model.created_at,
                   type=model.type,
                   name=model.name,
                   seller_id=model.seller_id,
                   buyer_id=model.buyer_id,
                   state=model.state,
                   good=Good.deserialize(data['good']),
                   price=model.price)

    def to_model_fields(self):
        data = {'type': self.type,
                'name': self.name,
                'seller': self.seller_id,
                'buyer': self.buyer_id,
                'state': self.state,
                'good_uid': self.good.uid,
                'data': s11n.to_json({'good': self.good.serialize()}),
                'price': self.price}
        return data


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

    def has_goods(self):
        return bool(self.goods_count())

    def all(self):
        return sorted(self._goods.itervalues(), key=lambda good: good.name)

    def clear(self):
        self._goods = {}
