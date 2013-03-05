# coding: utf-8

from dext.settings import settings
from dext.utils.decorators import nested_commit_on_success

import rels
from rels.django_staff import DjangoEnum

from collections import namedtuple

from game.balance import formulas as f

from game.models import SupervisorTask, SupervisorTaskMember, SUPERVISOR_TASK_TYPE
from game.exceptions import GameException


class MONTHS(DjangoEnum):
    date_text = rels.Column()

    _records = ( ('COLD',  1, u'холодный месяц', u'холодного месяца'),
                 ('CRUDE', 2, u'сырой месяц',    u'сырого месяца'),
                 ('HOT',   3, u'жаркий месяц',   u'жаркого месяца'),
                 ('DRY',   4, u'сухой месяц',    u'сухого месяца') )


class GameTime(namedtuple('GameTimeTuple', ('year', 'month', 'day', 'hour', 'minute', 'second'))):

    @classmethod
    def create_from_turn(cls, turn_number):
        return cls(*f.turns_to_game_time(turn_number))

    @property
    def verbose_date(self):
        return u'%(day)d день %(month)s %(year)d года' % {'day': self.day,
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



class SupervisorTaskPrototype(object):

    def __init__(self, model):
        self.model = model
        self.captured_members = set()


    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(SupervisorTask.objects.get(id=id_))
        except SupervisorTask.DoesNotExist:
            return None


    @property
    def id(self): return self.model.id

    @property
    def type(self): return self.model.type


    @property
    def members(self):
        if not hasattr(self, '_members'):
            self._members = set(SupervisorTaskMember.objects.filter(task=self.model).values_list('account_id', flat=True))
        return self._members

    def capture_member(self, account_id):
        self.captured_members.add(account_id)

    @property
    def all_members_captured(self): return self.members == self.captured_members

    @classmethod
    @nested_commit_on_success
    def create_arena_pvp_1x1(cls, account_1, account_2):

        model = SupervisorTask.objects.create(type=SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1)

        SupervisorTaskMember.objects.create(task=model, account=account_1.model)
        SupervisorTaskMember.objects.create(task=model, account=account_2.model)

        return cls(model)


    @nested_commit_on_success
    def process(self):

        if not self.all_members_captured:
            raise GameException('try process supervisor task %d when not all members captured members: %r, captured members: %r' % (self.id, self.members, self.captured_members))

        if self.type == SUPERVISOR_TASK_TYPE.ARENA_PVP_1X1:
            return self.process_arena_pvp_1x1()


    def process_arena_pvp_1x1(self):
        from accounts.prototypes import AccountPrototype
        from game.actions.prototypes import ActionMetaProxyPrototype
        from game.actions.meta_actions import MetaActionArenaPvP1x1Prototype
        from game.logic_storage import LogicStorage
        from game.pvp.prototypes import Battle1x1Prototype
        from game.pvp.models import BATTLE_1X1_STATE
        from game.bundles import BundlePrototype

        storage = LogicStorage()

        account_1_id, account_2_id = list(self.members)

        account_1 = AccountPrototype.get_by_id(account_1_id)
        account_2 = AccountPrototype.get_by_id(account_2_id)

        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1_id]
        hero_2 = storage.accounts_to_heroes[account_2_id]

        meta_action_battle = MetaActionArenaPvP1x1Prototype.create(storage, hero_1, hero_2)

        bundle = BundlePrototype.create()

        ActionMetaProxyPrototype.create(parent=storage.heroes_to_actions[hero_1.id][-1], _bundle_id=bundle.id, meta_action=meta_action_battle)
        ActionMetaProxyPrototype.create(parent=storage.heroes_to_actions[hero_2.id][-1], _bundle_id=bundle.id, meta_action=meta_action_battle)

        storage.save_required.add(hero_1.id)
        storage.save_required.add(hero_2.id)
        storage.save_changed_data()

        battle_1 = Battle1x1Prototype.get_active_by_account_id(account_1_id)
        battle_1.state = BATTLE_1X1_STATE.PROCESSING
        battle_1.save()

        battle_2 = Battle1x1Prototype.get_active_by_account_id(account_2_id)
        battle_2.state = BATTLE_1X1_STATE.PROCESSING
        battle_2.save()

    def remove(self):
        self.model.delete()
