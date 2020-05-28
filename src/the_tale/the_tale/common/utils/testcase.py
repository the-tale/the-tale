
import smart_imports

smart_imports.all()


def setUp(self):

    accounts_tt_services.players_timers.cmd_debug_clear_service()

    global_settings.refresh(force=True)

    heroes_storage.position_descriptions.clear()

    places_storage.places.clear()
    places_storage.buildings.clear()
    persons_storage.persons.clear()
    persons_storage.social_connections.clear()
    roads_storage.roads.clear()
    mobs_storage.mobs.clear()
    companions_storage.companions.clear()
    artifacts_storage.artifacts.clear()
    map_storage.map_info.clear()
    places_storage.resource_exchanges.clear()
    emissaries_storage.emissaries.clear()
    emissaries_storage.events.clear()
    collections_storage.collections.clear()
    collections_storage.kits.clear()
    collections_storage.items.clear()
    achievements_storage.achievements.clear()
    linguistics_storage.dictionary.clear()
    linguistics_storage.lexicon.clear()
    linguistics_storage.restrictions.clear()
    places_storage.effects.clear()
    clans_storage.infos.clear()

    game_prototypes.GameState.start()


class TestAccountsFactory(object):

    def __init__(self):
        self._next_account_uid = 0

    def get_next_uid(self):
        self._next_account_uid += 1
        return self._next_account_uid

    def create_account(self,
                       is_fast=False,
                       nick=None,
                       email=None,
                       password='111111',
                       is_bot=False,
                       is_superuser=False,
                       referral_of_id=None):

        if is_fast:
            nick = nick or 'fast-user-{}'.format(self.get_next_uid())
            result, account_id, bundle_id = accounts_logic.register_user(nick,
                                                                         is_bot=is_bot,
                                                                         referral_of_id=referral_of_id)
        else:
            nick = nick or 'test-user-%d' % self.get_next_uid()
            email = email or '{}@test.com'.format(nick)
            result, account_id, bundle_id = accounts_logic.register_user(nick,
                                                                         email,
                                                                         password,
                                                                         is_bot=is_bot,
                                                                         referral_of_id=referral_of_id)

        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

        if is_superuser:
            account._model.is_superuser = True
            account.save()

        return accounts_prototypes.AccountPrototype.get_by_id(account_id)


def make_request_decorator(method):

    @functools.wraps(method)
    def make_request_wrapper(self, url, meta={}, user=None, session=None):
        request = method(self, url, meta=meta)
        request.user = user if user is not None else django_auth_models.AnonymousUser()
        request.session = session if session is not None else {}
        return request

    return make_request_wrapper


class TestCaseMixin(object):

    def fake_request(self, path='/', user=None, method='GET', ajax=False, **kwargs):
        csrf = kwargs.get('csrf', django_middleware.csrf._get_new_csrf_token())

        request = django_wsgi_handlers.WSGIRequest({'REQUEST_METHOD': method.upper(),
                                                    'PATH_INFO': path,
                                                    'wsgi.input': io.StringIO(),
                                                    'CSRF_COOKIE': csrf,
                                                    'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' if ajax else None})
        request.user = django_auth_models.AnonymousUser() if user is None else user
        return request

    def check_logged_in(self, account=None, client=None):
        client = client or self.client

        self.assertIn('_auth_user_id', client.session)

        if account:
            self.assertEqual(account.id, int(client.session['_auth_user_id']))

    def check_logged_out(self, client=None):
        client = client or self.client
        self.assertNotIn('_auth_user_id', client.session)

    def check_html_ok(self, response, status_code=200, texts=[], content_type='text/html', encoding='utf-8', body=None):
        self.assertEqual(response.status_code, status_code)

        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        content = response.content.decode(encoding)

        if body is not None:
            self.assertEqual(content, body)

        for text in texts:
            if isinstance(text, tuple):
                substr, number = text
                substr = str(substr)
                self.assertEqual((substr, content.count(substr)), (substr, number))
            else:
                substr = str(text)
                self.assertEqual((substr, substr in content), (substr, True))

    def check_xml_ok(self, *argv, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'text/xml'
        return self.check_html_ok(*argv, **kwargs)

    def check_ajax_ok(self, response, data=None, content_type='application/json', encoding='utf-8'):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        content = s11n.from_json(response.content.decode(encoding))

        self.assertEqual(content['status'], 'ok')

        if data is not None:
            self.assertEqual(content['data'], data)

        return content.get('data')

    def check_ajax_error(self, response, code, content_type='application/json', encoding='utf-8', status_code=200):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, status_code)
        data = s11n.from_json(response.content.decode(encoding))
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], code)

    def check_ajax_processing(self, response, status_url=None, content_type='application/json', encoding='utf-8'):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content.decode(encoding))
        self.assertEqual(data['status'], 'processing')
        if status_url:
            self.assertEqual(data['status_url'], status_url)

    def check_js_ok(self, response, status_code=200, texts=[], content_type='application/x-javascript', encoding='utf-8', body=None):
        self.check_html_ok(response, status_code=status_code, texts=texts, content_type=content_type, encoding=encoding)

    def check_redirect(self, requested_url, test_url, status_code=302, target_status_code=200):
        self.check_response_redirect(self.request_html(requested_url), test_url, status_code=status_code, target_status_code=target_status_code)

    def check_response_redirect(self, response, test_url, status_code=302, target_status_code=200):
        self.assertRedirects(response, test_url, status_code=status_code, target_status_code=target_status_code)

    @contextlib.contextmanager
    def check_not_changed(self, callback):
        old_value = callback()
        yield
        self.assertEqual(callback(), old_value)

    @contextlib.contextmanager
    def check_changed(self, callback):
        old_value = callback()
        yield
        self.assertNotEqual(callback(), old_value)

    @contextlib.contextmanager
    def check_delta(self, callback, delta):
        old_value = callback()
        yield
        self.assertEqual(callback() - old_value, delta)

    @contextlib.contextmanager
    def check_almost_delta(self, callback, delta):
        old_value = callback()
        yield
        self.assertAlmostEqual(callback() - old_value, delta)

    @contextlib.contextmanager
    def check_increased(self, callback):
        old_value = callback()
        yield
        self.assertTrue(callback() > old_value)

    @contextlib.contextmanager
    def check_decreased(self, callback):
        old_value = callback()
        yield
        self.assertTrue(callback() < old_value)

    @contextlib.contextmanager
    def check_calls_count(self, name, count):
        with mock.patch(name) as mocked:
            yield
        self.assertEqual(mocked.call_count, count)

    @contextlib.contextmanager
    def check_calls_exists(self, name):
        with mock.patch(name) as mocked:
            yield
        self.assertGreater(mocked.call_count, 0)

    def check_serialization(self, obj):
        obj_data = obj.serialize()
        self.assertEqual(obj_data, obj.deserialize(s11n.from_json(s11n.to_json(obj_data))).serialize())

    def request_html(self, url, client=None):
        client = client or self.client
        return client.get(url, HTTP_ACCEPT='text/html')

    def request_js(self, url):
        return self.client.get(url, HTTP_ACCEPT='application/x-javascript')

    def request_xml(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/xml')

    def request_json(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/json')

    def request_ajax_json(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def request_ajax_html(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/html', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post_xml(self, url):
        return self.client.post(url, HTTP_ACCEPT='text/xml')

    def post_html(self, url):
        return self.client.post(url, HTTP_ACCEPT='text/html')

    def post_ajax_html(self, url, data=None):
        return self.client.post(url, data if data else {}, HTTP_ACCEPT='text/html', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post_ajax_json(self, url, data=None, client=None):
        client = client or self.client
        return client.post(url, data if data else {}, HTTP_ACCEPT='text/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post_ajax_binary(self, url, data=None):
        return self.client.post(url, data if data else '', HTTP_ACCEPT='text/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest', content_type='application/octet-stream')

    @make_request_decorator
    def make_request_html(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/html'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_xml(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/xml'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_ajax_json(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/json',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_ajax_html(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/html',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_post_xml(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/xml'}
        _meta.update(meta)
        return self.request_factory.post(url, **_meta)

    @make_request_decorator
    def make_post_ajax_json(self, url, data=None, meta={}, client=None):
        _meta = {'HTTP_ACCEPT': 'text/json',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)

        client = client or self.client

        return client.post(url, data if data else {}, **_meta)

    def request_login(self, email, password='111111', remember=False, client=None):
        data = {'email': email, 'password': password}
        if remember:
            data['remember'] = 'remember'
        response = self.post_ajax_json(utils_urls.url('accounts:auth:api-login', api_version='1.0', api_client='test-1.0'),
                                       data,
                                       client=client)
        self.check_ajax_ok(response)

    def request_logout(self):
        response = self.post_ajax_json(utils_urls.url('accounts:auth:api-logout', api_version='1.0', api_client='test-1.0'))
        self.check_ajax_ok(response)

    @decorators.lazy_property
    def accounts_factory(self):
        return TestAccountsFactory()

    def check_logined_as(self, account_id):
        self.assertEqual(self.client.session.get('_auth_user_id'), str(account_id))

    def check_not_logined(self):
        self.assertEqual(self.client.session.get('_auth_user_id'), None)


class TestCase(django_test.TestCase, TestCaseMixin):
    def setUp(self):
        self.request_factory = django_test_client.RequestFactory()
        setUp(self)
