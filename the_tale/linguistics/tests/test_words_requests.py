# coding: utf-8# coding: utf-8
import datetime

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils import s11n
from dext.common.utils.urls import url

from utg import relations as utg_relations
from utg import words


from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)



class IndexRequestsTests(BaseRequestsTests):
    pass


class NewRequestsTests(BaseRequestsTests):

    def test_displaying_fields_for_all_forms(self):

        for word_type in utg_relations.WORD_TYPE.records:
            requested_url = url('linguistics:words:new', type=word_type.value)
            texts = [('"field_%d"' % i, 2) for i in xrange(words.Word.get_forms_number(word_type))]
            self.check_html_ok(self.request_html(requested_url), texts=texts)
