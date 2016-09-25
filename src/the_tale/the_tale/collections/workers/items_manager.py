# coding: utf-8

from the_tale.common.utils.workers import BaseWorker

from the_tale.collections.prototypes import GiveItemTaskPrototype, AccountItemsPrototype
from the_tale.collections.storage import items_storage


class Worker(BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('ITEMS_MANAGER INITIALIZED')

    def add_item(self, item, account_id, notify):
        account_items = AccountItemsPrototype.get_by_account_id(account_id)
        account_items.add_item(item, notify=notify)
        account_items.save()

    def process_no_cmd(self):
        self.add_items()

    def add_items(self):
        for task in GiveItemTaskPrototype.from_query(GiveItemTaskPrototype._db_all()):
            item = items_storage[task.item_id]

            self.logger.info('process task %d for item %d' % (task.id, item.id))

            self.add_item(item, task.account_id, notify=True)

            task.remove()

    def cmd_stop(self):
        return self.send_cmd('stop')

    def process_stop(self):
        self.initialized = False
        self.stop_required = True
        self.stop_queue.put({'code': 'stopped', 'worker': 'items_manager'}, serializer='json', compression=None)
        self.logger.info('ITEMS MANAGER STOPPED')
