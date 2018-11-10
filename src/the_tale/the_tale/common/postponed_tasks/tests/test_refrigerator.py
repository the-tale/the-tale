
import smart_imports

smart_imports.all()


class RefrigeratorTests(utils_testcase.TestCase):

    def setUp(self):
        super(RefrigeratorTests, self).setUp()

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.worker = amqp_environment.environment.workers.refrigerator
        self.worker.initialize()

        self.task_1 = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask(result_state=POSTPONED_TASK_LOGIC_RESULT.WAIT))
        self.task_2 = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask())

    def test_initialize(self):
        self.assertEqual(self.worker.tasks, {})
        self.assertTrue(self.worker.next_task_process_time < datetime.datetime.now())
        self.assertTrue(self.worker.initialized)

    def test_process_wait_task(self):
        self.worker.process_wait_task(self.task_2.id)
        self.assertEqual(set(self.worker.tasks.keys()), set([self.task_2.id]))
        self.worker.process_wait_task(self.task_1.id)
        self.assertEqual(set(self.worker.tasks.keys()), set([self.task_2.id, self.task_1.id]))

    def test_check_tasks(self):
        self.worker.process_wait_task(self.task_2.id)
        self.worker.process_wait_task(self.task_1.id)
        self.worker.process_wait_task(PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask(result_state=POSTPONED_TASK_LOGIC_RESULT.CONTINUE)).id)

        self.worker.check_tasks()

        self.assertEqual(set(self.worker.tasks.keys()), set([self.task_1.id]))
