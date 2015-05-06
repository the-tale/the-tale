# coding: utf-8

from the_tale.common.utils.workers import BaseWorker
from the_tale.common import postponed_tasks

from the_tale.market import logic
from the_tale.market import objects
from the_tale.market import goods_types


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 60

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('MARKET MANAGER INITIALIZED')

    def process_no_cmd(self):
        logic.close_lots_by_timeout()

    def cmd_logic_task(self, account_id, task_id):
        return self.send_cmd('logic_task', {'task_id': task_id,
                                            'account_id': account_id})

    def process_logic_task(self, account_id, task_id): # pylint: disable=W0613
        task = postponed_tasks.PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger)
        task.do_postsave_actions()

    def cmd_add_item(self, account_id, good):
        return self.send_cmd('add_item', {'account_id': account_id,
                                          'good_data': good.serialize()})

    def process_add_item(self, account_id, good_data):
        good = objects.Good.deserialize(good_data)
        goods = logic.load_goods(account_id=account_id)
        goods.add_good(good)
        logic.save_goods(goods)

    def cmd_remove_item(self, account_id, good):
        return self.send_cmd('remove_item', {'account_id': account_id,
                                             'good_data': good.serialize()})

    def process_remove_item(self, account_id, good_data):
        good = objects.Good.deserialize(good_data)
        goods = logic.load_goods(account_id=account_id)
        goods.remove_good(good.uid)
        logic.save_goods(goods)

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'market_manager'}, serializer='json', compression=None)
        self.logger.info('MARKET MANAGER STOPPED')
