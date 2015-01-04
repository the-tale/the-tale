# coding: utf-8

from dext.common.utils import s11n

from the_tale import amqp_environment

from the_tale.market import models
from the_tale.market import objects
from the_tale.market import relations


def load_lot(id):
    try:
        model = models.Lot.objects.get(id=id)
    except models.Lot.DoesNotExist:
        return None

    return objects.Lot.from_model(model)

def save_lot(lot):
    models.Lot.objects.filter(id=lot.id).update(**lot.to_model_fields())


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


def send_good_to_market(seller_id, good, price):
    from the_tale.common.postponed_tasks import PostponedTaskPrototype
    from the_tale.market import postponed_tasks

    logic_task = postponed_tasks.CreateLotTask(account_id=seller_id,
                                               good_type=good.type,
                                               good_uid=good.uid,
                                               price=price)

    task = PostponedTaskPrototype.create(logic_task)

    amqp_environment.environment.workers.market_manager.cmd_logic_task(seller_id, task.id)

    return task


def purchase_lot(buyer_id, lot):
    from the_tale.common.postponed_tasks import PostponedTaskPrototype
    from the_tale.bank import transaction as bank_transaction
    from the_tale.bank import prototypes as bank_prototypes
    from the_tale.bank import relations as bank_relations
    from the_tale.market import postponed_tasks

    invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                      recipient_id=lot.seller_id,
                                                      sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                      sender_id=buyer_id,
                                                      currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                      amount=lot.price,
                                                      description=u'Покупка «%s»' % lot.name,
                                                      operation_uid=u'market-buy-lot-%s' % lot.type)


    transaction = bank_transaction.Transaction(invoice.id)

    logic_task = postponed_tasks.BuyLotTask(seller_id=lot.seller_id,
                                            buyer_id=buyer_id,
                                            lot_id=lot.id,
                                            transaction=transaction)

    task = PostponedTaskPrototype.create(logic_task)

    amqp_environment.environment.workers.market_manager.cmd_logic_task(buyer_id, task.id)

    return task
