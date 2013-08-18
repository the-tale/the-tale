# coding: utf-8

from django.test import client

from dext.utils.urls import url

from common.utils.testcase import TestCase

from game.logic import create_test_map

from forum.tests.helpers import ForumFixture

class TestRequests(TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        create_test_map()
        self.client = client.Client()

    def test_index(self):
        response = self.client.get(url('portal:'))
        self.assertEqual(response.status_code, 200)

    def test_preview(self):
        text = 'simple test text'
        self.check_html_ok(self.client.post(url('portal:preview'), {'text': text}), texts=[text])

    def test_hot_themes__show_all(self):
        forum = ForumFixture()
        self.check_html_ok(self.request_html(url('portal:')), texts=[forum.thread_1.caption, forum.thread_2.caption, forum.thread_3.caption])

    def test_hot_themes__hide_restricted_themes(self):
        forum = ForumFixture()
        forum.subcat_3._model.restricted = True
        forum.subcat_3.save()
        self.check_html_ok(self.request_html(url('portal:')), texts=[forum.thread_1.caption, forum.thread_2.caption, (forum.thread_3.caption, 0)])
