# coding: utf-8

import rels
from rels.django_staff import DjangoEnum

from common.utils.decorators import lazy_property
from common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from bank.transaction import Transaction

from game.heroes.prototypes import HeroPrototype

from accounts.workers.environment import workers_environment as accounts_workers_environment
from accounts.prototypes import AccountPrototype


class BUY_PREMIUM_STATE(DjangoEnum):
    _records = ( ('TRANSACTION_REQUESTED', 1, u'запрошены средства'),
                 ('TRANSACTION_REJECTED', 2, u'недостаточно средств'),
                 ('TRANSACTION_FROZEN', 3, u'средства выделены'),
                 ('WAIT_TRANSACTION_CONFIRMATION', 4, u'ожидает подтверждение платежа'),
                 ('SUCCESSED', 5, u'операция выполнена'),
                 ('ERROR_IN_FREEZING_TRANSACTION',6, u'неверное состояние транзакции при замарозке средств'),
                 ('ERROR_IN_CONFIRM_TRANSACTION', 7, u'неверное состояние транзакции при подтверждении траты'),
                 ('WRONG_TASK_STATE', 8, u'ошибка при обрабокте задачи — неверное состояние') )


class BuyPremium(PostponedLogic):

    TYPE = 'buy-premium'

    def __init__(self, account_id, days, transaction, state=BUY_PREMIUM_STATE.TRANSACTION_REQUESTED):
        self.account_id = account_id
        self.days=days
        self.state = state if isinstance(state, rels.Record) else BUY_PREMIUM_STATE._index_value[state]
        self.transaction = Transaction.deserialize(transaction) if isinstance(transaction, dict) else transaction

    def __eq__(self, other):
        return (self.state == other.state and
                self.days == other.days and
                self.transaction == other.transaction and
                self.account_id == other.account_id)

    def serialize(self):
        return { 'state': self.state.value,
                 'days': self.days,
                 'transaction': self.transaction.serialize(),
                 'account_id': self.account_id }

    @property
    def uuid(self): return self.account_id

    @property
    def error_message(self): return self.state.text

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

    def process(self, main_task, storage=None):

        if self.state._is_TRANSACTION_REQUESTED:
            transaction_state = self.transaction.get_invoice_state()

            if transaction_state._is_REQUESTED:
                return POSTPONED_TASK_LOGIC_RESULT.WAIT
            if transaction_state._is_REJECTED:
                self.state = BUY_PREMIUM_STATE.TRANSACTION_REJECTED
                main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
                return POSTPONED_TASK_LOGIC_RESULT.ERROR
            elif transaction_state._is_FROZEN:
                self.state = BUY_PREMIUM_STATE.TRANSACTION_FROZEN
                main_task.extend_postsave_actions((lambda: accounts_workers_environment.accounts_manager.cmd_task(main_task.id),))
                return POSTPONED_TASK_LOGIC_RESULT.CONTINUE
            else:
                self.state = BUY_PREMIUM_STATE.ERROR_IN_FREEZING_TRANSACTION
                main_task.comment = 'wrong invoice %d state %r on freezing step' % (self.transaction.invoice_id, transaction_state)
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        elif self.state._is_TRANSACTION_FROZEN:
            self.account.prolong_premium(days=self.days)
            self.account.save()
            HeroPrototype.get_by_account_id(self.account.id).cmd_update_with_account_data(self.account)
            self.transaction.confirm()

            self.state = BUY_PREMIUM_STATE.WAIT_TRANSACTION_CONFIRMATION
            return POSTPONED_TASK_LOGIC_RESULT.WAIT

        elif self.state._is_WAIT_TRANSACTION_CONFIRMATION:
            transaction_state = self.transaction.get_invoice_state()

            if transaction_state._is_FROZEN:
                return POSTPONED_TASK_LOGIC_RESULT.WAIT
            elif transaction_state._is_CONFIRMED:
                self.state = BUY_PREMIUM_STATE.SUCCESSED
                return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
            else:
                self.state = BUY_PREMIUM_STATE.ERROR_IN_CONFIRM_TRANSACTION
                main_task.comment = 'wrong invoice %d state %r on confirmation step' % (self.transaction.invoice_id, transaction_state)
                return POSTPONED_TASK_LOGIC_RESULT.ERROR
        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = BUY_PREMIUM_STATE.WRONG_TASK_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
