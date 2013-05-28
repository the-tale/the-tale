# coding: utf-8

from django.test import client

from dext.utils.urls import url

from common.utils.testcase import TestCase

from common.postponed_tasks.prototypes import PostponedTaskPrototype, autodiscover
from common.postponed_tasks.models import POSTPONED_TASK_STATE
from common.postponed_tasks.postponed_tasks import FakePostponedInternalTask

class RequestsTests(TestCase):

    def setUp(self):
        super(RequestsTests, self).setUp()
        autodiscover()
        self.task = PostponedTaskPrototype.create(FakePostponedInternalTask())

        self.client = client.Client()

    def request_status(self, state):
        self.task.state = state
        self.task.save()
        return self.client.get(url('postponed-tasks:status', self.task.id))

    def test_status_waiting(self):
        self.check_ajax_processing(self.request_status(POSTPONED_TASK_STATE.WAITING), url('postponed-tasks:status', self.task.id))

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

    def test_status__wrong_task_id(self):
        self.check_ajax_error(self.request_ajax_json(url('postponed-tasks:status', 'wrong_task')),
                              'postponed_task.task.wrong_format')

    def test_status__no_task(self):
        self.check_ajax_error(self.request_ajax_json(url('postponed-tasks:status', 666)),
                              'postponed_task.task.not_found')

    def test_wait_success(self):
        self.check_html_ok(self.client.get(url('postponed-tasks:wait', self.task.id)))

    def test_wait_wrong_task(self):
        self.check_html_ok(self.request_ajax_html(url('postponed-tasks:wait', 'wrong_task')), texts=['postponed_task.task.wrong_format'])

    def test_wait_task_not_found(self):
        self.check_html_ok(self.request_ajax_html(url('postponed-tasks:wait', 666)), texts=['postponed_task.task.not_found'], status_code=404)
