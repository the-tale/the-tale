# coding: utf-8

import collections

from django.db import transaction

import rels
from rels.django import DjangoEnum

from dext.settings import settings

from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.game.balance import formulas as f

from the_tale.game.models import SupervisorTask, SupervisorTaskMember, SUPERVISOR_TASK_TYPE

from the_tale.game.conf import game_settings
from the_tale.game import relations
from the_tale.game import exceptions


class MONTHS(DjangoEnum):
    date_text = rels.Column()

    records = ( ('COLD',  1, u'холодный месяц', u'холодного месяца'),
                 ('CRUDE', 2, u'сырой месяц',    u'сырого месяца'),
                 ('HOT',   3, u'жаркий месяц',   u'жаркого месяца'),
                 ('DRY',   4, u'сухой месяц',    u'сухого месяца') )


class GameTime(collections.namedtuple('GameTimeTuple', ('year', 'month', 'day', 'hour', 'minute', 'second'))):

    @classmethod
    def create_from_turn(cls, turn_number):
        return cls(*f.turns_to_game_time(turn_number))

    @property
    def verbose_date(self):
        return u'%(day)d %(month)s %(year)d года' % {'day': self.day,
                                                     'month': MONTHS(self.month).date_text,
                                                     'year': self.year}
    @property
    def verbose_date_short(self):
        return '%d-%d-%d' % (self.day, self.month, self.year)

    @property
    def verbose_time(self):
        return u'%(hour).2d:%(minute).2d' % {'hour': self.hour,
                                             'minute': self.minute}
    def month_record(self): return MONTHS(self.month)


class TimePrototype(object):

    def __init__(self, turn_number):
        self.turn_number = turn_number

    @property
    def game_time(self): return GameTime(*f.turns_to_game_time(self.turn_number))

    @classmethod
    def get_current_time(cls):
        return cls(turn_number=cls.get_current_turn_number())

    @classmethod
    def get_current_turn_number(cls):
        if 'turn number' not in settings:
            settings['turn number'] = '0'
        return int(settings['turn number'])

    def increment_turn(self):
        self.turn_number += 1
        self.save()

    def save(self):
        settings['turn number'] = str(self.turn_number)

    def ui_info(self):
        game_time = self.game_time
        return { 'number': self.turn_number,
                 'verbose_date': game_time.verbose_date,
                 'verbose_time': game_time.verbose_time }



class SupervisorTaskPrototype(BasePrototype):
    _model_class = SupervisorTask
    _readonly = ('id', 'type')
    _bidirectional = ()
    _get_by = ('id', )

    def __init__(self, model):
        super(SupervisorTaskPrototype, self).__init__(model=model)
        self.captured_members = set()

    @lazy_property
    def members(self): return set(SupervisorTaskMember.objects.filter(task=self._model).values_list('account_id', flat=True))

    def capture_member(self, account_id):
        self.captured_members.add(account_id)

    @property
    def all_members_captured(self): return self.members == self.captured_members

    @classmethod
    @transaction.atomic
    def create_arena_pvp_1x1(cls, account_1, account_2):

        model = cls._model_class.objects.create(type=SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1)

        SupervisorTaskMember.objects.create(task=model, account=account_1._model)
        SupervisorTaskMember.objects.create(task=model, account=account_2._model)

        return cls(model)

    @transaction.atomic
    def process(self):

        if not self.all_members_captured:
            raise exceptions.SupervisorTaskMemberMissedError(task_id=self.id, members=self.members, captured_members=self.captured_members)

        if self.type == SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1:
            return self.process_arena_pvp_1x1()


    def process_arena_pvp_1x1(self): # pylint: disable=R0914
        from the_tale.accounts.prototypes import AccountPrototype
        from the_tale.game.actions.prototypes import ActionMetaProxyPrototype
        from the_tale.game.actions.meta_actions import MetaActionArenaPvP1x1Prototype
        from the_tale.game.logic_storage import LogicStorage
        from the_tale.game.pvp.prototypes import Battle1x1Prototype
        from the_tale.game.pvp.models import BATTLE_1X1_STATE
        from the_tale.game.bundles import BundlePrototype

        storage = LogicStorage()

        account_1_id, account_2_id = list(self.members)

        account_1 = AccountPrototype.get_by_id(account_1_id)
        account_2 = AccountPrototype.get_by_id(account_2_id)

        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1_id]
        hero_2 = storage.accounts_to_heroes[account_2_id]

        old_bundle_1_id = hero_1.actions.current_action.bundle_id
        old_bundle_2_id = hero_2.actions.current_action.bundle_id

        bundle = BundlePrototype.create()

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(storage, hero_1, hero_2, bundle=bundle)

        ActionMetaProxyPrototype.create(hero=hero_1, _bundle_id=bundle.id, meta_action=meta_action_battle)
        ActionMetaProxyPrototype.create(hero=hero_2, _bundle_id=bundle.id, meta_action=meta_action_battle)

        storage.merge_bundles([old_bundle_1_id, old_bundle_2_id], bundle.id)

        storage.save_bundle_data(bundle.id, update_cache=True)
        # storage.save_changed_data()

        battle_1 = Battle1x1Prototype.get_by_account_id(account_1_id)
        battle_1.state = BATTLE_1X1_STATE.PROCESSING
        battle_1.save()

        battle_2 = Battle1x1Prototype.get_by_account_id(account_2_id)
        battle_2.state = BATTLE_1X1_STATE.PROCESSING
        battle_2.save()

    def remove(self):
        self._model.delete()


class GameState(object):

    @classmethod
    def _set_state(cls, state):
        settings[game_settings.GAME_STATE_KEY] = str(state.value)

    @classmethod
    def _get_state(cls):
        return relations.GAME_STATE.index_value[int(settings.get(game_settings.GAME_STATE_KEY, relations.GAME_STATE.STOPPED.value))]

    @classmethod
    def state(cls):
        return cls._get_state()

    @classmethod
    def stop(cls):
        cls._set_state(relations.GAME_STATE.STOPPED)

    @classmethod
    def start(cls):
        cls._set_state(relations.GAME_STATE.WORKING)

    @classmethod
    def is_stopped(cls):
        return cls._get_state().is_STOPPED

    @classmethod
    def is_working(cls):
        return cls._get_state().is_WORKING
