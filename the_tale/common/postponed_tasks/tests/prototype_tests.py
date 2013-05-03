# coding: utf-8

import mock

from common.utils import testcase
from common.utils.fake import FakeLogger

from common.postponed_tasks.exceptions import PostponedTaskException
from common.postponed_tasks.prototypes import PostponedTaskPrototype, PostponedLogic, _register_postponed_tasks, autodiscover, POSTPONED_TASK_LOGIC_RESULT
from common.postponed_tasks.models import PostponedTask, POSTPONED_TASK_STATE
from common.postponed_tasks.postponed_tasks import FakePostponedInternalTask


class PrototypeTests(testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        autodiscover()
        self.task = PostponedTaskPrototype.create(FakePostponedInternalTask())

    def test_internals_tasks_collection(self):
        from common.postponed_tasks.prototypes import _INTERNAL_LOGICS
        self.assertEqual(_INTERNAL_LOGICS['fake-task'], FakePostponedInternalTask)

    def test_internals_tasks_collection_duplicate_registration(self):
        from common.postponed_tasks.prototypes import _INTERNAL_LOGICS

        class Fake2PostponedInternalTask(PostponedLogic):
            TYPE = 'fake-task'

        self.assertRaises(PostponedTaskException, _register_postponed_tasks, _INTERNAL_LOGICS, [Fake2PostponedInternalTask])

    def test_internals_tasks_collection_no_type(self):
        from common.postponed_tasks.prototypes import _INTERNAL_LOGICS

        class Fake3PostponedInternalTask(PostponedLogic):
            pass

        self.assertRaises(PostponedTaskException, _register_postponed_tasks, _INTERNAL_LOGICS, [Fake3PostponedInternalTask])


    def test_create(self):
        self.assertTrue(self.task.state.is_waiting)
        self.assertTrue(self.task.internal_state, FakePostponedInternalTask.INITIAL_STATE)
        self.assertEqual(self.task.internal_logic.TYPE, FakePostponedInternalTask.TYPE)
        self.assertTrue(PostponedTaskPrototype.check_if_used(FakePostponedInternalTask.TYPE, 777))

    def test_remove_old_tasks(self):
        task = PostponedTaskPrototype.create(FakePostponedInternalTask())
        task.state = POSTPONED_TASK_STATE.PROCESSED
        task.save()

        removed_task = PostponedTaskPrototype.create(FakePostponedInternalTask())
        removed_task.state = POSTPONED_TASK_STATE.ERROR
        removed_task.save()

        PostponedTaskPrototype.remove_old_tasks()

        self.assertEqual(PostponedTask.objects.all().count(), 3)

        with mock.patch('common.postponed_tasks.conf.postponed_tasks_settings.TASK_LIVE_TIME', -1):
            PostponedTaskPrototype.remove_old_tasks()

        self.assertEqual(PostponedTask.objects.all().count(), 1)



    def test_reset_all(self):
        task = PostponedTaskPrototype.create(FakePostponedInternalTask())
        task.state = POSTPONED_TASK_STATE.PROCESSED
        task.save()

        self.assertEqual(PostponedTask.objects.all().count(), 2)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).count(), 1)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.PROCESSED).count(), 1)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.RESETED).count(), 0)

        PostponedTaskPrototype.reset_all()

        self.assertEqual(PostponedTask.objects.all().count(), 2)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.WAITING).count(), 0)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.PROCESSED).count(), 1)
        self.assertEqual(PostponedTask.objects.filter(state=POSTPONED_TASK_STATE.RESETED).count(), 1)


    def test_process_not_waiting_state(self):

        for state in POSTPONED_TASK_STATE._ALL:

            if state == POSTPONED_TASK_STATE.WAITING:
                continue

            self.task.state = state

            with mock.patch.object(FakePostponedInternalTask, 'process',
                                   mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
                self.task.process(FakeLogger())

            self.assertEqual(call_counter.call_count, 0)
            self.assertEqual(self.task.state, state)

    def test_process_timeout(self):

        self.task._model.live_time = -1

        with mock.patch.object(FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
            self.task.process(FakeLogger())

        self.assertEqual(call_counter.call_count, 0)
        self.assertTrue(self.task.state.is_timeout)


    def test_process_success(self):
        with mock.patch.object(FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
            self.task.process(FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_processed)


    def test_process_internal_error(self):

        with mock.patch.object(FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.ERROR)) as call_counter:
            self.task.process(FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_error)

    def test_process_internal_continue(self):

        with mock.patch.object(FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.CONTINUE)) as call_counter:
            self.task.process(FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_waiting)


    def test_process_internal_wait(self):

        with mock.patch.object(FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.WAIT)) as call_counter:
            self.task.process(FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_waiting)


    def test_process_exception(self):

        def process_with_exception(self, *argv, **kwargs):
            raise Exception()

        with mock.patch.object(FakePostponedInternalTask, 'process', process_with_exception):
            self.task.process(FakeLogger())

        self.assertTrue(self.task.state.is_exception)
        self.assertTrue(self.task.comment)
