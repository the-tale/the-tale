# coding: utf-8

from the_tale.common.utils.workers import BaseWorker


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 0.25

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('MARKET MANAGER INITIALIZED')

    def process_no_cmd(self):
        pass

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        pass

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'market_manager'}, serializer='json', compression=None)
        self.logger.info('MARKET MANAGER STOPPED')
