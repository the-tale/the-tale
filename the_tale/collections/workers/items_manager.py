# coding: utf-8

import Queue

from django.utils.log import getLogger

from dext.settings import settings

from the_tale.common.amqp_queues import connection, BaseWorker

from the_tale.collections.prototypes import GiveItemTaskPrototype, AccountItemsPrototype
from the_tale.collections.storage import items_storage


class Worker(BaseWorker):

    logger = getLogger('the-tale.workers.collections_items_manager')
    name = 'items manager'
    command_name = 'collections_items_manager'

    def __init__(self, messages_queue, stop_queue):
        super(Worker, self).__init__(command_queue=messages_queue)
        self.stop_queue = connection.SimpleQueue(stop_queue)
        self.initialized = True

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.logger.info('ITEMS_MANAGER INITIALIZED')

    def run(self):

        while not self.exception_raised and not self.stop_required:
            try:
                cmd = self.command_queue.get(block=True, timeout=10)
                # cmd.ack()

                settings.refresh()
                self.process_cmd(cmd.payload)
            except Queue.Empty:
                self.logger.info('try to update commands')
                settings.refresh()
                self.add_items()

    def add_item(self, item, account_id, notify):
        account_items = AccountItemsPrototype.get_by_account_id(account_id)
        account_items.add_item(item, notify=notify)
        account_items.save()

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
