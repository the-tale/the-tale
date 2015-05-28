# coding: utf-8

import mock

from dext.common.utils.urls import url

from utg import templates as utg_templates
from utg import words as utg_words
from utg import relations as utg_relations

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game.logic import create_test_map
from the_tale.game import relations as game_relations

from the_tale.linguistics import prototypes
from the_tale.linguistics import storage
from the_tale.linguistics import relations
from the_tale.linguistics.lexicon import keys
from the_tale.linguistics.conf import linguistics_settings


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        storage.game_dictionary.refresh()

        self.moderator = self.accounts_factory.create_account()

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_template'])
        group.user_set.add(self.moderator._model)



class IndexRequestsTests(BaseRequestsTests):

    def test_state_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value, state='www')),
                           texts=['linguistics.templates.state.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value, state=666)),
                           texts=['linguistics.templates.state.not_found'], status_code=404)

    def test_key_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:', key='www')), texts=['linguistics.templates.key.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=666)), texts=['linguistics.templates.key.not_found'], status_code=404)

    def test_no_templates(self):
        self.assertEqual(prototypes.TemplatePrototype._db_count(), 0)
        self.check_html_ok(self.request_html(url('linguistics:templates:', key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE.value)),
                           texts=['pgf-no-templates-message'])

    def test_no_key(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:')), texts=[])


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

        race_restriction = storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                        game_relations.RACE.ELF.value)

        data = {'template': self.template_text,
                'verificator_0': u'Призрак 13 неизвестное слово',
                'verificator_1': u'Привидение 13',
                'verificator_2': u'',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.GENDER.value: '',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.RACE.value:  race_restriction.id}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
                response = self.client.post(self.requested_url, data)

        template = prototypes.TemplatePrototype._db_latest()

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', template.id)})

        self.assertEqual(template.utg_template.template, u'%s %s %s')
        self.assertEqual(len(template.verificators), 4)

        self.assertEqual(template.verificators[0], prototypes.Verificator(text=u'Призрак 13 неизвестное слово', externals={'hero': (u'герой', u''), 'level': (1, u'')}))
        self.assertEqual(template.verificators[1], prototypes.Verificator(text=u'Привидение 13', externals={'hero': (u'рыцарь', u'мн'), 'level': (2, u'')}))
        self.assertEqual(template.verificators[2], prototypes.Verificator(text=u'', externals={'hero': (u'привидение', u''), 'level': (5, u'')}))
        self.assertEqual(template.verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (5, u'')}))

        self.assertEqual(template.author_id, self.account_1.id)
        self.assertEqual(template.parent_id, None)

        self.assertEqual(template.raw_restrictions, frozenset([('hero', race_restriction.id)]))

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertTrue(last_contribution.state.is_ON_REVIEW)
        self.assertTrue(last_contribution.source.is_PLAYER)
        self.assertEqual(last_contribution.account_id, template.author_id)
        self.assertEqual(last_contribution.entity_id, template.id)


    def test_create_by_moderator(self):
        self.request_login(self.moderator.email)

        race_restriction = storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                        game_relations.RACE.ELF.value)

        data = {'template': self.template_text,
                'verificator_0': u'Призрак 13 неизвестное слово',
                'verificator_1': u'Привидение 13',
                'verificator_2': u'',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.GENDER.value: '',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.RACE.value:  race_restriction.id}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
                response = self.client.post(self.requested_url, data)

        template = prototypes.TemplatePrototype._db_latest()

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertTrue(last_contribution.state.is_ON_REVIEW)
        self.assertTrue(last_contribution.source.is_MODERATOR)
        self.assertEqual(last_contribution.account_id, template.author_id)
        self.assertEqual(last_contribution.entity_id, template.id)



class ShowRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(ShowRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP
        self.TEXT = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.TEXT, externals=['hero'])

        self.template =  prototypes.TemplatePrototype.create(key=self.key,
                                                             raw_template=self.TEXT,
                                                             utg_template=self.utg_template,
                                                             verificators=[],
                                                             author=self.account_1)

        result, account_id, bundle_id = register_user('moderator', 'moderator@test.com', '111111')
        self.moderator = AccountPrototype.get_by_id(account_id)

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_template'])
        group.user_set.add(self.moderator._model)

        self.request_login(self.account_1.email)


    def test_template_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:show', 'www')), texts=['linguistics.templates.template.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:templates:show', 666)), texts=['linguistics.templates.template.not_found'], status_code=404)

    def test_success(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:show', self.template.id)), texts=[('pgf-has-parent-message', 0),
                                                                                               ('pgf-has-child-message', 0),
                                                                                               ('pgf-replace-button', 0),
                                                                                               ('pgf-detach-button', 0),
                                                                                               ('pgf-in-game-button', 0),
                                                                                               ('pgf-on-review-button', 0),
                                                                                               ('pgf-remove-button', 1),
                                                                                               ('pgf-edit-button', 1) ])

    def test_success__in_game(self):
        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        self.check_html_ok(self.request_html(url('linguistics:templates:show', self.template.id)), texts=[('pgf-has-parent-message', 0),
                                                                                               ('pgf-has-child-message', 0),
                                                                                               ('pgf-replace-button', 0),
                                                                                               ('pgf-detach-button', 0),
                                                                                               ('pgf-in-game-button', 0),
                                                                                               ('pgf-on-review-button', 0),
                                                                                               ('pgf-remove-button', 0),
                                                                                               ('pgf-edit-button', 1) ])

    def test_success__unlogined(self):
        self.request_logout()
        self.check_html_ok(self.request_html(url('linguistics:templates:show', self.template.id)), texts=[('pgf-has-parent-message', 0),
                                                                                               ('pgf-has-child-message', 0),
                                                                                               ('pgf-replace-button', 0),
                                                                                               ('pgf-detach-button', 0),
                                                                                               ('pgf-in-game-button', 0),
                                                                                               ('pgf-on-review-button', 0),
                                                                                               ('pgf-remove-button', 0),
                                                                                               ('pgf-edit-button', 0) ])

    def test_success__moderator(self):
        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        self.request_login(self.moderator.email)

        child = prototypes.TemplatePrototype.create(key=self.key,
                                                    raw_template=self.TEXT,
                                                    utg_template=self.utg_template,
                                                    verificators=[],
                                                    author=self.account_1,
                                                    parent=self.template)

        self.check_html_ok(self.request_html(url('linguistics:templates:show', self.template.id)), texts=[('pgf-has-parent-message', 0),
                                                                                                          ('pgf-has-child-message', 1),
                                                                                                          ('pgf-replace-button', 0),
                                                                                                          ('pgf-detach-button', 0),
                                                                                                          ('pgf-in-game-button', 0),
                                                                                                          ('pgf-on-review-button', 1),
                                                                                                          ('pgf-remove-button', 1) ])
        self.check_html_ok(self.request_html(url('linguistics:templates:show', child.id)), texts=[('pgf-has-parent-message', 1),
                                                                                                  ('pgf-has-child-message', 0),
                                                                                                  ('pgf-replace-button', 1),
                                                                                                  ('pgf-detach-button', 1),
                                                                                                  ('pgf-in-game-button', 1),
                                                                                                  ('pgf-on-review-button', 0),
                                                                                                  ('pgf-remove-button', 1) ])

    def test_success__has_parent_or_child(self):
        child = prototypes.TemplatePrototype.create(key=self.key,
                                                    raw_template=self.TEXT,
                                                    utg_template=self.utg_template,
                                                    verificators=[],
                                                    author=self.account_1,
                                                    parent=self.template)

        self.check_html_ok(self.request_html(url('linguistics:templates:show', child.id)), texts=[('pgf-has-parent-message', 1),
                                                                                                  ('pgf-has-child-message', 0)])
        self.check_html_ok(self.request_html(url('linguistics:templates:show', self.template.id)), texts=[('pgf-has-parent-message', 0),
                                                                                                          ('pgf-has-child-message', 1)])

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
            texts = errors+['pgf-verificator-error-message'] if errors else [('pgf-verificator-error-message', 0)]
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

        verificators = prototypes.TemplatePrototype.get_start_verificatos(key=key)

        verificators[0].text = u'Призрак 1 w-1-ед,вн'
        verificators[1].text = u'Привидение 1'
        verificators[2].text = u'Русалка abrakadabra'

        prototype = prototypes.TemplatePrototype.create(key=key,
                                                        raw_template=TEXT,
                                                        utg_template=template,
                                                        verificators=verificators[:3],
                                                        author=self.account_1)

        self.check_html_ok(self.request_html(url('linguistics:templates:show', prototype.id)), texts=[verificators[0].text,
                                                                                                      verificators[1].text,
                                                                                                      verificators[2].text])



class EditRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(EditRequestsTests, self).setUp()
        self.request_login(self.account_1.email)

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

        result, account_id, bundle_id = register_user('test_user2', 'test_user2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)


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


    def test_verificators(self):
        text = u'text_2'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])

        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[prototypes.Verificator(u'right-verificator-1', externals={}),
                                                                     prototypes.Verificator(u'wrong-verificator-1', externals={'hero': (u'абракадабра', u'')}),
                                                                     prototypes.Verificator(u'right-verificator-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}),
                                                                     prototypes.Verificator(u'wrong-verificator-2', externals={'hero': (u'абракадабра', u''), 'level': (2, u'')}),],
                                                       author=self.account_1)


        self.check_html_ok(self.request_html(url('linguistics:templates:edit', template.id)),
                           texts=['right-verificator-1',
                                  'right-verificator-2',
                                  ('wrong-verificator-1', 0),
                                  ('wrong-verificator-2', 0)])


    def test_edit_anothers_author_template(self):
        text = u'text_2'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])

        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[prototypes.Verificator(u'right-verificator-1', externals={}),
                                                                     prototypes.Verificator(u'wrong-verificator-1', externals={'hero': (u'абракадабра', u'')}),
                                                                     prototypes.Verificator(u'right-verificator-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}),
                                                                     prototypes.Verificator(u'wrong-verificator-2', externals={'hero': (u'абракадабра', u''), 'level': (2, u'')}),],
                                                       author=self.account_2)


        self.check_html_ok(self.request_html(url('linguistics:templates:edit', template.id)),
                           texts=['linguistics.templates.edit.can_not_edit_anothers_template'])


    def test_edit_when_template_has_child(self):
        account_2 = self.accounts_factory.create_account()
        prototypes.TemplatePrototype.create(key=self.template.key,
                                            raw_template='updated-template',
                                            utg_template=self.template.utg_template,
                                            verificators=[],
                                            author=account_2,
                                            parent=self.template)

        self.check_html_ok(self.request_html(url('linguistics:templates:edit', self.template.id)),
                           texts=['linguistics.templates.edit.template_has_child'])



class UpdateRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(UpdateRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.text = u'[hero|загл] [level] [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=[prototypes.Verificator(u'verificator-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}),
                                                                          prototypes.Verificator(u'verificator-2', externals={'hero': (u'герой', u''), 'level': (2, u'')})],
                                                            author=self.account_1)

        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                account_id=self.account_1.id,
                                                entity_id=self.template.id,
                                                source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                state=self.template.state.contribution_state)

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


    def test_update__full_copy_restriction(self):

        data = {'template': self.template.raw_template,
                'verificator_0': u'verificator-1',
                'verificator_1': u'verificator-2'}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, data),
                                  'linguistics.templates.update.full_copy_restricted')


    def test_update__on_review_by_owner(self):

        race_restriction = storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                        game_relations.RACE.ELF.value)

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.GENDER.value: '',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.RACE.value:  race_restriction.id}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            with self.check_not_changed(prototypes.ContributionPrototype._db_count):
                response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', self.template.id)})

        self.assertEqual(self.template.raw_template, u'updated-template')
        self.assertEqual(self.template.utg_template.template, u'updated-template')

        self.assertEqual(len(self.template.verificators), 4)

        self.assertEqual(self.template.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(self.template.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(self.template.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': (u'привидение', u''), 'level': (1, u'')}))
        self.assertEqual(self.template.verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (1, u'')}))

        self.assertEqual(self.template.author_id, self.account_1.id)
        self.assertEqual(self.template.parent_id, None)

        self.assertEqual(self.template.raw_restrictions, frozenset([('hero', race_restriction.id)]))



    def test_update__in_game_by_owner(self):

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_delta(prototypes.TemplatePrototype._db_count, 1):
            with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
                response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_IN_GAME)

        template = prototypes.TemplatePrototype._db_latest()
        self.assertTrue(template.state.is_ON_REVIEW)

        self.assertNotEqual(template.id, self.template.id)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', template.id)})

        self.assertEqual(template.utg_template.template, u'updated-template')
        self.assertEqual(len(template.verificators), 4)

        self.assertEqual(template.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(template.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(template.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': (u'привидение', u''), 'level': (1, u'')}))
        self.assertEqual(template.verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (1, u'')}))

        self.assertEqual(template.author_id, self.account_1.id)
        self.assertEqual(template.parent_id, self.template.id)

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertTrue(last_contribution.state.is_ON_REVIEW)
        self.assertTrue(last_contribution.source.is_PLAYER)
        self.assertEqual(last_contribution.account_id, template.author_id)
        self.assertEqual(last_contribution.entity_id, template.id)


    def test_update__in_game_by_moderator(self):

        self.request_login(self.moderator.email)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
                response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_IN_GAME)

        template = prototypes.TemplatePrototype._db_latest()
        self.assertTrue(template.state.is_IN_GAME)

        self.assertEqual(template.id, self.template.id)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', template.id)})

        self.assertEqual(template.utg_template.template, u'updated-template')
        self.assertEqual(len(template.verificators), 4)

        self.assertEqual(template.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(template.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(template.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': (u'привидение', u''), 'level': (1, u'')}))
        self.assertEqual(template.verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (1, u'')}))

        self.assertEqual(template.author_id, self.account_1.id)
        self.assertEqual(template.parent_id, None)

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertTrue(last_contribution.state.is_IN_GAME)
        self.assertTrue(last_contribution.source.is_MODERATOR)
        self.assertEqual(last_contribution.account_id, self.moderator.id)
        self.assertEqual(last_contribution.entity_id, template.id)

    def test_update__on_review_by_moderator(self):

        self.request_login(self.moderator.email)

        race_restriction = storage.restrictions_storage.get_restriction(relations.TEMPLATE_RESTRICTION_GROUP.RACE,
                                                                        game_relations.RACE.ELF.value)

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.GENDER.value: '',
                'restriction_hero_%d' % relations.TEMPLATE_RESTRICTION_GROUP.RACE.value:  race_restriction.id}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            with self.check_delta(prototypes.ContributionPrototype._db_count, 1):
                response = self.client.post(self.requested_url, data)

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        self.check_ajax_ok(response, data={'next_url': url('linguistics:templates:show', self.template.id)})

        self.assertEqual(self.template.raw_template, u'updated-template')
        self.assertEqual(self.template.utg_template.template, u'updated-template')

        self.assertEqual(len(self.template.verificators), 4)

        self.assertEqual(self.template.verificators[0], prototypes.Verificator(text=u'verificatorx-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(self.template.verificators[1], prototypes.Verificator(text=u'verificatorx-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}))
        self.assertEqual(self.template.verificators[2], prototypes.Verificator(text=u'verificatorx-3', externals={'hero': (u'привидение', u''), 'level': (1, u'')}))
        self.assertEqual(self.template.verificators[3], prototypes.Verificator(text=u'', externals={'hero': (u'героиня', u''), 'level': (1, u'')}))

        self.assertEqual(self.template.author_id, self.account_1.id)
        self.assertEqual(self.template.parent_id, None)

        self.assertEqual(self.template.raw_restrictions, frozenset([('hero', race_restriction.id)]))

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertTrue(last_contribution.state.is_ON_REVIEW)
        self.assertTrue(last_contribution.source.is_MODERATOR)
        self.assertEqual(last_contribution.account_id, self.moderator.id)
        self.assertEqual(last_contribution.entity_id, self.template.id)


    def test_update__on_review_by_other(self):
        self.request_logout()

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        account = AccountPrototype.get_by_id(account_id)

        self.request_login(account.email)

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, data),
                                  'linguistics.templates.update.can_not_edit_anothers_template')

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        last_prototype = prototypes.TemplatePrototype._db_latest()
        self.assertTrue(last_prototype.state.is_ON_REVIEW)
        self.assertEqual(last_prototype.id, self.template.id)

        self.assertEqual(last_prototype.utg_template.template, '%s %s %s')

        self.assertEqual(len(last_prototype.verificators), 2)

        self.assertEqual(last_prototype.verificators[0], prototypes.Verificator(text=u'verificator-1', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}))
        self.assertEqual(last_prototype.verificators[1], prototypes.Verificator(text=u'verificator-2', externals={'hero': (u'герой', u''), 'level': (2, u'')}))

        self.assertEqual(last_prototype.author_id, self.account_1.id)
        self.assertEqual(last_prototype.parent_id, None)


    def test_update__has_child(self):
        account_2 = self.accounts_factory.create_account()

        child = prototypes.TemplatePrototype.create(key=self.template.key,
                                                    raw_template='updated-template',
                                                    utg_template=self.template.utg_template,
                                                    verificators=[],
                                                    author=account_2,
                                                    parent=self.template)

        data = {'template': 'updated-template',
                'verificator_0': u'verificatorx-1',
                'verificator_1': u'verificatorx-2',
                'verificator_2': u'verificatorx-3'}

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, data),
                                  'linguistics.templates.update.template_has_child')

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)

        self.assertEqual(prototypes.TemplatePrototype._db_latest().id, child.id)


class ReplaceRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(ReplaceRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])

        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)

        self.author_contribution = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                           account_id=self.account_1.id,
                                                                           entity_id=self.template.id,
                                                                           source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                           state=self.template.state.contribution_state)

        self.account_2 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:replace', self.template.id)


    def test_template_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:replace', 'www'), {}), 'linguistics.templates.template.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:replace', 666), {}), 'linguistics.templates.template.not_found')


    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count) :
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.moderation_rights')


    def test_no_parent(self):
        self.request_login(self.moderator.email)

        self.assertEqual(self.template.parent_id, None)

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.replace.no_parent')


    def test_replace__on_review(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_2,
                                                       parent=self.template)

        self.assertTrue(self.template.state.is_ON_REVIEW)

        with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template.id), {}))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)

        template.reload()

        self.assertTrue(template.state.is_ON_REVIEW)
        self.assertEqual(template.parent_id, None)


    def test_replace__in_game(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_2,
                                                       parent=self.template)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template.id), {}))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)

        template.reload()

        self.assertTrue(template.state.is_IN_GAME)
        self.assertEqual(template.parent_id, None)


    def test_replace__parent_with_no_errors_by_child_with_errors(self):
        self.request_login(self.moderator.email)

        verificators = [ prototypes.Verificator(text=u'Героиня 1 w-1-нс,ед,вн', externals={'hero': (u'героиня', u''), 'level': (1, u'')}),
                         prototypes.Verificator(text=u'Рыцари 1 w-1-нс,мн,вн', externals={'hero': (u'рыцарь', u'мн'), 'level': (5, u'')}),
                         prototypes.Verificator(text=u'Герой 1 w-1-нс,ед,вн', externals={'hero': (u'герой', u''), 'level': (2, u'')}),
                         prototypes.Verificator(text=u'Привидение 1 w-1-нс,ед,вн', externals={'hero': (u'привидение', u''), 'level': (5, u'')}) ]

        dictionary = storage.game_dictionary.item

        word = utg_words.Word.create_test_word(type=utg_relations.WORD_TYPE.NOUN, prefix=u'w-1-', only_required=True)
        word.forms[0] = u'пепельница'

        dictionary.add_word(word)

        self.template.update(verificators=verificators)

        self.assertTrue(self.template.errors_status.is_NO_ERRORS)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_2,
                                                       parent=self.template)

        self.assertTrue(template.errors_status.is_HAS_ERRORS)

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:replace', template.id), {}),
                                  'linguistics.templates.replace.can_not_replace_with_errors')


    def test_replace__parent_inheritance(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])

        template_1 = prototypes.TemplatePrototype.create(key=self.key,
                                                         raw_template=text,
                                                         utg_template=utg_template,
                                                         verificators=[],
                                                         author=self.account_2,
                                                         parent=self.template)


        template_2 = prototypes.TemplatePrototype.create(key=self.key,
                                                         raw_template=text,
                                                         utg_template=utg_template,
                                                         verificators=[],
                                                         author=self.account_2,
                                                         parent=template_1)

        with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template_2.id), {}))

        self.template.reload()
        template_2.reload()

        self.assertNotEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)
        self.assertEqual(prototypes.TemplatePrototype.get_by_id(template_1.id), None)
        self.assertEqual(template_2.parent_id, self.template.id)


    def test_replace__wrong_keys(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_2,
                                                       parent=self.template)

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:replace', template.id), {}), 'linguistics.templates.replace.not_equal_keys')


    def test_reassigning_contributions(self):
        self.request_login(self.moderator.email)

        account_3 = self.accounts_factory.create_account()

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=account_3,
                                                       parent=self.template)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                account_id=account_3.id,
                                                entity_id=template.id,
                                                source=relations.CONTRIBUTION_SOURCE.random(),
                                                state=template.state.contribution_state)

        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                account_id=self.account_2.id,
                                                entity_id=self.template.id,
                                                source=relations.CONTRIBUTION_SOURCE.random(),
                                                state=self.template.state.contribution_state)

        with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=self.template.id).count, -2):
            with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=template.id).count, 2):
                with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
                    self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template.id), {}))

        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=self.template.id).count(), 0)
        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=template.id).count(), 3)
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE).values_list('account_id', flat=True)),
                         set([self.account_1.id, self.account_2.id, account_3.id]))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)

        template.reload()

        self.assertTrue(template.state.is_IN_GAME)
        self.assertEqual(template.parent_id, None)


    def test_remove_duplicate_contributions(self):
        self.request_login(self.moderator.email)

        account_3 = self.accounts_factory.create_account()

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=account_3,
                                                       parent=self.template)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=account_3.id,
                                                                 entity_id=template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=template.state.contribution_state)

        contribution_2 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.account_1.id,
                                                                 entity_id=template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=self.template.state.contribution_state)

        contribution_3 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.account_2.id,
                                                                 entity_id=self.template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=self.template.state.contribution_state)

        with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=self.template.id).count, -2):
            with self.check_delta(prototypes.ContributionPrototype._db_filter(entity_id=template.id).count, 1):
                with self.check_delta(prototypes.TemplatePrototype._db_count, -1):
                    self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template.id), {}))

        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=self.template.id).count(), 0)
        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=template.id).count(), 3)
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE).values_list('account_id', flat=True)),
                         set([self.account_1.id, self.account_2.id, account_3.id]))
        self.assertEqual(set(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE).values_list('id', flat=True)),
                         set([self.author_contribution.id, contribution_1.id, contribution_3.id]))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)

        template.reload()

        self.assertTrue(template.state.is_IN_GAME)
        self.assertEqual(template.parent_id, None)


    def test_update_templates_state(self):
        self.request_login(self.moderator.email)

        account_3 = self.accounts_factory.create_account()

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=account_3,
                                                       parent=self.template)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=account_3.id,
                                                                 entity_id=template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=relations.CONTRIBUTION_STATE.random())

        contribution_3 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.account_2.id,
                                                                 entity_id=self.template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.random(),
                                                                 state=relations.CONTRIBUTION_STATE.random())

        self.check_ajax_ok(self.client.post(url('linguistics:templates:replace', template.id), {}))

        self.assertEqual(prototypes.ContributionPrototype._db_filter(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                     entity_id=template.id,
                                                                     state=relations.CONTRIBUTION_STATE.IN_GAME).count(), 3)

class DetachRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(DetachRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)

        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('moderator', 'moderator@test.com', '111111')
        self.moderator = AccountPrototype.get_by_id(account_id)

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_template'])
        group.user_set.add(self.moderator._model)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:detach', self.template.id)


    def test_template_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:detach', 'www'), {}), 'linguistics.templates.template.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:detach', 666), {}), 'linguistics.templates.template.not_found')


    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_count) :
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.moderation_rights')


    def test_no_parent(self):
        self.request_login(self.moderator.email)

        self.assertEqual(self.template.parent_id, None)

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.detach.no_parent')


    def test_detach(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_2,
                                                       parent=self.template)

        self.assertTrue(self.template.state.is_ON_REVIEW)

        self.check_ajax_ok(self.client.post(url('linguistics:templates:detach', template.id), {}))

        template.reload()
        self.assertEqual(template.parent_id, None)



class InGameRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(InGameRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)

        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                account_id=self.account_1.id,
                                                entity_id=self.template.id,
                                                source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                state=self.template.state.contribution_state)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:in-game', self.template.id)


    def test_template_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:in-game', 'www'), {}), 'linguistics.templates.template.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:in-game', 666), {}), 'linguistics.templates.template.not_found')


    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).count) :
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.moderation_rights')


    def test_has_parent(self):
        self.request_login(self.moderator.email)

        text = u'[hero|загл] 2 [пепельница|hero|вн]'
        utg_template = utg_templates.Template()
        utg_template.parse(text, externals=['hero'])
        template = prototypes.TemplatePrototype.create(key=self.key,
                                                       raw_template=text,
                                                       utg_template=utg_template,
                                                       verificators=[],
                                                       author=self.account_1,
                                                       parent=self.template)

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:in-game', template.id), {}), 'linguistics.templates.in_game.has_parent')

    def test_already_in_game(self):
        self.request_login(self.moderator.email)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.IN_GAME).count):
                self.check_ajax_ok(self.client.post(self.requested_url))


    def test_in_game(self):
        self.request_login(self.moderator.email)

        self.assertTrue(self.template.state.is_ON_REVIEW)

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            with self.check_delta(prototypes.ContributionPrototype._db_filter(state=relations.CONTRIBUTION_STATE.ON_REVIEW).count, -1):
                with self.check_delta(prototypes.ContributionPrototype._db_filter(state=relations.CONTRIBUTION_STATE.IN_GAME).count, 1):
                    self.check_ajax_ok(self.client.post(self.requested_url))

        self.template.reload()
        self.assertTrue(self.template.state.is_IN_GAME)

        last_contribution = prototypes.ContributionPrototype._db_latest()

        self.assertTrue(last_contribution.type.is_TEMPLATE)
        self.assertEqual(last_contribution.account_id, self.template.author_id)
        self.assertEqual(last_contribution.entity_id, self.template.id)


class OnReviewRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(OnReviewRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)
        prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                account_id=self.account_1.id,
                                                entity_id=self.template.id,
                                                source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                state=self.template.state.contribution_state)


        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:on-review', self.template.id)


    def test_template_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:on-review', 'www'), {}), 'linguistics.templates.template.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:on-review', 666), {}), 'linguistics.templates.template.not_found')


    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count) :
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.moderation_rights')


    def test_already_on_review(self):
        self.request_login(self.moderator.email)

        self.template.state = relations.TEMPLATE_STATE.ON_REVIEW
        self.template.save()

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count):
            self.check_ajax_ok(self.client.post(self.requested_url))


    def test_on_review(self):
        self.request_login(self.moderator.email)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        with self.check_not_changed(prototypes.ContributionPrototype._db_count):
            with self.check_not_changed(prototypes.ContributionPrototype._db_filter(state=relations.CONTRIBUTION_STATE.ON_REVIEW).count):
                with self.check_not_changed(prototypes.ContributionPrototype._db_filter(state=relations.CONTRIBUTION_STATE.IN_GAME).count):
                    self.check_ajax_ok(self.client.post(self.requested_url))

        self.template.reload()
        self.assertTrue(self.template.state.is_ON_REVIEW)



class RemoveRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(RemoveRequestsTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:templates:remove', self.template.id)


    def test_template_errors(self):
        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(url('linguistics:templates:remove', 'www'), {}), 'linguistics.templates.template.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:templates:remove', 666), {}), 'linguistics.templates.template.not_found')


    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')

    def test_moderation_rights(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(prototypes.TemplatePrototype._db_filter(state=relations.TEMPLATE_STATE.ON_REVIEW).count) :
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.templates.remove.no_rights')


    def test_remove(self):
        self.request_login(self.moderator.email)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        self.check_ajax_ok(self.client.post(self.requested_url))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)


    def test_remove_contributions(self):
        self.request_login(self.moderator.email)

        contribution_1 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.account_1.id,
                                                                 entity_id=self.template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.ON_REVIEW)

        contribution_2 = prototypes.ContributionPrototype.create(type=relations.CONTRIBUTION_TYPE.TEMPLATE,
                                                                 account_id=self.account_2.id,
                                                                 entity_id=self.template.id,
                                                                 source=relations.CONTRIBUTION_SOURCE.PLAYER,
                                                                 state=relations.CONTRIBUTION_STATE.IN_GAME)

        self.check_ajax_ok(self.client.post(self.requested_url))

        self.assertFalse(prototypes.ContributionPrototype._db_filter(id=contribution_1.id).exists())
        self.assertTrue(prototypes.ContributionPrototype._db_filter(id=contribution_2.id).exists())

    def test_remove_by_owner(self):
        self.request_login(self.account_1.email)

        self.template.state = relations.TEMPLATE_STATE.IN_GAME
        self.template.save()

        with self.check_not_changed(prototypes.TemplatePrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url), 'linguistics.templates.remove.no_rights')

        self.template.state = relations.TEMPLATE_STATE.ON_REVIEW
        self.template.save()

        self.check_ajax_ok(self.client.post(self.requested_url))

        self.assertEqual(prototypes.TemplatePrototype.get_by_id(self.template.id), None)


class SpecificationTests(BaseRequestsTests):

    def test_success(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:specification')), texts=[])


class EditKeyTests(BaseRequestsTests):

    def setUp(self):
        super(EditKeyTests, self).setUp()

        self.key = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1)

    def test_success(self):
        self.request_login(self.moderator.email)
        self.check_html_ok(self.request_html(url('linguistics:templates:edit-key', self.template.id)), texts=[str(self.template.key)])

    def test_no_rights(self):
        self.check_html_ok(self.request_html(url('linguistics:templates:edit-key', self.template.id)), texts=['pgf-error-linguistics.templates.moderation_rights'])



class ChangeKeyTests(BaseRequestsTests):

    def setUp(self):
        super(ChangeKeyTests, self).setUp()

        self.key_1 = keys.LEXICON_KEY.HERO_COMMON_JOURNAL_LEVEL_UP
        self.key_2 = keys.LEXICON_KEY.HERO_COMMON_DIARY_CREATE

        self.verificators = prototypes.TemplatePrototype.get_start_verificatos(key=self.key_1)
        self.verificators[0].text = u'verificator-1'
        self.verificators[1].text = u'verificator-2'

        self.text = u'[hero|загл] 1 [пепельница|hero|вн]'
        self.utg_template = utg_templates.Template()
        self.utg_template.parse(self.text, externals=['hero'])
        self.template = prototypes.TemplatePrototype.create(key=self.key_1,
                                                            raw_template=self.text,
                                                            utg_template=self.utg_template,
                                                            verificators=self.verificators[:2],
                                                            author=self.account_1,
                                                            state=relations.TEMPLATE_STATE.IN_GAME)

        self.request_login(self.moderator.email)

    def test_no_rights(self):
        self.request_logout()
        self.check_ajax_error(self.post_ajax_json(url('linguistics:templates:change-key', self.template.id), {'key': str(self.key_2)}),
                              'linguistics.templates.moderation_rights')

    def test_form_errors(self):
        self.check_ajax_error(self.post_ajax_json(url('linguistics:templates:change-key', self.template.id), {}),
                              'linguistics.templates.change_key.form_errors')

    def test_has_child(self):
        prototypes.TemplatePrototype.create(key=self.key_1,
                                            raw_template=self.text,
                                            utg_template=self.utg_template,
                                            verificators=self.verificators[:2],
                                            author=self.account_1,
                                            parent=self.template)

        self.check_ajax_error(self.post_ajax_json(url('linguistics:templates:change-key', self.template.id), {'key': str(self.key_2)}),
                              'linguistics.templates.change_key.template_has_child')

    def test_success(self):
        self.check_ajax_ok(self.post_ajax_json(url('linguistics:templates:change-key', self.template.id), {'key': str(self.key_2)}))

        self.template.reload()

        self.assertEqual(self.template.key, self.key_2)
        self.assertTrue(self.template.state.is_ON_REVIEW)
        self.assertEqual(self.template.parent_id, None)
        self.assertEqual(self.template.verificators, [])

    def test_has_parent(self):
        child = prototypes.TemplatePrototype.create(key=self.key_1,
                                                    raw_template=self.text,
                                                    utg_template=self.utg_template,
                                                    verificators=[],
                                                    author=self.account_1,
                                                    parent=self.template,
                                                    state=relations.TEMPLATE_STATE.ON_REVIEW)

        self.check_ajax_ok(self.post_ajax_json(url('linguistics:templates:change-key', child.id), {'key': str(self.key_2)}))

        child.reload()

        self.assertEqual(child.key, self.key_2)
        self.assertTrue(child.state.is_ON_REVIEW)
        self.assertEqual(child.parent_id, None)
        self.assertEqual(child.verificators, [])
