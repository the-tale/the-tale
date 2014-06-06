# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.common.utils.decorators import lazy_property
from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.utils.logic import random_value_by_priority

from the_tale.bank.transaction import Transaction

from the_tale.game.relations import HABIT_TYPE
from the_tale.game.heroes.relations import PREFERENCE_TYPE

from the_tale.game.cards.relations import CARD_TYPE

from the_tale.accounts.workers.environment import workers_environment as accounts_workers_environment
from the_tale.accounts.prototypes import AccountPrototype, RandomPremiumRequestPrototype

from the_tale.accounts.payments import relations
from the_tale.accounts.payments.logic import transaction_logic
from the_tale.accounts.payments.conf import payments_settings
from the_tale.accounts.payments import exceptions


class BASE_BUY_TASK_STATE(DjangoEnum):
    records = ( ('TRANSACTION_REQUESTED', 1, u'запрошены средства'),
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
        self.state = state if isinstance(state, rels.Record) else self.RELATION.index_value[state]
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

        if transaction_state.is_REQUESTED:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        if transaction_state.is_REJECTED:
            self.state = self.RELATION.TRANSACTION_REJECTED
            main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
        elif transaction_state.is_FROZEN:
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

        if transaction_state.is_FROZEN:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        elif transaction_state.is_CONFIRMED:
            self.state = self.RELATION.SUCCESSED
            self.process_referrals()
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
        else:
            self.state = self.RELATION.ERROR_IN_CONFIRM_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on confirmation step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


    def process(self, main_task, storage=None): # pylint: disable=W0613

        if self.state.is_TRANSACTION_REQUESTED:
            return self.process_transaction_requested(main_task)

        elif self.state.is_TRANSACTION_FROZEN:
            return self.process_transaction_frozen(main_task, storage=storage)

        elif self.state.is_WAIT_TRANSACTION_CONFIRMATION:
            return self.process_transaction_confirmation(main_task)

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = self.RELATION.WRONG_TASK_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


    def process_referrals(self):
        invoice = self.transaction.get_invoice()

        if invoice.amount >= 0:
            return

        buyer = AccountPrototype.get_by_id(invoice.recipient_id)

        if buyer.referral_of_id is None:
            return

        owner = AccountPrototype.get_by_id(buyer.referral_of_id)

        transaction_logic(account=owner,
                          amount=-int(invoice.amount*payments_settings.REFERRAL_BONUS),
                          description=u'Часть от потраченного вашим рефералом',
                          uid='referral-bonus',
                          force=True)


class BaseLogicBuyTask(BaseBuyTask):

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        from the_tale.game.workers.environment import workers_environment as game_workers_environment
        main_task.extend_postsave_actions((lambda: game_workers_environment.supervisor.cmd_logic_task(self.account_id, main_task.id),))


class BuyPremium(BaseBuyTask):
    TYPE = 'purchase-premium'

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


class BaseBuyHeroMethod(BaseLogicBuyTask):
    TYPE = None
    ARGUMENTS = ()
    METHOD = None

    def __init__(self, **kwargs):
        arguments = {name: value for name, value in kwargs.iteritems() if name in self.ARGUMENTS}
        for name in arguments:
            del kwargs[name]

        super(BaseBuyHeroMethod, self).__init__(**kwargs)

        self.arguments = self.deserialize_arguments(arguments)

    def __eq__(self, other):
        return (super(BaseBuyHeroMethod, self).__eq__(other) and
                self.arguments == other.arguments )

    def serialize_arguments(self):
        return self.arguments

    @classmethod
    def deserialize_arguments(cls, arguments):
        return arguments

    def serialize(self):
        data = super(BaseBuyHeroMethod, self).serialize()
        if set(data.iterkeys()) & set(self.arguments.iterkeys()):
            raise exceptions.BuyHeroMethodSerializationError()
        data.update(self.serialize_arguments())
        return data

    def on_process_transaction_frozen(self, storage, **kwargs):
        hero = storage.accounts_to_heroes[self.account_id]
        self.invoke_method(hero)
        storage.save_bundle_data(hero.actions.current_action.bundle_id, update_cache=True)

    def invoke_method(self, hero):
        getattr(hero, self.METHOD)(**self.arguments)


class BuyEnergy(BaseBuyHeroMethod):
    TYPE = 'purchase-energy'
    ARGUMENTS = ('energy', )
    METHOD = 'purchase_energy_bonus'


class BuyResetHeroPreference(BaseBuyHeroMethod):
    TYPE = 'purchase-reset-hero-preference'
    ARGUMENTS = ('preference_type', )
    METHOD = 'purchase_reset_preference'

    def serialize_arguments(self):
        return {'preference_type': self.arguments['preference_type'].value}

    @classmethod
    def deserialize_arguments(cls, arguments):
        preference_type = arguments['preference_type']
        return {'preference_type': preference_type if isinstance(preference_type, rels.Record) else PREFERENCE_TYPE(preference_type)}


class BuyChangeHeroHabits(BaseBuyHeroMethod):
    TYPE = 'purchase-change-hero-habits'
    ARGUMENTS = ('habit_type', 'habit_value')
    METHOD = 'purchase_change_habits'

    def serialize_arguments(self):
        return {'habit_type': self.arguments['habit_type'].value,
                'habit_value': self.arguments['habit_value']}

    @classmethod
    def deserialize_arguments(cls, arguments):
        habit_type = arguments['habit_type']
        return {'habit_type': habit_type if isinstance(habit_type, rels.Record) else HABIT_TYPE(habit_type),
                'habit_value': arguments['habit_value']}


class BuyResetHeroAbilities(BaseBuyHeroMethod):
    TYPE = 'purchase-reset-hero-abilities'
    ARGUMENTS = ()
    METHOD = 'purchase_reset_abilities'

class BuyRechooseHeroAbilitiesChoices(BaseBuyHeroMethod):
    TYPE = 'purchase-rechoose-hero-abilities-choices'
    ARGUMENTS = ()
    METHOD = 'purchase_rechooce_abilities_choices'


class BuyPermanentPurchase(BaseBuyTask):
    TYPE = 'purchase-permanent-purchase'

    def __init__(self, purchase_type, **kwargs):
        super(BuyPermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type if isinstance(purchase_type, rels.Record) else relations.PERMANENT_PURCHASE_TYPE.index_value[purchase_type]

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


class BuyRandomPremiumChest(BaseBuyHeroMethod):
    TYPE = 'purchase-random-premium-chest'
    ARGUMENTS = ('message', )
    METHOD = None

    MESSAGE = u'''
<strong>Поздравляем!</strong><br/>

Благодаря Вам один из активных игроков получит подписку!<br/>

Вы получаете <strong>%(reward)s</strong><br/>
'''

    NORMAL_ARTIFACT_LABEL = u'%s <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    RARE_ARTIFACT_LABEL = u'<span class="rare-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'
    EPIC_ARTIFACT_LABEL = u'<span class="epic-artifact-label">%s</span> <span class="physic-label">%d</span> <span class="magic-label">%d</span>'

    def get_reward_type(self):
        return random_value_by_priority([(record, record.priority)
                                         for record in relations.RANDOM_PREMIUM_CHEST_REWARD.records])

    def invoke_method(self, hero):
        reward = self.get_reward_type()

        result = getattr(hero, reward.hero_method)(**reward.arguments)

        if reward.is_NORMAL_ARTIFACT:
            message = self.MESSAGE % {'reward': (self.NORMAL_ARTIFACT_LABEL % (result.name, result.power.physic, result.power.magic))}
        elif reward.is_RARE_ARTIFACT:
            message = self.MESSAGE % {'reward': (self.RARE_ARTIFACT_LABEL % (result.name, result.power.physic, result.power.magic))}
        elif reward.is_EPIC_ARTIFACT:
            message = self.MESSAGE % {'reward': (self.EPIC_ARTIFACT_LABEL % (result.name, result.power.physic, result.power.magic))}
        else:
            message = self.MESSAGE % {'reward': reward.description}

        self.arguments['message'] = message

        RandomPremiumRequestPrototype.create(hero.account_id, days=payments_settings.RANDOM_PREMIUM_DAYS)

    @property
    def processed_data(self): return {'message': self.arguments['message'] }



class BuyCards(BaseBuyHeroMethod):
    TYPE = 'purchase-cards'
    ARGUMENTS = ('card_type', 'count')
    METHOD = 'purchase_card'


    def serialize_arguments(self):
        return {'card_type': self.arguments['card_type'].value,
                'count': self.arguments['count']}

    @classmethod
    def deserialize_arguments(cls, arguments):
        card_type = arguments['card_type']
        return {'card_type': card_type if isinstance(card_type, rels.Record) else CARD_TYPE(card_type),
                'count': arguments['count']}
