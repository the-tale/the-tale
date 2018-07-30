
import smart_imports

smart_imports.all()


class PrototypeTests(utils_testcase.TestCase):

    def setUp(self):
        super(PrototypeTests, self).setUp()
        self.task = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask())

    def test_internals_tasks_collection(self):
        self.assertEqual(prototypes._INTERNAL_LOGICS['fake-task'], postponed_tasks.FakePostponedInternalTask)

    def test_internals_tasks_collection_duplicate_registration(self):
        class Fake2PostponedInternalTask(PostponedLogic):
            TYPE = 'fake-task'

        self.assertRaises(exceptions.PostponedTaskException, prototypes._register_postponed_tasks, prototypes._INTERNAL_LOGICS, [Fake2PostponedInternalTask])

    def test_internals_tasks_collection_no_type(self):
        class Fake3PostponedInternalTask(PostponedLogic):
            pass

        prototypes._register_postponed_tasks(prototypes._INTERNAL_LOGICS, [Fake3PostponedInternalTask])

        self.assertTrue(None not in prototypes._INTERNAL_LOGICS)

    def test_create(self):
        self.assertTrue(self.task.state.is_waiting)
        self.assertTrue(self.task.internal_state, postponed_tasks.FakePostponedInternalTask.INITIAL_STATE)
        self.assertEqual(self.task.internal_logic.TYPE, postponed_tasks.FakePostponedInternalTask.TYPE)

    def test_remove_old_tasks(self):
        task = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask())
        task.state = POSTPONED_TASK_STATE.PROCESSED
        task.save()

        removed_task = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask())
        removed_task.state = POSTPONED_TASK_STATE.ERROR
        removed_task.save()

        PostponedTaskPrototype.remove_old_tasks()

        self.assertEqual(PostponedTask.objects.all().count(), 3)

        with mock.patch('the_tale.common.postponed_tasks.conf.settings.TASK_LIVE_TIME', -1):
            PostponedTaskPrototype.remove_old_tasks()

        self.assertEqual(PostponedTask.objects.all().count(), 1)

    def test_reset_all(self):
        task = PostponedTaskPrototype.create(postponed_tasks.FakePostponedInternalTask())
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

            with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                                   mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
                self.task.process(utils_fake.FakeLogger())

            self.assertEqual(call_counter.call_count, 0)
            self.assertEqual(self.task.state, state)

    def test_process_timeout(self):

        self.task._model.live_time = -1

        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
            self.task.process(utils_fake.FakeLogger())

        self.assertEqual(call_counter.call_count, 0)
        self.assertTrue(self.task.state.is_timeout)

    def test_process_success(self):
        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.SUCCESS)) as call_counter:
            self.task.process(utils_fake.FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_processed)

    def test_process_internal_error(self):

        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.ERROR)) as call_counter:
            self.task.process(utils_fake.FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_error)

    def test_process_internal_continue(self):

        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.CONTINUE)) as call_counter:
            self.task.process(utils_fake.FakeLogger())

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_waiting)

    def test_process_internal_wait(self):

        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process',
                               mock.Mock(return_value=POSTPONED_TASK_LOGIC_RESULT.WAIT)) as call_counter:
            self.task.process(utils_fake.FakeLogger())

        self.assertEqual(len(self.task._postsave_actions), 1)

        with mock.patch('the_tale.common.postponed_tasks.workers.refrigerator.Worker.cmd_wait_task') as cmd_wait_task:
            self.task.do_postsave_actions()

        self.assertEqual(cmd_wait_task.call_count, 1)

        self.assertEqual(call_counter.call_count, 1)
        self.assertTrue(self.task.state.is_waiting)

    def test_process_exception(self):

        def process_with_exception(self, *argv, **kwargs):
            raise Exception()

        with mock.patch.object(postponed_tasks.FakePostponedInternalTask, 'process', process_with_exception):
            self.task.process(utils_fake.FakeLogger())

        self.assertTrue(self.task.state.is_exception)
        self.assertTrue(self.task.comment)
