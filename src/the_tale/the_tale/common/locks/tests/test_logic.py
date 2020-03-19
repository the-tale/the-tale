import smart_imports

smart_imports.all()


class CreateLockRequestTests(utils_testcase.TestCase):

    def test_create(self):
        with self.check_delta(models.LockRequest.objects.count, 1):
            request = logic.create_lock_request('xxx', comment='yyy')

        self.assertEqual(request.name, 'xxx')
        self.assertTrue(request.state.is_REQUESTED)
        self.assertEqual(request.data, {'pid': os.getpid(),
                                        'command': sys.argv,
                                        'comment': 'yyy'})

        loaded_request = models.LockRequest.objects.first()

        self.assertEqual(loaded_request.id, request.id)
        self.assertEqual(loaded_request.name, 'xxx')
        self.assertTrue(loaded_request.state.is_REQUESTED)
        self.assertEqual(loaded_request.data, {'pid': os.getpid(),
                                               'command': sys.argv,
                                               'comment': 'yyy'})

    def test_multiple_create(self):
        with self.check_delta(models.LockRequest.objects.count, 4):
            requests = [logic.create_lock_request('xxx'),
                        logic.create_lock_request('yyy'),
                        logic.create_lock_request('xxx'),
                        logic.create_lock_request('zzz')]

        self.assertEqual([request.name for request in requests],
                         ['xxx', 'yyy', 'xxx', 'zzz'])

        self.assertTrue(all(request.state.is_REQUESTED for request in requests))


class TryToLockTests(utils_testcase.TestCase):

    def test_simple(self):
        request = logic.create_lock_request('xxx')

        self.assertTrue(logic.try_to_lock(request))

        loaded_request = models.LockRequest.objects.get(id=request.id)

        self.assertTrue(loaded_request.state.is_ACTIVE)

    def test_different_locks(self):
        requests = [logic.create_lock_request('yyy'),
                    logic.create_lock_request('xxx')]

        self.assertTrue(logic.try_to_lock(requests[1]))

        loaded_request = models.LockRequest.objects.get(id=requests[0].id)
        self.assertTrue(loaded_request.state.is_REQUESTED)

        loaded_request = models.LockRequest.objects.get(id=requests[1].id)
        self.assertTrue(loaded_request.state.is_ACTIVE)

    def test_no_locks(self):
        request = logic.create_lock_request('xxx')

        models.LockRequest.objects.all().delete()

        self.assertFalse(logic.try_to_lock(request))

    def test_no_lock_id(self):
        requests = [logic.create_lock_request('yyy'),
                    logic.create_lock_request('xxx')]

        models.LockRequest.objects.filter(id=requests[1].id).delete()

        self.assertFalse(logic.try_to_lock(requests[1]))

        loaded_request = models.LockRequest.objects.get(id=requests[0].id)
        self.assertTrue(loaded_request.state.is_REQUESTED)

    def test_not_first_lock_id(self):
        requests = [logic.create_lock_request('xxx'),
                    logic.create_lock_request('xxx')]

        self.assertEqual(logic.try_to_lock(requests[1]), None)

        self.assertTrue(logic.try_to_lock(requests[0]))

        self.assertEqual(logic.try_to_lock(requests[1]), None)

        logic.delete_lock_request(requests[0])

        self.assertTrue(logic.try_to_lock(requests[1]))

        loaded_request = models.LockRequest.objects.get(id=requests[1].id)
        self.assertTrue(loaded_request.state.is_ACTIVE)


class DeleteLockRequestTests(utils_testcase.TestCase):

    def test_simple(self):
        request = logic.create_lock_request('xxx')

        with self.check_delta(models.LockRequest.objects.count, -1):
            logic.delete_lock_request(request)


class LockTests(utils_testcase.TestCase):

    def test_simple(self):

        with logic.lock('xxx'):
            request = models.LockRequest.objects.first()

            self.assertEqual(request.name, 'xxx')
            self.assertTrue(request.state.is_ACTIVE)

        self.assertFalse(models.LockRequest.objects.exists())

    def test_hierarchical(self):

        with logic.lock('xxx'):

            with logic.lock('yyy'):
                requests = list(models.LockRequest.objects.all().order_by('id'))

                self.assertEqual(requests[0].name, 'xxx')
                self.assertTrue(requests[0].state.is_ACTIVE)

                self.assertEqual(requests[1].name, 'yyy')
                self.assertTrue(requests[1].state.is_ACTIVE)

            requests = list(models.LockRequest.objects.all().order_by('id'))

            self.assertEqual(len(requests), 1)

            self.assertEqual(requests[0].name, 'xxx')
            self.assertTrue(requests[0].state.is_ACTIVE)

        self.assertFalse(models.LockRequest.objects.exists())
