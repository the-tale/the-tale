# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import prototypes as account_prototypes

from the_tale.market import logic
from the_tale.market import goods_types


class CreateLotTask(PostponedLogic):
    TYPE = None

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


    def __init__(self, account_id, good_type, good_uid, price, step=STEP.UNPROCESSED, state=STATE.UNPROCESSED):
        super(CreateLotTask, self).__init__()
        self.account_id = account_id
        self.good_type = good_type
        self.good_uid = good_uid
        self.price = price
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)

    def serialize(self):
        return { 'account_id': self.account_id,
                 'good_type': self.good_type,
                 'good_uid': self.good_uid,
                 'price': self.price,
                 'state': self.state.value,
                 'step': self.step.value}

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

            logic.reserve_lot(self.account_id, goods.get_good(self.good_uid), price=self.price)

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

            main_task.extend_postsave_actions((lambda: environment.workers.market_manager.cmd_logic_task(self.account_id, main_task.id),))

            self.step = self.STEP.GOTTEN
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE


        if self.step.is_ROLLBACK:
            goods = logic.load_goods(self.account_id)
            logic.rollback_lot(self.account_id, goods.get_good(self.good_uid))

            self.step = self.STEP.ROLLBACKED
            self.state = self.STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


        if self.step.is_GOTTEN:
            goods = logic.load_goods(self.account_id)
            logic.activate_lot(self.account_id, goods.get_good(self.good_uid))
            goods.remove_good(self.good_uid)
            logic.save_goods(goods)
            self.step = self.STEP.ACTIVATED
            self.state = self.STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
