# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.accounts.achievements.workers.achievements_manager import Worker as AchievementsManager


class Environment(BaseEnvironment):

    def initialize(self):
        self.achievements_manager = AchievementsManager(messages_queue='achievements_manager_queue', stop_queue='achievements_manager_queue_stop')


workers_environment = Environment()
