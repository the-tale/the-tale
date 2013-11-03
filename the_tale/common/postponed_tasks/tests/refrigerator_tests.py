# coding: utf-8
import datetime

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype, autodiscover, POSTPONED_TASK_LOGIC_RESULT
from the_tale.common.postponed_tasks.postponed_tasks import FakePostponedInternalTask
from the_tale.common.postponed_tasks.workers.environment import workers_environment as postponed_tasks_workers_environment


class RefrigeratorTests(testcase.TestCase):

    def setUp(self):
        super(RefrigeratorTests, self).setUp()
        autodiscover()

        postponed_tasks_workers_environment.deinitialize()
        postponed_tasks_workers_environment.initialize()

        self.worker = postponed_tasks_workers_environment.refrigerator
        self.worker.initialize()

        self.task_1 = PostponedTaskPrototype.create(FakePostponedInternalTask(result_state=POSTPONED_TASK_LOGIC_RESULT.WAIT))
        self.task_2 = PostponedTaskPrototype.create(FakePostponedInternalTask())

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
        self.worker.process_wait_task(PostponedTaskPrototype.create(FakePostponedInternalTask(result_state=POSTPONED_TASK_LOGIC_RESULT.CONTINUE)).id)

        self.worker.check_tasks()

        self.assertEqual(set(self.worker.tasks.keys()), set([self.task_1.id]))
