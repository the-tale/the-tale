# coding: utf-8

from common.amqp_queues.environment import BaseEnvironment

from bank.workers.bank_processor import Worker as BankProcessor
from bank.dengionline.workers.banker import Worker as DOBanker


class Environment(BaseEnvironment):

    def initialize(self):
        self.bank_processor = BankProcessor(messages_queue='bank_processor_messages_queue', stop_queue='bank_processor_stop')
        self.dengionline_banker = DOBanker(messages_queue='dengionline_banker_messages_queue', stop_queue='dengionline_banker_stop')


workers_environment = Environment()
workers_environment.initialize()
