# coding: utf-8

from bank.workers.bank_processor import Worker as BankProcessor

class QUEUE:
    BANK_PROCESSOR_MESSAGES = 'bank_processor_messages_queue'
    BANK_PROCESSOR_STOP = 'bank_processor_stop'


class Environment(object):

    def __init__(self):
        pass

    def initialize(self):
        self.bank_processor = BankProcessor(messages_queue=QUEUE.BANK_PROCESSOR_MESSAGES, stop_queue=QUEUE.BANK_PROCESSOR_STOP)

    def deinitialize(self):
        self.bank_processor.close_queries()

    def clean_queues(self):
        self.bank_processor.clean_queues()


workers_environment = Environment()
workers_environment.initialize()
