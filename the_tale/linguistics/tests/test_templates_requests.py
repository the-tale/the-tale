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
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import keys

from the_tale.linguistics.lexicon import logic as lexicon_logic


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

    def setUp(self):
        super(NewRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

    def test_key_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:new')), texts=['linguistics.templates.key.not_specified'])
        self.check_html_ok(self.request_html(url('linguistics:templates:new', key='www')), texts=['linguistics.templates.key.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:new', key=666)), texts=['linguistics.templates.key.not_found'], status_code=404)


    def test_fast_account(self):
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_html_ok(self.request_html(url('linguistics:templates:new')), texts=['common.fast_account'])


    def test_ban_forum_account(self):
        self.account_1.ban_forum(1)
        self.account_1.save()

        self.check_html_ok(self.request_html(url('linguistics:templates:new')), texts=['common.ban_forum'])

    def test_login_required(self):
        self.request_logout()
        url_ = url('linguistics:templates:new')
        self.check_redirect(url_, login_page_url(url_))


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

        self.request_login(self.account_1.email)

    def test_key_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:create')), 'linguistics.templates.key.not_specified')
            self.check_ajax_error(self.client.post(url('linguistics:templates:create', key='www')), 'linguistics.templates.key.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:create', key=666)), 'linguistics.templates.key.not_found')

    def test_fast_account(self):
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.client.post(self.requested_url), 'common.fast_account')


    def test_ban_forum_account(self):
        self.account_1.ban_forum(1)
        self.account_1.save()

        self.check_ajax_error(self.client.post(self.requested_url), 'common.ban_forum')

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(self.requested_url), 'common.login_required')

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

        self.assertEqual(last_prototype.author_id, self.account_1.id)
        self.assertEqual(last_prototype.parent_id, None)



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
                                                        verificators=[],
                                                        author=self.account_1)

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
                                                        verificators=[verificator_1, verificator_2, verificator_3],
                                                        author=self.account_1)

        self.check_html_ok(self.request_html(url('linguistics:templates:show', prototype.id)), texts=[verificator_1.text,
                                                                                                      verificator_2.text,
                                                                                                      verificator_3.text])



class EditRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(EditRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

        storage.raw_dictionary.refresh()
        storage.game_dictionary.refresh()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP
        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=[],
                                                            author=self.account_1)

        self.requested_url = url('linguistics:templates:edit', self.template.id)


    def test_template_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:edit', 'www')), texts=['linguistics.templates.template.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:edit', 666)), texts=['linguistics.templates.template.not_found'], status_code=404)

    def test_fast_account(self):
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_html_ok(self.request_html(self.requested_url), texts=['common.fast_account'])


    def test_ban_forum_account(self):
        self.account_1.ban_forum(1)
        self.account_1.save()

        self.check_html_ok(self.request_html(self.requested_url), texts=['common.ban_forum'])

    def test_login_required(self):
        self.request_logout()
        url_ = url('linguistics:templates:edit', self.template.id)
        self.check_redirect(url_, login_page_url(url_))


    def test_succcess(self):
        self.check_html_ok(self.request_html(self.requested_url))


    def test_validators(self):
        externals = lexicon_logic.get_verificators_externals(self.key)

        self.assertEqual(len(externals), 3)

        text = u'text_2'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])

        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[prototypes.Verificator(u'right-verificator-1', externals=externals[0]),
                                                                     prototypes.Verificator(u'wrong-verificator', externals=[{'hero': 12}]),
                                                                     prototypes.Verificator(u'right-verificator-2', externals=externals[2]),],
                                                       author=self.account_1)


        self.check_html_ok(self.request_html(url('linguistics:templates:edit', template.id)),
                           texts=['right-verificator-1',
                                  'right-verificator-2',
                                  ('wrong-verificator', 0)])



class UpdateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(UpdateRequestsTests, self).setUp()

        storage.raw_dictionary.refresh()
        storage.game_dictionary.refresh()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        externals = lexicon_logic.get_verificators_externals(self.key)
        self.template_text = u'[hero|загл] [level] [неизвестное слово|level]'
        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=[prototypes.Verificator(u'verificator-1', externals=externals[0]),
                                                                          prototypes.Verificator(u'verificator-2', externals=externals[2]),],
                                                            author=self.account_1)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:update', self.template.id)


    def test_template_errors(self):
        self.check_ajax_error(self.client.post(url('linguistics:templates:update', 'www'), {}), 'linguistics.templates.template.wrong_format')
        self.check_ajax_error(self.client.post(url('linguistics:templates:update', 666), {}), 'linguistics.templates.template.not_found')


    def test_fast_account(self):
        self.account_1.is_fast = True
        self.account_1.save()

        self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.fast_account')


    def test_ban_forum_account(self):
        self.account_1.ban_forum(1)
        self.account_1.save()

        self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.ban_forum')


    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_form_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.update.form_errors')


    def test_update__on_review_by_owner(self):

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', self.template.id)})

        self.assertEqual(self.template.utg_template.template, u'updated-template')
        self.assertEqual(len(self.template.verificators), 3)
        self.assertEqual(self.template.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(self.template.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': u'привидение', 'level': 13}))
        self.assertEqual(self.template.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': u'русалка', 'level': 13}))

        self.assertEqual(self.template.author_id, self.account_1.id)
        self.assertEqual(self.template.parent_id, None)


    def test_update__in_game_by_owner(self):

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_IN_GAME)

        last_prototype = prototypes.TemplatePrototype._db_latest()
        self.assertTrue(last_prototype.state.is_ON_REVIEW)

        self.assertNotEqual(last_prototype.id, self.template.id)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', last_prototype.id)})

        self.assertEqual(last_prototype.utg_template.template, u'updated-template')
        self.assertEqual(len(last_prototype.verificators), 3)
        self.assertEqual(last_prototype.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(last_prototype.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': u'привидение', 'level': 13}))
        self.assertEqual(last_prototype.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': u'русалка', 'level': 13}))

        self.assertEqual(last_prototype.author_id, self.account_1.id)
        self.assertEqual(last_prototype.parent_id, self.template.id)


    def test_update__on_review_by_other(self):
        self.request_logout()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        self.request_login(account.email)

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        last_prototype = prototypes.TemplatePrototype._db_latest()
        self.assertTrue(last_prototype.state.is_ON_REVIEW)

        self.assertNotEqual(last_prototype.id, self.template.id)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', last_prototype.id)})

        self.assertEqual(last_prototype.utg_template.template, u'updated-template')
        self.assertEqual(len(last_prototype.verificators), 3)
        self.assertEqual(last_prototype.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': u'призрак', 'level': 13}))
        self.assertEqual(last_prototype.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': u'привидение', 'level': 13}))
        self.assertEqual(last_prototype.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': u'русалка', 'level': 13}))

        self.assertEqual(last_prototype.author_id, account.id)
        self.assertEqual(last_prototype.parent_id, self.template.id)
