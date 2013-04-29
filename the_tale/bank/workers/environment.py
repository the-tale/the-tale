# coding: utf-8
from bank.workers.bank import Worker as Bank

class QUEUE:
    MESSAGE_SENDER_MESSAGES = 'bank_messages_queue'
    MESSAGE_SENDER_STOP = 'bank_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.bank = Bank(messages_queue=QUEUE.BANK_MESSAGES_QUEUE, stop_queue=QUEUE.BANK_STOP)

    def deinitialize(self):
        self.bank.close_queries()

    def clean_queues(self):
        self.bank.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
