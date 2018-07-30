
import smart_imports

smart_imports.all()


def wraps_patch(external_func):

    def decorator(internal_func):
        return internal_func

    return decorator


class RefuseThirdPartyTests(utils_testcase.TestCase):

    def setUp(self):
        super(RefuseThirdPartyTests, self).setUp()
        self.target_func = mock.Mock()

    @mock.patch('functools.wraps', wraps_patch)
    def test_has_token(self):
        resource = mock.Mock(request=self.make_request_html('/', session={conf.settings.ACCESS_TOKEN_SESSION_KEY: 'bla-bla-uuid'}))

        decorators.refuse_third_party(self.target_func)(resource)

        self.assertEqual(self.target_func.call_count, 0)
        self.assertEqual(resource.auto_error.call_count, 1)

    @mock.patch('functools.wraps', wraps_patch)
    def test_no_token(self):
        resource = mock.Mock(request=self.make_request_html('/', session={}))

        decorators.refuse_third_party(self.target_func)(resource)

        self.assertEqual(self.target_func.call_count, 1)
        self.assertEqual(resource.auto_error.call_count, 0)
