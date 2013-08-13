# coding: utf-8

import rels
from rels.django_staff import DjangoEnum

from common.utils.decorators import lazy_property
from common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from bank.transaction import Transaction

from game.heroes.prototypes import HeroPrototype

from accounts.workers.environment import workers_environment as accounts_workers_environment
from accounts.prototypes import AccountPrototype

from accounts.payments.relations import PERMANENT_PURCHASE_TYPE


class BASE_BUY_TASK_STATE(DjangoEnum):
    _records = ( ('TRANSACTION_REQUESTED', 1, u'запрошены средства'),
                 ('TRANSACTION_REJECTED', 2, u'недостаточно средств'),
                 ('TRANSACTION_FROZEN', 3, u'средства выделены'),
                 ('WAIT_TRANSACTION_CONFIRMATION', 4, u'ожидает подтверждение платежа'),
                 ('SUCCESSED', 5, u'операция выполнена'),
                 ('ERROR_IN_FREEZING_TRANSACTION',6, u'неверное состояние транзакции при замарозке средств'),
                 ('ERROR_IN_CONFIRM_TRANSACTION', 7, u'неверное состояние транзакции при подтверждении траты'),
                 ('WRONG_TASK_STATE', 8, u'ошибка при обрабокте задачи — неверное состояние') )



class BaseBuyTask(PostponedLogic):
    TYPE = None
    RELATION = BASE_BUY_TASK_STATE

    def __init__(self, account_id, transaction, state=None):
        super(BaseBuyTask, self).__init__()

        if state is None:
            state = self.RELATION.TRANSACTION_REQUESTED

        self.account_id = account_id
        self.state = state if isinstance(state, rels.Record) else self.RELATION._index_value[state]
        self.transaction = Transaction.deserialize(transaction) if isinstance(transaction, dict) else transaction

    def __eq__(self, other):
        return (self.state == other.state and
                self.transaction == other.transaction and
                self.account_id == other.account_id)

    def serialize(self):
        return { 'state': self.state.value,
                 'transaction': self.transaction.serialize(),
                 'account_id': self.account_id }

    @property
    def uuid(self): return self.account_id

    @property
    def error_message(self): return self.state.text

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

    def process_transaction_requested(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state._is_REQUESTED:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        if transaction_state._is_REJECTED:
            self.state = self.RELATION.TRANSACTION_REJECTED
            main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
        elif transaction_state._is_FROZEN:
            self.state = self.RELATION.TRANSACTION_FROZEN
            self.on_process_transaction_requested__transaction_frozen(main_task)
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE
        else:
            self.state = self.RELATION.ERROR_IN_FREEZING_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on freezing step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        main_task.extend_postsave_actions((lambda: accounts_workers_environment.accounts_manager.cmd_task(main_task.id),))

    def on_process_transaction_frozen(self, storage):
        raise NotImplementedError

    def process_transaction_frozen(self, main_task, storage): # pylint: disable=W0613
        self.on_process_transaction_frozen(storage=storage)
        self.transaction.confirm()

        self.state = self.RELATION.WAIT_TRANSACTION_CONFIRMATION
        return POSTPONED_TASK_LOGIC_RESULT.WAIT

    def process_transaction_confirmation(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state._is_FROZEN:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        elif transaction_state._is_CONFIRMED:
            self.state = self.RELATION.SUCCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
        else:
            self.state = self.RELATION.ERROR_IN_CONFIRM_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on confirmation step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


    def process(self, main_task, storage=None): # pylint: disable=W0613

        if self.state._is_TRANSACTION_REQUESTED:
            return self.process_transaction_requested(main_task)

        elif self.state._is_TRANSACTION_FROZEN:
            return self.process_transaction_frozen(main_task, storage=storage)

        elif self.state._is_WAIT_TRANSACTION_CONFIRMATION:
            return self.process_transaction_confirmation(main_task)

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = self.RELATION.WRONG_TASK_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


class BuyPremium(BaseBuyTask):
    TYPE = 'buy-premium'

    def __init__(self, days, **kwargs):
        super(BuyPremium, self).__init__(**kwargs)
        self.days = days

    def __eq__(self, other):
        return (super(BuyPremium, self).__eq__(other) and
                self.days == other.days )

    def serialize(self):
        data = super(BuyPremium, self).serialize()
        data['days'] = self.days
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.prolong_premium(days=self.days)
        self.account.save()
        HeroPrototype.get_by_account_id(self.account.id).cmd_update_with_account_data(self.account)


class BuyEnergyCharges(BaseBuyTask):
    TYPE = 'buy-energy-charges'

    def __init__(self, charges_number, **kwargs):
        super(BuyEnergyCharges, self).__init__(**kwargs)
        self.charges_number = charges_number

    def __eq__(self, other):
        return (super(BuyEnergyCharges, self).__eq__(other) and
                self.charges_number == other.charges_number )

    def serialize(self):
        data = super(BuyEnergyCharges, self).serialize()
        data['charges_number'] = self.charges_number
        return data

    def on_process_transaction_frozen(self, storage, **kwargs):
        hero = storage.accounts_to_heroes[self.account_id]
        hero.energy_charges += self.charges_number

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        from game.workers.environment import workers_environment as game_workers_environment
        main_task.extend_postsave_actions((lambda: game_workers_environment.supervisor.cmd_logic_task(self.account_id, main_task.id),))



class BuyPermanentPurchase(BaseBuyTask):
    TYPE = 'buy-permanent-purchase'

    def __init__(self, purchase_type, **kwargs):
        super(BuyPermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type if isinstance(purchase_type, rels.Record) else PERMANENT_PURCHASE_TYPE._index_value[purchase_type]

    def __eq__(self, other):
        return (super(BuyPermanentPurchase, self).__eq__(other) and
                self.purchase_type == other.purchase_type )

    def serialize(self):
        data = super(BuyPermanentPurchase, self).serialize()
        data['purchase_type'] = self.purchase_type.value
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.permanent_purchases.insert(self.purchase_type)
        self.account.save()
        HeroPrototype.get_by_account_id(self.account.id).cmd_update_with_account_data(self.account)
