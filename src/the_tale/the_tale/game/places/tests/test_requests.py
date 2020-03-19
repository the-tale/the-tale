
import smart_imports

smart_imports.all()


class APIListRequestTests(utils_testcase.TestCase):

    def setUp(self):
        super(APIListRequestTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_success(self):
        data = self.check_ajax_ok(self.request_ajax_json(logic.api_list_url()))

        self.assertEqual(data,
                         {'places': {
                             str(self.place_1.id): {'specialization': modifiers.CITY_MODIFIERS.NONE.value,
                                                    'frontier': False,
                                                    'name': '1x1-\u043d\u0441,\u0435\u0434,\u0438\u043c',
                                                    'position': {'y': 1, 'x': 1},
                                                    'id': self.place_1.id,
                                                    'size': 1},
                             str(self.place_3.id): {'specialization': modifiers.CITY_MODIFIERS.NONE.value,
                                                    'frontier': False,
                                                    'name': '1x10-\u043d\u0441,\u0435\u0434,\u0438\u043c',
                                                    'position': {'y': 3, 'x': 1},
                                                    'id': self.place_3.id,
                                                    'size': 3},
                             str(self.place_2.id): {'specialization': modifiers.CITY_MODIFIERS.NONE.value,
                                                    'frontier': False,
                                                    'name': '10x10-\u043d\u0441,\u0435\u0434,\u0438\u043c',
                                                    'position': {'y': 3, 'x': 3},
                                                    'id': self.place_2.id,
                                                    'size': 3}}})


class APIShowTests(utils_testcase.TestCase):

    def setUp(self):
        super(APIShowTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_success(self):
        self.check_ajax_ok(self.request_ajax_json(logic.api_show_url(self.place_2)))


class TestShowRequests(utils_testcase.TestCase):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()
        self.account = self.accounts_factory.create_account()

    def test_place_new_place_message(self):
        self.assertTrue(self.place_1.is_new)
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=['pgf-new-place-message'])

    @mock.patch('the_tale.game.balance.constants.PLACE_NEW_PLACE_LIVETIME', 0)
    def test_place_new_place_message__not_new(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=[('pgf-new-place-message', 0)])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', True)
    def test_place_frontier_message(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=['pgf-frontier-message'])

    @mock.patch('the_tale.game.places.objects.Place.is_frontier', False)
    def test_place_frontier_message__not_new(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=[('pgf-frontier-message', 0)])

    def test_wrong_place_id(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', 'wrong_id')), texts=['pgf-error-place.wrong_format'])

    def test_place_does_not_exist(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', 666)), texts=['pgf-error-place.wrong_value'])

    def test__has_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-1-caption', 'folclor-1-text', meta_relations.Place.create_from_object(self.place_1))
        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-2-caption', 'folclor-2-text', meta_relations.Place.create_from_object(self.place_1))

        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=[('pgf-no-folclor', 0),
                                                                                                         'folclor-1-caption',
                                                                                                         'folclor-2-caption'])

    def test__no_folclor(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:places:show', self.place_1.id)), texts=['pgf-no-folclor'])
