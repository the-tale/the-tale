# coding: utf-8

from accounts.workers.registration import Worker as Registration
from accounts.workers.accounts_manager import Worker as AccountsManager


class QUEUE:
    REGISTRATION = 'registration_queue'
    REGISTRATION_STOP = 'registration_queue_stop'
    ACCOUNTS_MANAGER = 'accounts_manager_queue'
    ACCOUNTS_MANAGER_STOP = 'accounts_manager_queue_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.registration = Registration(registration_queue=QUEUE.REGISTRATION, stop_queue=QUEUE.REGISTRATION_STOP)
        self.accounts_manager = AccountsManager(messages_queue=QUEUE.ACCOUNTS_MANAGER, stop_queue=QUEUE.ACCOUNTS_MANAGER_STOP)

    def deinitialize(self):
        self.registration.close_queries()
        self.accounts_manager.close_queries()

    def clean_queues(self):
        self.registration.clean_queues()
        self.accounts_manager.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
