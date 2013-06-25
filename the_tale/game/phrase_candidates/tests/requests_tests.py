# coding: utf-8
import random

import mock

from django.test import client
from django.core.urlresolvers import reverse

from dext.utils.urls import url

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from game.text_generation import get_phrases_types
from game.logic import create_test_map

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.phrase_candidates.models import PhraseCandidate, PHRASE_CANDIDATE_STATE
from game.phrase_candidates.prototypes import PhraseCandidatePrototype
from game.phrase_candidates.conf import phrase_candidates_settings
from game.phrase_candidates.forms import SUBTYPE_CHOICES_IDS, UNKNOWN_TYPE_ID

class RequestsTestsBase(TestCase):

    def setUp(self):
        super(RequestsTestsBase, self).setUp()

        self.place1, self.place2, self.place3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.moderators_group = sync_group('phrase moderators group', ['phrase_candidates.moderate_phrasecandidate'])
        self.developers_group = sync_group('developers group', ['phrase_candidates.add_to_game_phrasecandidate'])


    def create_phrase(self, id_, author, text=None):
        phrases_modules = get_phrases_types()
        phrase_type = random.choice(phrases_modules['modules'].keys())
        phrase_subtype = random.choice(phrases_modules['modules'][phrase_type]['types'].keys())

        if text is None:
            text = u'text %d' % id_

        return PhraseCandidatePrototype.create(type_=phrase_type,
                                               type_name=u'type %d' % id_,
                                               subtype=phrase_subtype,
                                               subtype_name=u'subtype %d' % id_,
                                               author=author,
                                               text=text)

    def get_another_phrase_subtype(self, phrase):
        phrases_modules = get_phrases_types()
        phrase_type = phrase.type
        phrase_subtype = phrase.subtype
        while phrase_subtype == phrase.subtype:
            phrase_type = random.choice(phrases_modules['modules'].keys())
            phrase_subtype = random.choice(phrases_modules['modules'][phrase_type]['types'].keys())
        return phrase_type, phrase_subtype



class RequestsTests(RequestsTestsBase):

    def setUp(self):
        super(RequestsTests, self).setUp()

    def test_phrase_not_found(self):
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.request_ajax_json(reverse('game:phrase-candidates:edit', args=[666])), 'phrase_candidates.phrase_not_found')


class IndexRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=1, author=self.account_1)
        self.phrase_2 = self.create_phrase(id_=2, author=self.account_1)
        self.phrase_3 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_1@test.com')

    def test_first_page(self):
        self.request_logout()
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=[(self.account_1.nick, 2),
                                                                                       (self.account_2.nick, 1),
                                                                                       (self.phrase_1.text, 1),
                                                                                       (self.phrase_2.text, 1),
                                                                                       (self.phrase_3.text, 1),
                                                                                       (u'pgf-no-phrases-message', 0)])

    def test_second_page(self):
        texts = [(u'pgf-no-phrases-message', 0)]
        for i in xrange(phrase_candidates_settings.PHRASES_ON_PAGE):
            phrase = self.create_phrase(id_=3+1+i, author=self.account_3)
            texts.append((phrase.text, 1))

        texts.append((self.account_3.nick, phrase_candidates_settings.PHRASES_ON_PAGE))

        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=texts)

        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')+'?page=2'), texts=[(self.account_1.nick, 3),
                                                                                                 (self.account_2.nick, 1),
                                                                                                 (self.phrase_1.text, 1),
                                                                                                 (self.phrase_2.text, 1),
                                                                                                 (self.phrase_3.text, 1),
                                                                                                 (u'pgf-no-phrases-message', 0)])

    def test_large_page_number(self):
        self.check_redirect(reverse('game:phrase-candidates:')+'?page=666', reverse('game:phrase-candidates:')+'?page=1')

    def test_no_phrases(self):
        PhraseCandidate.objects.all().delete()
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=[(u'pgf-no-phrases-message', 1)])

    def test_author_filter_not_found(self):
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')+('?author_id=%d' % self.account_3.id)), texts=[(u'pgf-no-phrases-message', 1)])

    def test_author_filter(self):
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')+('?author_id=%d' % self.account_1.id)), texts=[(self.account_1.nick, 4),
                                                                                                                             (self.account_2.nick, 0),
                                                                                                                             (self.phrase_1.text, 1),
                                                                                                                             (self.phrase_2.text, 1),
                                                                                                                             (self.phrase_3.text, 0),
                                                                                                                             (u'pgf-no-phrases-message', 0)])

    def test_state_filter_not_found(self):
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')+('?state=%d' % PHRASE_CANDIDATE_STATE.ADDED)), texts=[(u'pgf-no-phrases-message', 1)])

    def test_state_filter(self):
        self.phrase_2.state = PHRASE_CANDIDATE_STATE.REMOVED
        self.phrase_2.save()

        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')+('?state=%d' % PHRASE_CANDIDATE_STATE.REMOVED)), texts=[(self.account_1.nick, 2),
                                                                                                                                      (self.account_2.nick, 0),
                                                                                                                                      (self.phrase_1.text, 0),
                                                                                                                                      (self.phrase_2.text, 1),
                                                                                                                                      (self.phrase_3.text, 0),
                                                                                                                                      (u'pgf-no-phrases-message', 0)])


    def test_edit_controls_hidden(self):
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=[(u'pgf-edit-phrase-button', 0),
                                                                                       (u'pgf-approve-phrase-button', 0),
                                                                                       (u'pgf-remove-phrase-button', 0),
                                                                                       (u'pgf-add-to-game-phrase-button', 0),])

    def test_edit_controls_shown(self):
        self.moderators_group.account_set.add(self.account_1._model)
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=[(u'pgf-edit-phrase-button', 1+1*3),
                                                                                       (u'pgf-approve-phrase-button', 1*3),
                                                                                       (u'pgf-remove-phrase-button', 1*3),
                                                                                       (u'pgf-add-to-game-phrase-button', 0),])

    def test_add_to_game_controls_shown(self):
        self.developers_group.account_set.add(self.account_1._model)
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:')), texts=[(u'pgf-edit-phrase-button', 0),
                                                                                       (u'pgf-approve-phrase-button', 0),
                                                                                       (u'pgf-remove-phrase-button', 0),
                                                                                       (u'pgf-add-to-game-phrase-button', 1*3),])


class TypesRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(TypesRequestsTests, self).setUp()
        self.request_login('test_user_1@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:types')), texts=[('pgf-add-phrase-button', 0)])

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:types')), texts=[('pgf-add-phrase-button', 0)])

    def test_success(self):

        texts = ['pgf-add-phrase-button']
        phrases_modules = get_phrases_types()
        for phrase_type in phrases_modules['modules']:
            texts.extend(phrases_modules['modules'][phrase_type]['types'].keys())

        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:types')), texts=texts)


class NewRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(NewRequestsTests, self).setUp()

        self.phrases_modules = get_phrases_types()
        self.phrase_type = random.choice(self.phrases_modules['modules'].keys())
        self.phrase_subtype = random.choice(self.phrases_modules['modules'][self.phrase_type]['types'].keys())
        self.phrase_data = self.phrases_modules['modules'][self.phrase_type]['types'][self.phrase_subtype]

        self.request_login('test_user_1@test.com')

    def create_new_url(self, phrase_type=None, phrase_subtype=None):
        if phrase_type is None: phrase_type = self.phrase_type
        if phrase_subtype is None: phrase_subtype = self.phrase_subtype
        return reverse('game:phrase-candidates:new')+('?phrase_type=%s&phrase_subtype=%s' % (phrase_type, phrase_subtype))

    def test_login_required(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(self.create_new_url()), texts=['common.login_required'])

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_ajax_html(self.create_new_url()), texts=['common.fast_account'])

    @mock.patch('accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned(self):
        self.request_login('test_user_1@test.com')
        self.check_html_ok(self.request_ajax_html(self.create_new_url()), texts=['common.ban_forum'])

    def test_success(self):
        texts = [(self.phrase_type, 2),
                 (self.phrase_subtype, 1),
                 (self.phrase_data['name'], 1),
                 (self.phrase_data['example'], 1),
                 (self.phrase_data['description'], 1)]

        self.check_html_ok(self.request_ajax_html(self.create_new_url()), texts=texts)

    def test_wrong_module(self):
        self.check_ajax_error(self.request_ajax_json(self.create_new_url(phrase_type=u'bla-bla-bla')),
                              u'phrase_candidates.new.type_not_exist')

    def test_wrong_subtype(self):
        self.check_ajax_error(self.request_ajax_json(self.create_new_url(phrase_subtype=u'bla-bla-bla')),
                              u'phrase_candidates.new.type_not_exist')


class CreateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()

        self.phrases_modules = get_phrases_types()
        self.phrase_type = random.choice(self.phrases_modules['modules'].keys())
        self.phrase_subtype = random.choice(self.phrases_modules['modules'][self.phrase_type]['types'].keys())
        self.phrase_data = self.phrases_modules['modules'][self.phrase_type]['types'][self.phrase_subtype]

        self.request_login('test_user_1@test.com')


    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': self.phrase_type,
                                                                                          'phrase_subtype': self.phrase_subtype,
                                                                                          'text': 'created-text'}), 'common.login_required')
    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': self.phrase_type,
                                                                                          'phrase_subtype': self.phrase_subtype,
                                                                                          'text': 'created-text'}), 'common.fast_account')

    @mock.patch('accounts.prototypes.AccountPrototype.is_ban_forum', True)
    def test_banned(self):
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': self.phrase_type,
                                                                                          'phrase_subtype': self.phrase_subtype,
                                                                                          'text': 'created-text'}), 'common.ban_forum')

    def test_success(self):
        self.assertEqual(PhraseCandidate.objects.all().count(), 0)
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': self.phrase_type,
                                                                                       'phrase_subtype': self.phrase_subtype,
                                                                                       'text': 'created-text'}))
        self.assertEqual(PhraseCandidate.objects.all().count(), 1)

        phrase = PhraseCandidatePrototype(PhraseCandidate.objects.all()[0])

        self.assertEqual(phrase.text, 'created-text')
        self.assertEqual(phrase.author_id, self.account_1.id)
        self.assertEqual(phrase.type, self.phrase_type)
        self.assertEqual(phrase.type_name, self.phrases_modules['modules'][self.phrase_type]['name'])
        self.assertEqual(phrase.subtype, self.phrase_subtype)
        self.assertEqual(phrase.subtype_name, self.phrase_data['name'])


    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {}), 'phrase_candidates.create.form_errors')
        self.assertEqual(PhraseCandidate.objects.all().count(), 0)

    def test_wrong_module(self):
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': 'bla-bla',
                                                                                          'phrase_subtype': self.phrase_subtype,
                                                                                          'text': 'created-text'}), 'phrase_candidates.create.type_not_exist')
        self.assertEqual(PhraseCandidate.objects.all().count(), 0)

    def test_wrong_subtype(self):
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:create'), {'phrase_type': self.phrase_type,
                                                                                          'phrase_subtype': 'bla-bla',
                                                                                          'text': 'created-text'}), 'phrase_candidates.create.type_not_exist')
        self.assertEqual(PhraseCandidate.objects.all().count(), 0)


class EditRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(EditRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_1@test.com')

        self.moderators_group.account_set.add(self.account_1._model)

    def test_login_required(self):
        self.request_logout()
        self.check_html_ok(self.request_ajax_html(url('game:phrase-candidates:edit', self.phrase_1.id)), texts=['common.login_required'])

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_html_ok(self.request_ajax_html(url('game:phrase-candidates:edit', self.phrase_1.id)), texts=['common.fast_account'])

    def test_success(self):
        texts = [(self.phrase_1.text, 1),
                 (PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.IN_QUEUE], 1),
                 (PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.APPROVED], 1),
                 (PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.REMOVED], 1),
                 (PHRASE_CANDIDATE_STATE._ID_TO_TEXT[PHRASE_CANDIDATE_STATE.ADDED], 0),]
        texts.extend(('"%s"' % choice_id, 1) for choice_id in SUBTYPE_CHOICES_IDS)
        self.check_html_ok(self.client.get(reverse('game:phrase-candidates:edit', args=[self.phrase_1.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest'), texts=texts)

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.request_ajax_json(reverse('game:phrase-candidates:edit', args=[self.phrase_1.id])),
                              'phrase_candidates.moderate_rights_required')


class UpdateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(UpdateRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_3@test.com')

        self.moderators_group.account_set.add(self.account_3._model)

    def test_login_required(self):
        self.request_logout()
        new_type, new_subtype = self.get_another_phrase_subtype(self.phrase_1)
        self.check_ajax_error(self.client.post(url('game:phrase-candidates:update', self.phrase_1.id), {'state': PHRASE_CANDIDATE_STATE.APPROVED,
                                                                                                        'text': u'new text',
                                                                                                        'subtype': new_subtype}), 'common.login_required')

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        new_type, new_subtype = self.get_another_phrase_subtype(self.phrase_1)
        self.check_ajax_error(self.client.post(url('game:phrase-candidates:update', self.phrase_1.id), {'state': PHRASE_CANDIDATE_STATE.APPROVED,
                                                                                                        'text': u'new text',
                                                                                                        'subtype': new_subtype}), 'common.fast_account')

    def test_success(self):
        new_type, new_subtype = self.get_another_phrase_subtype(self.phrase_1)
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:update', args=[self.phrase_1.id]), {'state': PHRASE_CANDIDATE_STATE.APPROVED,
                                                                                                                'text': u'new text',
                                                                                                                'subtype': new_subtype}))
        phrase = PhraseCandidatePrototype.get_by_id(self.phrase_1.id)
        self.assertEqual(phrase.text, u'new text')
        self.assertTrue(phrase.state.is_approved)
        self.assertEqual(phrase.subtype, new_subtype)
        self.assertEqual(phrase.type, new_type)
        self.assertEqual(phrase.moderator_id, self.account_3.id)

    def test_success_unknown_type(self):
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:update', args=[self.phrase_1.id]), {'state': PHRASE_CANDIDATE_STATE.APPROVED,
                                                                                                                'text': u'new text',
                                                                                                                'subtype': UNKNOWN_TYPE_ID}))
        phrase = PhraseCandidatePrototype.get_by_id(self.phrase_1.id)
        self.assertEqual(phrase.subtype, self.phrase_1.subtype)
        self.assertEqual(phrase.type, self.phrase_1.type)

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error( self.client.post(reverse('game:phrase-candidates:update', args=[self.phrase_1.id]), {'state': PHRASE_CANDIDATE_STATE.APPROVED,
                                                                                                                    'text': u'new text'}),
                               'phrase_candidates.moderate_rights_required')

    def test_added_state_restrictions(self):
        self.check_ajax_error( self.client.post(reverse('game:phrase-candidates:update', args=[self.phrase_1.id]), {'state': PHRASE_CANDIDATE_STATE.ADDED,
                                                                                                                    'text': u'new text'}),
                               'phrase_candidates.update.form_errors')


    def test_form_errors(self):
        self.check_ajax_error( self.client.post(reverse('game:phrase-candidates:update', args=[self.phrase_1.id]), {}),
                               'phrase_candidates.update.form_errors')



class RemoveRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(RemoveRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_1@test.com')

        self.moderators_group.account_set.add(self.account_1._model)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:remove', args=[self.phrase_1.id])), 'common.login_required')

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:remove', args=[self.phrase_1.id])), 'common.fast_account')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:remove', args=[self.phrase_1.id])),
                              'phrase_candidates.moderate_rights_required')


    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:remove', args=[self.phrase_1.id])))
        phrase = PhraseCandidatePrototype.get_by_id(self.phrase_1.id)
        self.assertTrue(phrase.state.is_removed)
        self.assertEqual(phrase.moderator_id, self.account_1.id)




class ApproveRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(ApproveRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_1@test.com')

        self.moderators_group.account_set.add(self.account_1._model)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:approve', args=[self.phrase_1.id])), 'common.login_required')

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:approve', args=[self.phrase_1.id])), 'common.fast_account')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:approve', args=[self.phrase_1.id])),
                              'phrase_candidates.moderate_rights_required')


    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:approve', args=[self.phrase_1.id])))
        phrase = PhraseCandidatePrototype.get_by_id(self.phrase_1.id)
        self.assertTrue(phrase.state.is_approved)
        self.assertEqual(phrase.moderator_id, self.account_1.id)



class AddRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(AddRequestsTests, self).setUp()

        self.phrase_1 = self.create_phrase(id_=3, author=self.account_2)

        self.request_login('test_user_1@test.com')

        self.developers_group.account_set.add(self.account_1._model)

    def test_login_required(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:add', args=[self.phrase_1.id])), 'common.login_required')

    def test_account_is_fast(self):
        self.request_login('test_user_1@test.com')
        self.account_1.is_fast = True
        self.account_1.save()
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:add', args=[self.phrase_1.id])), 'common.fast_account')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_ajax_error(self.client.post(reverse('game:phrase-candidates:add', args=[self.phrase_1.id])),
                              'phrase_candidates.add_to_game_rights_required')


    def test_success(self):
        self.check_ajax_ok(self.client.post(reverse('game:phrase-candidates:add', args=[self.phrase_1.id])))
        phrase = PhraseCandidatePrototype.get_by_id(self.phrase_1.id)
        self.assertTrue(phrase.state.is_added)
        self.assertEqual(phrase.moderator_id, self.account_1.id)
