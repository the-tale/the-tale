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
from utg import templates as utg_templates
from utg import dictionary as utg_dictionary

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map

from the_tale.linguistics import prototypes
from the_tale.linguistics import storage
from the_tale.linguistics.lexicon import keys


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)



class IndexRequestsTests(BaseRequestsTests):

    def test_state_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value, state='www')),
                           texts=['linguistics.templates.state.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value, state=666)),
                           texts=['linguistics.templates.state.not_found'], status_code=404)

    def test_key_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:')), texts=['linguistics.templates.key.not_specified'])
        self.check_html_ok(self.request_html(url('linguistics:templates:', key='www')), texts=['linguistics.templates.key.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=666)), texts=['linguistics.templates.key.not_found'], status_code=404)

    def test_no_templates(self):
        self.assertEqual(prototypes.TemplatePrototype._db_count(), 0)
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value)),
                           texts=['pgf-no-templates-message'])



class NewRequestsTests(BaseRequestsTests):

    def test_key_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:new')), texts=['linguistics.templates.key.not_specified'])
        self.check_html_ok(self.request_html(url('linguistics:templates:new', key='www')), texts=['linguistics.templates.key.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:new', key=666)), texts=['linguistics.templates.key.not_found'], status_code=404)


    def test_succcess(self):
        key = keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE
        texts = [key.description]
        self.check_html_ok(self.request_html(url('linguistics:templates:new', key=key.value)),
                           texts=texts)



class CreateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()
        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP
        self.requested_url = url('linguistics:templates:create', key=self.key.value)

        self.template_text = u'[hero|загл] [level] [неизвестное слово|level]'

    def test_key_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:create')), 'linguistics.templates.key.not_specified')
            self.check_ajax_error(self.client.post(url('linguistics:templates:create', key='www')), 'linguistics.templates.key.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:create', key=666)), 'linguistics.templates.key.not_found')


    def test_form_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.create.form_errors')


    def test_create(self):
        data = {'template': self.template_text,
                'verificator_0': u'Призрак 13 неизвестное слово',
                'verificator_1': u'Привидение 13',
                'verificator_2': u''}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            response = self.client.post(self.requested_url, data)

        last_prototype = prototypes.TemplatePrototype._db_latest()

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', last_prototype.id)})

        self.assertEqual(last_prototype.utg_template.template, u'%s %s %s')
        self.assertEqual(len(last_prototype.verificators), 3)
        self.assertEqual(last_prototype.verificators[0], prototypes.Verificator(text=u'Призрак 13 неизвестное слово', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(last_prototype.verificators[1], prototypes.Verificator(text=u'Привидение 13', externals={'hero': u'привидение', 'level': 13}))
        self.assertEqual(last_prototype.verificators[2], prototypes.Verificator(text=u'', externals={'hero': u'русалка', 'level': 13}))



class ShowRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(ShowRequestsTests, self).setUp()

        storage.raw_dictionary.refresh()
        storage.game_dictionary.refresh()

    def test_template_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:show', 'www')), texts=['linguistics.templates.template.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:show', 666)), texts=['linguistics.templates.template.not_found'], status_code=404)

    def check_errors(self, errors):

        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[])

        with mock.patch('the_tale.linguistics.prototypes.TemplatePrototype.get_errors', lambda *argv, **kwargs: errors):
            texts = errors+['pgf-errors-messages'] if errors else [('pgf-errors-messages', 0)]
            self.check_html_ok(self.request_html(url('linguistics:templates:show', prototype.id)), texts=texts)

    def test_no_errors(self):
        self.check_errors(errors=[])

    def test_has_errors(self):
        self.check_errors(errors=['bla-bla-bla-error', 'xxx-tttt-yyyy--zzzz'])

    def test_verificators(self):
        key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'

        template = utg_templates.Template()

        template.parse(TEXT, externals=['hero'])

        verificator_1 = prototypes.Verificator(text=u'Призрак 1 w-1-ед,вн', externals={'hero': u'призрак', 'level': 13})
        verificator_2 = prototypes.Verificator(text=u'Привидение 1', externals={'hero': u'привидение', 'level': 13})
        verificator_3 = prototypes.Verificator(text=u'Русалка abrakadabra', externals={'hero': u'русалка', 'level': 13})

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=[verificator_1, verificator_2, verificator_3])

        self.check_html_ok(self.request_html(url('linguistics:templates:show', prototype.id)), texts=[verificator_1.text,
                                                                                                      verificator_2.text,
                                                                                                      verificator_3.text])
