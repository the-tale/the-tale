
import smart_imports

smart_imports.all()


class BaseRequestsTests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()


class IndexRequestsTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(dext_urls.url('linguistics:')), texts=[])

    def test_all_groups(self):
        texts = [group.text for group in lexicon_groups_relations.LEXICON_GROUP.records]
        self.check_html_ok(self.request_html(dext_urls.url('linguistics:')), texts=texts)

    def test_all_keys(self):
        texts = [key.text for key in lexicon_keys.LEXICON_KEY.records]
        self.check_html_ok(self.request_html(dext_urls.url('linguistics:')), texts=texts)


class HowAddPhraseTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(dext_urls.url('linguistics:how-add-phrase')), texts=[])
