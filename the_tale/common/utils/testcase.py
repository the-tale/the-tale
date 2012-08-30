# coding: utf-8

from dext.utils import s11n

from django.test import TestCase as DjangoTestCase

class TestCase(DjangoTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def check_html_ok(self, response, texts=[], excluded_texts=[]):
        self.assertEqual(response.status_code, 200)
        for text in texts:
            if isinstance(text, tuple):
                substr, number = text
                self.assertEqual(response.content.count(substr), number)
            else:
                self.assertTrue(text in response.content)

    def check_ajax_ok(self, response, data=None):
        self.assertEqual(response.status_code, 200)
        content = s11n.from_json(response.content)
        self.assertEqual(content['status'], 'ok')

        if data is not None:
            self.assertEqual(content['data'], data)

    def check_ajax_error(self, response, code):
        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], code)

    def check_ajax_processing(self, response, status_url=None):
        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content)
        self.assertEqual(data['status'], 'processing')
        if status_url:
            self.assertEqual(data['status_url'], status_url)
