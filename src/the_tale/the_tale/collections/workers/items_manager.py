
import smart_imports

smart_imports.all()


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.logger.info('ITEMS_MANAGER INITIALIZED')

    def add_item(self, item, account_id, notify):
        account_items = prototypes.AccountItemsPrototype.get_by_account_id(account_id)
        account_items.add_item(item, notify=notify)
        account_items.save()

    def process_no_cmd(self):
        self.add_items()

    def add_items(self):
        for task in prototypes.GiveItemTaskPrototype.from_query(prototypes.GiveItemTaskPrototype._db_all()):
            item = storage.items[task.item_id]

            self.logger.info('process task %d for item %d' % (task.id, item.id))

            self.add_item(item, task.account_id, notify=True)

            task.remove()
