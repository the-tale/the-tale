
import smart_imports

smart_imports.all()


class RegistrationException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    GET_CMD_TIMEOUT = 10

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        PostponedTaskPrototype.reset_all()
        self.logger.info('REGISTRATION INITIALIZED')

    def cmd_task(self, task_id):
        return self.send_cmd('task', {'task_id': task_id})

    def process_task(self, task_id):
        task = PostponedTaskPrototype.get_by_id(task_id)
        task.process(self.logger)
        task.save()
