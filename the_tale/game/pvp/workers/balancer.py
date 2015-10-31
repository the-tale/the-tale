# coding: utf-8
import datetime
import math
import itertools
import collections

from django.db import transaction

from dext.common.amqp_queues import BaseWorker

from the_tale.amqp_environment import environment

from the_tale.common import postponed_tasks

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.prototypes import SupervisorTaskPrototype

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.pvp.conf import pvp_settings
from the_tale.game.pvp.prototypes import Battle1x1Prototype


class PvPBalancerException(Exception): pass


class QueueRecord(collections.namedtuple('QueueRecord', ('account_id', 'created_at', 'battle_id', 'hero_level'))): #pylint: disable=E1001
    __slots__ = ()


class BalancingRecord(collections.namedtuple('BalancingRecord', ('min_level', 'max_level', 'record'))): #pylint: disable=E1001
    __slots__ = ()

    def in_interval(self, level):
        return self.min_level <= level <= self.max_level

    def has_intersections(self, other):
        return self.in_interval(other.record.hero_level) and other.in_interval(self.record.hero_level)



class Worker(BaseWorker):
    STOP_SIGNAL_REQUIRED = False
    GET_CMD_TIMEOUT = 0
    NO_CMD_TIMEOUT = pvp_settings.BALANCER_SLEEP_TIME

    def __init__(self, *argv, **kwargs):
        super(Worker, self).__init__(*argv, **kwargs)
        self.arena_queue = {}

    def process_no_cmd(self):
        if self.initialized:
            self._do_balancing()

    def initialize(self):
        # worker initialized by supervisor
        pass

    def cmd_initialize(self, worker_id):
        self.send_cmd('initialize', {'worker_id': worker_id})

    def process_initialize(self, worker_id):

        if self.initialized:
            self.logger.warn('WARNING: pvp balancer already initialized, do reinitialization')

        self.initialized = True
        self.worker_id = worker_id

        Battle1x1Prototype.reset_waiting_battles()

        self.arena_queue = {}

        self.logger.info('PVP BALANCER INITIALIZED')

        environment.workers.supervisor.cmd_answer('initialize', self.worker_id)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        environment.workers.supervisor.cmd_answer('stop', self.worker_id)
        self.stop_required = True
        self.logger.info('PVP BALANCER STOPPED')

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id):#pylint: disable=W0613
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger, pvp_balancer=self)
        task.do_postsave_actions()

    def add_to_arena_queue(self, hero_id):

        hero = heroes_logic.load_hero(hero_id=hero_id)

        if hero.account_id in self.arena_queue:
            return None

        battle = Battle1x1Prototype.create(AccountPrototype.get_by_id(hero.account_id))

        if not battle.state.is_WAITING:
            raise PvPBalancerException('account %d already has battle not in waiting state' % hero.account_id)

        record = QueueRecord(account_id=battle.account_id,
                             created_at=battle.created_at,
                             battle_id=battle.id,
                             hero_level=hero.level)

        if record.account_id in self.arena_queue:
            raise PvPBalancerException('account %d already added in balancer queue' % record.account_id)

        self.arena_queue[record.account_id] = record

        return battle

    def leave_arena_queue(self, hero_id):
        hero = heroes_logic.load_hero(hero_id=hero_id)

        battle = Battle1x1Prototype.get_by_account_id(hero.account_id)

        if not battle.state.is_WAITING:
            return

        if battle.account_id not in self.arena_queue:
            self.logger.error('can not leave queue: battle %d in waiting state but no in arena queue' % battle.id)
            return

        del self.arena_queue[battle.account_id]

        battle.remove()


    def _get_prepaired_queue(self):

        records = []
        records_to_bots = []

        time_in_level = float(pvp_settings.BALANCING_TIMEOUT) / pvp_settings.BALANCING_MAX_LEVEL_DELTA

        for record in self.arena_queue.values():

            time_delta = (datetime.datetime.now() - record.created_at).total_seconds()

            if time_delta > pvp_settings.BALANCING_TIMEOUT:
                records_to_bots.append(record)
                continue

            balancing_record = BalancingRecord(min_level=int(math.floor(record.hero_level - pvp_settings.BALANCING_MIN_LEVEL_DELTA - time_delta / time_in_level)),
                                               max_level=int(math.ceil(record.hero_level + pvp_settings.BALANCING_MIN_LEVEL_DELTA + time_delta / time_in_level)),
                                               record=record)

            records.append(balancing_record)

        return sorted(records, key=lambda r: r.record.created_at), records_to_bots

    def _search_battles(self, records):

        battle_pairs = []
        records_to_exclude = []

        while records:

            current_record = records[0]

            records.pop(0)

            for index, record in enumerate(records):

                if pvp_settings.BALANCING_WITHOUT_LEVELS or current_record.has_intersections(record):
                    battle_pairs.append((current_record.record, record.record))
                    records.pop(index)
                    records_to_exclude.append(current_record.record)
                    records_to_exclude.append(record.record)
                    break

        return battle_pairs, records_to_exclude

    def _clean_queue(self, records_to_remove, records_to_exclude):
        for record in itertools.chain(records_to_remove, records_to_exclude):
            del self.arena_queue[record.account_id]

        if records_to_remove:
            for record in records_to_remove:
                Battle1x1Prototype.get_by_id(record.battle_id).remove()
            self.logger.info('remove from queue request from the_tale.accounts %r' % (records_to_remove, ))


    def _initiate_battle(self, record_1, record_2, calculate_ratings=False):
        from the_tale.accounts.prototypes import AccountPrototype

        account_1 = AccountPrototype.get_by_id(record_1.account_id)
        account_2 = AccountPrototype.get_by_id(record_2.account_id)

        self.logger.info('start battle between accounts %d and %d' % (account_1.id, account_2.id))

        with transaction.atomic():
            battle_1 = Battle1x1Prototype.get_by_id(record_1.battle_id)
            battle_2 = Battle1x1Prototype.get_by_id(record_2.battle_id)

            battle_1.set_enemy(account_2)
            battle_2.set_enemy(account_1)

            if calculate_ratings and abs(record_1.hero_level - record_2.hero_level) <= pvp_settings.BALANCING_MIN_LEVEL_DELTA:
                battle_1.calculate_rating = True
                battle_2.calculate_rating = True

            battle_1.save()
            battle_2.save()

            task = SupervisorTaskPrototype.create_arena_pvp_1x1(account_1, account_2)

        environment.workers.supervisor.cmd_add_task(task.id)

    def _initiate_battle_with_bot(self, record):

        # search free bot
        # since now bots needed only for PvP, we can do simplified search
        battled_accounts_ids = Battle1x1Prototype._model_class.objects.all().values_list('account_id', flat=True)

        try:
            bot_account = AccountPrototype(model=AccountPrototype._model_class.objects.filter(is_bot=True).exclude(id__in=battled_accounts_ids)[0])
        except IndexError:
            bot_account = None

        if bot_account is None:
            return [record], []

        bot_hero = heroes_logic.load_hero(account_id=bot_account.id)

        self.logger.info('start battle between account %d and bot %d' % (record.account_id, bot_account.id))

        # create battle for bot
        self.add_to_arena_queue(bot_hero.id)
        bot_record = self.arena_queue[bot_account.id]

        self._initiate_battle(record, bot_record, calculate_ratings=False)

        return [], [record, bot_record]


    def _do_balancing(self):

        records_to_remove = []

        records, records_to_bots = self._get_prepaired_queue()

        battle_pairs, records_to_exclude = self._search_battles(records)

        for battle_pair in battle_pairs:
            self._initiate_battle(*battle_pair, calculate_ratings=True)

        for record in records_to_bots:
            _records_to_remove, _records_to_exclude = self._initiate_battle_with_bot(record)
            records_to_remove.extend(_records_to_remove)
            records_to_exclude.extend(_records_to_exclude)

        self._clean_queue(records_to_remove, records_to_exclude)

    def force_battle(self, account_1_id, account_2_id):
        record_1 = self.arena_queue[account_1_id]
        record_2 = self.arena_queue[account_2_id]

        self._initiate_battle(record_1, record_2)
        self._clean_queue(records_to_remove=[], records_to_exclude=[record_1, record_2])
