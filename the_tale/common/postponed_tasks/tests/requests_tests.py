# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase

from common.postponed_tasks.prototypes import PostponedTaskPrototype
from common.postponed_tasks.models import POSTPONED_TASK_STATE
from common.postponed_tasks.postponed_tasks import FakePostponedInternalTask


class RequestsTests(TestCase):

    def setUp(self):
        self.task = PostponedTaskPrototype.create(FakePostponedInternalTask())

        self.client = client.Client()

    def request_status(self, state):
        self.task.state = state
        self.task.save()
        return self.client.get(reverse('postponed-tasks:status', args=[self.task.id]))

    def test_status_waiting(self):
        self.check_ajax_processing(self.request_status(POSTPONED_TASK_STATE.WAITING), reverse('postponed-tasks:status', args=[self.task.id]))

    def test_status_processed(self):
        self.check_ajax_ok(self.request_status(POSTPONED_TASK_STATE.PROCESSED), data={'test_value': 666})

    def test_status_reseted(self):
        self.check_ajax_error(self.request_status(POSTPONED_TASK_STATE.RESETED), 'postponed_task.task_reseted')

    def test_status_timeout(self):
        self.check_ajax_error(self.request_status(POSTPONED_TASK_STATE.TIMEOUT), 'postponed_task.timeout')

    def test_status_error(self):
        self.check_ajax_error(self.request_status(POSTPONED_TASK_STATE.ERROR), 'postponed_task.error')

    def test_status_exception(self):
        self.check_ajax_error(self.request_status(POSTPONED_TASK_STATE.EXCEPTION), 'postponed_task.exception')
