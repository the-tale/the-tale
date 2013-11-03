# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.accounts.workers.registration import Worker as Registration
from the_tale.accounts.workers.accounts_manager import Worker as AccountsManager


class Environment(BaseEnvironment):

    def initialize(self):
        self.registration = Registration(registration_queue='registration_queue', stop_queue='registration_queue_stop')
        self.accounts_manager = AccountsManager(messages_queue='accounts_manager_queue', stop_queue='accounts_manager_queue_stop')


workers_environment = Environment()
