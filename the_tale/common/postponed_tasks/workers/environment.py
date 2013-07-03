# coding: utf-8

from common.postponed_tasks.workers.refrigerator import Worker as Refrigerator
from common.amqp_queues.environment import BaseEnvironment


class Environment(BaseEnvironment):

    def initialize(self):
        self.refrigerator = Refrigerator(messages_queue='refrigerator_messages_queue', stop_queue='refrigerator_stop_queue')


workers_environment = Environment()
workers_environment.initialize()
