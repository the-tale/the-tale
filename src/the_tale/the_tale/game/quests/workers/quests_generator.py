# coding: utf-8
import sys
import collections

from the_tale import amqp_environment

from the_tale.common.utils.workers import BaseWorker

from the_tale.game.quests import logic


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 0
    NO_CMD_TIMEOUT = 0.1

    def initialize(self):
        if self.initialized:
            self.logger.warn('WARNING: quests generator already initialized, do reinitialization')

        self.initialized = True

        self.requests_query = collections.deque()
        self.requests_heroes_infos = {}

        self.logger.info('QUEST GENERATOR INITIALIZED')

    def process_no_cmd(self):
        if self.initialized:
            self.generate_quest()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True

        self.logger.info('QUESTS GENERATOR STOPPED')

        self.stop_queue.put({'code': 'stopped', 'worker': 'quests_generator'}, serializer='json', compression=None)

    def cmd_request_quest(self, account_id, hero_info):
        self.send_cmd('request_quest', {'account_id': account_id,
                                        'hero_info': hero_info})

    def process_request_quest(self, account_id, hero_info):
        self.requests_heroes_infos[account_id] = logic.HeroQuestInfo.deserialize(hero_info)
        if account_id not in self.requests_query:
            self.requests_query.append(account_id)

    def generate_quest(self):
        if not self.requests_query:
            return

        account_id = self.requests_query.popleft()
        hero_info = self.requests_heroes_infos.pop(account_id)

        try:
            knowledge_base = logic.create_random_quest_for_hero(hero_info, logger=self.logger)
        except Exception:
            self.logger.error('exception in quest generation')
            self.logger.error('Exception',
                              exc_info=sys.exc_info(),
                              extra={} )
            self.logger.error('continue processing')
            return

        amqp_environment.environment.workers.supervisor.cmd_setup_quest(account_id, knowledge_base.serialize())
