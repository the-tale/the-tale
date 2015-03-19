# coding: utf-8

import datetime

import rels
from rels.django import DjangoEnum

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import prototypes as account_prototypes
from the_tale.accounts.personal_messages import prototypes as personal_messages_prototypes
from the_tale.accounts import logic as accounts_logic

from the_tale.bank import transaction as bank_transaction
from the_tale.bank import prototypes as bank_prototypes
from the_tale.bank import relations as bank_relations

from the_tale.market import logic
from the_tale.market import objects
from the_tale.market import goods_types
from the_tale.market import relations
from the_tale.market import conf



def good_bought_message(lot):
    from the_tale.portal import logic as portal_logic

    template = u'Поздравляем! Кто-то купил «%(good)s», Вы получаете печеньки: %(price)d шт.'
    return template % {'good': lot.name,
                       'price': lot.price - lot.commission,
                       'static_path': (portal_logic.cdn_paths()['STATIC_CONTENT'] + 'images/cookies.png')}


def good_timeout_message(lot):
    template = u'Закончилось время продажи «%(good)s». Так как Ваш товар никто не купил, Вы получаете его обратно.'
    return template % {'good': lot.name}



class CreateLotTask(PostponedLogic):
    TYPE = 'create-lot-task'

    class STATE(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'в очереди'),
                    ('PROCESSED', 2, u'обработано'),
                    ('NO_GOOD', 3, u'нет такого товара'),
                    ('CAN_NOT_PROCESS', 4, u'не удалось обработать'),
                    ('BANNED', 5, u'игрок забанен'),
                    ('ALREADY_RESERVED', 6, u'лот уже зарезервирован') )


    class STEP(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'начало обработки'),
                    ('RESERVED', 2, u'лот зарезервирован'),
                    ('GOTTEN', 3, u'товар получен у героя'),
                    ('ACTIVATED', 4, u'лот активирован'),
                    ('ROLLBACK', 5, u'необходимо откатить лот'),
                    ('ROLLBACKED', 6, u'лот откачен') )


    def __init__(self, account_id, good_type, good_uid, price, step=STEP.UNPROCESSED, state=STATE.UNPROCESSED, lot_id=None):
        super(CreateLotTask, self).__init__()
        self.account_id = account_id
        self.good_type = good_type
        self.good_uid = good_uid
        self.lot_id = lot_id
        self.price = price
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)

    def serialize(self):
        return { 'account_id': self.account_id,
                 'good_type': self.good_type,
                 'good_uid': self.good_uid,
                 'price': self.price,
                 'state': self.state.value,
                 'step': self.step.value,
                 'lot_id': self.lot_id}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage=None): # pylint: disable=R0911

        good_type = goods_types.get_type(self.good_type)

        if self.step.is_UNPROCESSED:

            account = account_prototypes.AccountPrototype.get_by_id(self.account_id)

            if account.is_ban_game:
                main_task.comment = 'account is banned'
                self.state = self.STATE.BANNED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            goods = logic.load_goods(self.account_id)

            if not goods.has_good(self.good_uid):
                main_task.comment = 'account has no good %s' % self.good_uid
                self.state = self.STATE.NO_GOOD
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if logic.has_lot(self.account_id, self.good_uid):
                main_task.comment = u'account %d has lot for <%s> %s' % (self.account_id, self.good_type, self.good_uid)
                self.state = self.STATE.ALREADY_RESERVED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            lot = logic.reserve_lot(self.account_id, goods.get_good(self.good_uid), price=self.price)

            self.lot_id = lot.id

            main_task.extend_postsave_actions((lambda: environment.workers.logic.cmd_logic_task(self.account_id, main_task.id),))

            self.step = self.STEP.RESERVED
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_RESERVED:
            hero = storage.accounts_to_heroes[self.account_id]

            if not good_type.has_good(hero, self.good_uid):
                main_task.comment = 'hero has no good %s' % self.good_uid
                self.state = self.STATE.NO_GOOD
                self.step = self.STEP.ROLLBACK
                main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_task(self.account_id, main_task.id),))
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

            good_type.extract_good(hero, self.good_uid)

            storage.save_bundle_data(hero.actions.current_action.bundle_id)

            main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_logic_task(self.account_id, main_task.id),))

            self.step = self.STEP.GOTTEN
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_ROLLBACK:
            goods = logic.load_goods(self.account_id)

            lot = logic.load_lot(self.lot_id)
            lot.state = relations.LOT_STATE.CLOSED_BY_ERROR
            logic.save_lot(lot)

            self.step = self.STEP.ROLLBACKED
            self.state = self.STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


        if self.step.is_GOTTEN:
            goods = logic.load_goods(self.account_id)

            lot = logic.load_lot(self.lot_id)
            lot.state = relations.LOT_STATE.ACTIVE
            logic.save_lot(lot)

            goods.remove_good(self.good_uid)
            logic.save_goods(goods)
            self.step = self.STEP.ACTIVATED
            self.state = self.STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS




class BuyLotTask(PostponedLogic):
    TYPE = 'buy-lot-task'

    class STATE(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'в очереди'),
                    ('PROCESSED', 2, u'обработано'),
                    ('WRONG_LOT_STATE', 3, u'неверное состояние лота'),
                    ('WRONG_TRANSACTION_STATE', 4, u'неверное состояние транзакции'),
                    ('TRANSACTION_REJECTED', 5, u'в транзакции отказано'),
                    ('BUYER_BANNED', 6, u'игрок забанен'),
                    )


    class STEP(DjangoEnum):
        records = ( ('FREEZE_LOT', 0, u'заморозить лот'),
                    ('FREEZE_MONEY', 1, u'заморозить средства'),
                    ('RECEIVE_GOOD', 2, u'получить предмет'),
                    ('REMOVE_LOT', 3, u'удалить лот'),
                    ('SUCCESS', 4, u'покупка завершена'),
                    ('ERROR', 5, u'ошибка'))


    def __init__(self, buyer_id, seller_id, lot_id, transaction, good_type=None, good=None, step=STEP.FREEZE_MONEY, state=STATE.UNPROCESSED):
        super(BuyLotTask, self).__init__()
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.lot_id = lot_id
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)
        self.good_type = goods_types.get_type(good_type) if good_type else None
        self.good = objects.Good.deserialize(good) if isinstance(good, dict) else good
        self.transaction = bank_transaction.Transaction.deserialize(transaction) if isinstance(transaction, dict) else transaction

    def serialize(self):
        return { 'buyer_id': self.buyer_id,
                 'seller_id': self.seller_id,
                 'lot_id': self.lot_id,
                 'state': self.state.value,
                 'good_type': self.good_type.uid if self.good_type else None,
                 'good': self.good.serialize() if self.good else None,
                 'transaction': self.transaction.serialize(),
                 'step': self.step.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage=None): # pylint: disable=R0911

        if self.step.is_FREEZE_MONEY:

            transaction_state = self.transaction.get_invoice_state()

            if transaction_state.is_REQUESTED:
                return POSTPONED_TASK_LOGIC_RESULT.WAIT

            if transaction_state.is_REJECTED:
                self.state = self.STATE.TRANSACTION_REJECTED
                main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if not transaction_state.is_FROZEN:
                self.state = self.STATE.WRONG_TRANSACTION_STATE
                main_task.comment = 'wrong invoice %d state %r on freezing step' % (self.transaction.invoice_id, transaction_state)
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_logic_task(self.buyer_id, main_task.id),))
            self.step = self.STEP.FREEZE_LOT
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_FREEZE_LOT:
            buyer = account_prototypes.AccountPrototype.get_by_id(self.buyer_id)

            if buyer.is_ban_game:
                main_task.comment = 'account is banned'
                self.transaction.cancel()
                self.state = self.STATE.BUYER_BANNED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            lot = logic.load_lot(self.lot_id)

            if not lot.state.is_ACTIVE:
                main_task.comment = 'lot is not active, real state is: %s' % lot.state.name
                self.transaction.cancel()
                self.state = self.STATE.WRONG_LOT_STATE
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            self.good_type = goods_types.get_type(lot.type)
            self.good = lot.good

            lot.state = relations.LOT_STATE.FROZEN
            logic.save_lot(lot)

            main_task.extend_postsave_actions((lambda: environment.workers.logic.cmd_logic_task(self.buyer_id, main_task.id),))

            self.step = self.STEP.RECEIVE_GOOD
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_RECEIVE_GOOD:
            hero = storage.accounts_to_heroes[self.buyer_id]

            # TODO: save hero after receive item? and after extract too?...
            self.good_type.insert_good(hero, self.good)

            storage.save_bundle_data(hero.actions.current_action.bundle_id)

            main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_logic_task(self.buyer_id, main_task.id),))

            self.step = self.STEP.REMOVE_LOT
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_REMOVE_LOT:
            lot = logic.load_lot(self.lot_id)

            lot.buyer_id = self.buyer_id
            lot.state = relations.LOT_STATE.CLOSED_BY_BUYER
            lot.closed_at = datetime.datetime.now()
            logic.save_lot(lot)

            self.transaction.confirm()

            seller = account_prototypes.AccountPrototype.get_by_id(lot.seller_id)

            personal_messages_prototypes.MessagePrototype.create(accounts_logic.get_system_user(), seller, good_bought_message(lot))

            bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                    recipient_id=seller.id,
                                                    sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                    sender_id=0,
                                                    currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                    amount=-lot.commission,
                                                    description_for_sender=u'Комиссия с продажи «%s»' % lot.name,
                                                    description_for_recipient=u'Комиссия с продажи «%s»' % lot.name,
                                                    operation_uid=u'%s-%s' % (conf.settings.COMMISSION_OPERATION_UID, lot.type),
                                                    force=True)

            self.state = self.STATE.PROCESSED
            self.step = self.STEP.SUCCESS
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS




class CloseLotByTimoutTask(PostponedLogic):
    TYPE = 'close-lot-by-timeout-task'

    class STATE(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'в очереди'),
                    ('PROCESSED', 2, u'обработано'),
                    ('WRONG_LOT_STATE', 3, u'неверное состояние лота'),
                    )


    class STEP(DjangoEnum):
        records = ( ('FREEZE_LOT', 0, u'заморозить лот'),
                    ('RETURN_GOOD', 2, u'вернуть предмет'),
                    ('CLOSE_LOT', 3, u'закрыть лот'),
                    ('SUCCESS', 4, u'операция завершена'),
                    ('ERROR', 5, u'ошибка'))


    def __init__(self, lot_id, account_id=None, good_type=None, good=None, step=STEP.FREEZE_LOT, state=STATE.UNPROCESSED):
        super(CloseLotByTimoutTask, self).__init__()
        self.account_id = account_id
        self.lot_id = lot_id
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)
        self.good_type = goods_types.get_type(good_type) if good_type else None
        self.good = objects.Good.deserialize(good) if isinstance(good, dict) else good

    def serialize(self):
        return { 'account_id': self.account_id,
                 'lot_id': self.lot_id,
                 'state': self.state.value,
                 'good_type': self.good_type.uid if self.good_type else None,
                 'good': self.good.serialize() if self.good else None,
                 'step': self.step.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage=None): # pylint: disable=R0911

        if self.step.is_FREEZE_LOT:
            lot = logic.load_lot(self.lot_id)

            if not lot.state.is_ACTIVE:
                main_task.comment = 'lot is not active, real state is: %s' % lot.state.name
                self.state = self.STATE.WRONG_LOT_STATE
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            self.account_id = lot.seller_id
            self.good_type = goods_types.get_type(lot.type)
            self.good = lot.good

            lot.state = relations.LOT_STATE.FROZEN
            logic.save_lot(lot)

            main_task.extend_postsave_actions((lambda: environment.workers.logic.cmd_logic_task(self.account_id, main_task.id),))

            self.step = self.STEP.RETURN_GOOD
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_RETURN_GOOD:
            hero = storage.accounts_to_heroes[self.account_id]

            # TODO: save hero after receive item? and after extract too?...
            self.good_type.insert_good(hero, self.good)

            storage.save_bundle_data(hero.actions.current_action.bundle_id)

            main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_logic_task(self.account_id, main_task.id),))

            self.step = self.STEP.CLOSE_LOT
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_CLOSE_LOT:
            lot = logic.load_lot(self.lot_id)

            lot.state = relations.LOT_STATE.CLOSED_BY_TIMEOUT
            lot.closed_at = datetime.datetime.now()
            logic.save_lot(lot)

            seller = account_prototypes.AccountPrototype.get_by_id(lot.seller_id)

            personal_messages_prototypes.MessagePrototype.create(accounts_logic.get_system_user(), seller, good_timeout_message(lot))

            self.state = self.STATE.PROCESSED
            self.step = self.STEP.SUCCESS
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
