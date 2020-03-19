
import smart_imports

smart_imports.all()


class UrlsTests(utils_testcase.TestCase):

    def setUp(self):
        super(UrlsTests, self).setUp()

    def test_modify_url__no_query(self):
        self.assertEqual(utils_urls.modify_url('www.example.com', query=()), 'www.example.com')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/', query=()), 'http://www.example.com/')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/?x=y&x=z', query=()), 'http://www.example.com/?x=y&x=z')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/?x=y&x=z#abc=p&p=abc', query=()), 'http://www.example.com/?x=y&x=z#abc=p&p=abc')

    def test_modify_url(self):
        query = ( ('x', 123), ('test', 'bla-bla'), ('test', 'ма-ма') )
        self.assertEqual(utils_urls.modify_url('www.example.com', query=query), 'www.example.com?x=123&test=bla-bla&test=%D0%BC%D0%B0-%D0%BC%D0%B0')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/', query=query), 'http://www.example.com/?x=123&test=bla-bla&test=%D0%BC%D0%B0-%D0%BC%D0%B0')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/?x=y&x=z', query=query), 'http://www.example.com/?x=y&x=z&x=123&test=bla-bla&test=%D0%BC%D0%B0-%D0%BC%D0%B0')
        self.assertEqual(utils_urls.modify_url('http://www.example.com/?x=y&x=z#abc=p&p=abc', query=query),
                         'http://www.example.com/?x=y&x=z&x=123&test=bla-bla&test=%D0%BC%D0%B0-%D0%BC%D0%B0#abc=p&p=abc')
