# coding: utf-8
from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.game.logic import create_test_map

from the_tale.linguistics.lexicon.groups import relations as lexicon_groups_relations
from the_tale.linguistics.lexicon import keys


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()


class IndexRequestsTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(url('linguistics:')), texts=[])

    def test_all_groups(self):
        texts = [group.text for group in lexicon_groups_relations.LEXICON_GROUP.records]
        self.check_html_ok(self.request_html(url('linguistics:')), texts=texts)

    def test_all_keys(self):
        texts = [key.text for key in keys.LEXICON_KEY.records]
        self.check_html_ok(self.request_html(url('linguistics:')), texts=texts)


class HowAddPhraseTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(url('linguistics:how-add-phrase')), texts=[])
