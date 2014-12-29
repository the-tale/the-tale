# coding: utf-8

from dext.common.utils import s11n

from the_tale.market import models
from the_tale.market import objects
from the_tale.market import relations


def load_lot(id):
    try:
        model = models.Lot.objects.get(id=id)
    except models.Lot.DoesNotExists:
        return None

    return objects.Lot.from_model(model)


def load_lots_from_query(query):
    return [objects.Lot.from_model(model) for model in query]


def has_lot(account_id, good_uid):
    return models.Lot.objects.filter(seller_id=account_id, good_uid=good_uid).exists()


def reserve_lot(account_id, good, price):
    model = models.Lot.objects.create(type=good.type,
                                      good_uid=good.uid,
                                      seller_id=account_id,
                                      name=good.name,
                                      state=relations.LOT_STATE.RESERVED,
                                      price=price,
                                      data=s11n.to_json({'good': good.serialize()}))
    return objects.Lot.from_model(model)


def rollback_lot(account_id, good):
    models.Lot.objects.filter(type=good.type, good_uid=good.uid, seller_id=account_id, state=relations.LOT_STATE.RESERVED).delete()

def activate_lot(account_id, good):
    models.Lot.objects.filter(type=good.type, good_uid=good.uid, seller_id=account_id, state=relations.LOT_STATE.RESERVED).update(state=relations.LOT_STATE.ACTIVE)


def load_goods(account_id):
    try:
        model = models.Goods.objects.get(account_id=account_id)
    except models.Goods.DoesNotExists:
        return None

    return objects.Goods.from_model(model)


def create_goods(account_id):
    model = models.Goods.objects.create(account_id=account_id)
    return objects.Goods.from_model(model)

def save_goods(goods):
    models.Goods.objects.filter(id=goods.id).update(**goods.to_model_fields())
