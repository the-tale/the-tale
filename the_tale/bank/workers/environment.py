# coding: utf-8

from the_tale.common.amqp_queues.environment import BaseEnvironment

from the_tale.bank.workers.bank_processor import Worker as BankProcessor
from the_tale.bank.dengionline.workers.banker import Worker as DOBanker
from the_tale.bank.xsolla.workers.banker import Worker as XsollaBanker


class Environment(BaseEnvironment):

    def initialize(self):
        self.bank_processor = BankProcessor(messages_queue='bank_processor_messages_queue', stop_queue='bank_processor_stop')
        self.dengionline_banker = DOBanker(messages_queue='dengionline_banker_messages_queue', stop_queue='dengionline_banker_stop')
        self.xsolla_banker = XsollaBanker(messages_queue='xsolla_banker_messages_queue', stop_queue='xsolla_banker_stop')


workers_environment = Environment()
