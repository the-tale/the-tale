# coding: utf-8

from the_tale import amqp_environment

from the_tale.common.utils.workers import BaseWorker

from the_tale.game.quests import logic


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 60

    def initialize(self):
        if self.initialized:
            self.logger.warn('WARNING: quests generator already initialized, do reinitialization')

        self.initialized = True

        self.logger.info('QUEST GENERATOR INITIALIZED')

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
        knowledge_base = logic.create_random_quest_for_hero(logic.HeroQuestInfo.deserialize(hero_info), logger=self.logger)
        amqp_environment.environment.workers.supervisor.cmd_setup_quest(account_id, knowledge_base.serialize())
