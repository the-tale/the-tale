# coding: utf-8

from common.amqp_queues.environment import BaseEnvironment

from accounts.workers.registration import Worker as Registration
from accounts.workers.accounts_manager import Worker as AccountsManager


class Environment(BaseEnvironment):

    def initialize(self):
        self.registration = Registration(registration_queue='registration_queue', stop_queue='registration_queue_stop')
        self.accounts_manager = AccountsManager(messages_queue='accounts_manager_queue', stop_queue='accounts_manager_queue_stop')


workers_environment = Environment()
