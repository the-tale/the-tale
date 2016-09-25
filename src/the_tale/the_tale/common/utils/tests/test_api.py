# coding: utf-8

from dext.common.utils import s11n
from dext.views import handler

from the_tale.common.utils.resources import Resource

from the_tale.common.utils import testcase
from the_tale.common.utils import api


class TestResource(Resource):

    @api.handler(versions=('1.1', '1.0'))
    @handler('path')
    def test_view(self, arg_1, api_version=None):
        return self.ok(data={'arg_1': arg_1})


class ApiTest(testcase.TestCase):

    def setUp(self):
        super(ApiTest, self).setUp()
        self.resource = TestResource(self.fake_request())

    def check_api_error(self, error_code, **kwargs):
        data = s11n.from_json(self.resource.test_view(**kwargs).content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], error_code)

    def test_check_client_version(self):
        self.assertTrue(api.check_client_version('program-v0.1'))

    def test_check_client_version__no(self):
        self.assertFalse(api.check_client_version(None))

    def test_check_client_version__wrong_format(self):
        self.assertFalse(api.check_client_version('program-v-0-1'))

    def test_handler(self):
        self.assertEqual(s11n.from_json(self.resource.test_view(arg_1=6, api_version='1.1', api_client='client-v0.1').content),
                         {'status': 'ok', 'data': {'arg_1': 6} })

    def test_handler__no_api_version(self):
        self.check_api_error('api.no_method_version', arg_1=6, api_client='client-v0.1')

    def test_handler__wrong_api_version(self):
        self.check_api_error('api.wrong_method_version', arg_1=6, api_version='1.2', api_client='client-v0.1')

    def test_handler__depricated_api_version(self):
        self.assertEqual(s11n.from_json(self.resource.test_view(arg_1=6, api_version='1.0', api_client='client-v0.1').content),
                         {'status': 'ok', 'data': {'arg_1': 6}, 'depricated': True })

    def test_handler__no_client_version(self):
        self.check_api_error('api.no_client_identificator', arg_1=6, api_version='1.1')

    def test_handler__wrong_client_version(self):
        self.check_api_error('api.wrong_client_identificator_format', arg_1=6, api_version='1.1', api_client='clientv0.1')
        self.check_api_error('api.wrong_client_identificator_format', arg_1=6, api_version='1.1', api_client='clientv-0-1')
