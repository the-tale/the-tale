# coding: utf-8# coding: utf-8
import datetime
import random

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils import s11n
from dext.common.utils.urls import url

from utg import relations as utg_relations
from utg import words as utg_words


from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map

from the_tale.linguistics.lexicon.groups import relations as lexicon_groups_relations
from the_tale.linguistics.lexicon import keys


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)



class IndexRequestsTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(url('linguistics:')), texts=[])

    def test_all_groups(self):
        texts = [group.text for group in lexicon_groups_relations.LEXICON_GROUP.records]
        self.check_html_ok(self.request_html(url('linguistics:')), texts=texts)

    def test_all_keys(self):
        texts = [key.text for key in keys.LEXICON_KEY.records]
        self.check_html_ok(self.request_html(url('linguistics:')), texts=texts)
