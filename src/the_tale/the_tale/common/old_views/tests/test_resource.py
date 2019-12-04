
import smart_imports

smart_imports.all()


class ResourceTests(utils_testcase.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_handlers(self):
        self.assertEqual(helpers.EmptyResourceTestClass.get_handlers(), [])
        self.assertEqual([(info.name, info.path) for info in helpers.ResourceTestClass.get_handlers()],
                         [('', ('',)), # index
                          ('show', ('#object_id', 'show')),
                          ])

    def test_string(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.string('some string'), texts=['some string'], content_type='text/html', encoding='utf-8')

    def test_atom(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.atom('some string'), texts=['some string'], content_type='application/atom+xml', encoding='utf-8')

    def test_rss(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.rss('some string'), texts=['some string'], content_type='application/rss+xml', encoding='utf-8')

    def test_rdf(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.rdf('some string'), texts=['some string'], content_type='application/rdf+xml', encoding='utf-8')

    def test_json(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.json(data={'id': 'some text'}), texts=['data', 'some text', 'id'], content_type='application/json', encoding='utf-8')

    def test_json_ok(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_ajax_ok(resource.json_ok({'id': 'some text'}), {'id': 'some text'}, content_type='application/json', encoding='utf-8')

    def test_json_processing(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_ajax_processing(resource.json_processing('some/url'), 'some/url', content_type='application/json', encoding='utf-8')

    def test_json_error(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_ajax_error(resource.json_error('some.error.code', 'error text'), 'some.error.code', content_type='application/json', encoding='utf-8')

    def test_json_errors(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_ajax_error(resource.json_error('some.error.code', ['error text']), 'some.error.code', content_type='application/json', encoding='utf-8')

    def test_css(self):
        resource = helpers.ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.css('some text'), texts=['some text'], content_type='text/css', encoding='utf-8')

    def test_redirect(self):
        resource = helpers.ResourceTestClass(self.fake_request())

        url = '/some/url'

        self.assertEqual(resource.redirect(url).__dict__,
                         django_http.HttpResponseRedirect(url).__dict__)

        self.assertEqual(resource.redirect(url, permanent=True).__dict__,
                         django_http.HttpResponsePermanentRedirect(url).__dict__)

        self.assertEqual(resource.redirect('xxx://xxx.yy').__dict__,
                         django_http.HttpResponseRedirect('/').__dict__)

    def test_auto_error(self):
        resource = helpers.ResourceTestClass(self.fake_request(method='post'))
        self.check_ajax_error(resource.auto_error('some.error.code', 'error text'), 'some.error.code', content_type='application/json', encoding='utf-8')

        resource = helpers.ResourceTestClass(self.fake_request(method='get'))
        self.check_ajax_error(resource.auto_error('some.error.code', 'error text', response_type='json'), 'some.error.code', content_type='application/json', encoding='utf-8')

        resource = helpers.ResourceTestClass(self.fake_request(method='get', ajax=True))
        self.check_ajax_error(resource.auto_error('some.error.code', 'error text', response_type='json'), 'some.error.code', content_type='application/json', encoding='utf-8')
