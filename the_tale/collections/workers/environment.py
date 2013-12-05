# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.collections.workers.items_manager import Worker as ItemsManager


class Environment(BaseEnvironment):

    def initialize(self):
        self.items_manager = ItemsManager(messages_queue='items_manager_queue', stop_queue='items_manager_queue_stop')


workers_environment = Environment()
