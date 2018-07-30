
import smart_imports

smart_imports.all()


class RefrigeratorException(Exception):
    pass


class Worker(utils_workers.BaseWorker):
    NO_CMD_TIMEOUT = 0.1
    REFRESH_SETTINGS = False

    def clean_queues(self):
        super(Worker, self).clean_queues()
        self.stop_queue.queue.purge()

    def initialize(self):
        self.initialized = True
        self.next_task_process_time = datetime.datetime.now()
        self.tasks = {}
        PostponedTaskPrototype.reset_all()
        self.logger.info('REFRIGERATOR INITIALIZED')

    def process_no_cmd(self):
        if self.next_task_process_time < datetime.datetime.now():
            self.check_tasks()
            self.next_task_process_time = datetime.datetime.now() + datetime.timedelta(seconds=conf.settings.TASK_WAIT_DELAY)

    def check_tasks(self):

        for task in list(self.tasks.values()):
            task.process(self.logger)
            task.do_postsave_actions()

            if task.internal_result != POSTPONED_TASK_LOGIC_RESULT.WAIT:
                del self.tasks[task.id]

    def cmd_wait_task(self, task_id):
        return self.send_cmd('wait_task', {'task_id': task_id})

    def process_wait_task(self, task_id):
        task = PostponedTaskPrototype.get_by_id(task_id)
        if task:
            self.tasks[task_id] = task
