
import smart_imports

smart_imports.all()


class APIShowTests(utils_testcase.TestCase):

    def setUp(self):
        super(APIShowTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_success(self):
        self.check_ajax_ok(self.request_ajax_json(logic.api_show_url(self.place_2.persons[0])))


class TestShowRequests(utils_testcase.TestCase):

    def setUp(self):
        super(TestShowRequests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.person = self.place_1.persons[0]

        self.account = self.accounts_factory.create_account()

    def test_wrong_person_id(self):
        self.check_html_ok(self.request_html(dext_urls.url('game:persons:show', 'wrong_id')), texts=['pgf-error-person.wrong_format'])

    def test_person_does_not_exist(self):
        self.check_html_ok(self.request_html(dext_urls.url('game:persons:show', 666)), texts=['pgf-error-person.wrong_value'])

    def test__has_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-1-caption', 'folclor-1-text', meta_relations.Person.create_from_object(self.person))
        blogs_helpers.create_post_for_meta_object(self.account, 'folclor-2-caption', 'folclor-2-text', meta_relations.Person.create_from_object(self.person))

        self.check_html_ok(self.request_html(dext_urls.url('game:persons:show', self.person.id)), texts=[('pgf-no-folclor', 0),
                                                                                                         'folclor-1-caption',
                                                                                                         'folclor-2-caption'])

    def test__no_folclor(self):
        self.check_html_ok(self.request_html(dext_urls.url('game:persons:show', self.person.id)), texts=['pgf-no-folclor'])
