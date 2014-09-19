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

from the_tale.linguistics import prototypes
from the_tale.linguistics import relations
from the_tale.linguistics.conf import linguistics_settings


class BaseRequestsTests(TestCase):

    def setUp(self):
        super(BaseRequestsTests, self).setUp()

        create_test_map()

        result, account_id, bundle_id = register_user('test_user1', 'test_user1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)



class IndexRequestsTests(BaseRequestsTests):

    def test_state_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:', state='www')), texts=['linguistics.words.state.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:', state=666)), texts=['linguistics.words.state.not_found'], status_code=404)

    def test_type_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:', type='www')), texts=['linguistics.words.type.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:', type=666)), texts=['linguistics.words.type.not_found'], status_code=404)

    def create_words(self):
        type_1, type_2, type_3 = random.sample(utg_relations.WORD_TYPE.records, 3)
        word_1 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_1, prefix=u'w1-'))
        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_2, prefix=u'w2-'))
        word_3 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(type_3, prefix=u'w3-'))

        word_2.state = relations.WORD_STATE.IN_GAME
        word_2.save()

        return word_1, word_2, word_3

    def test_success(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [word_1.utg_word.normal_form(),
                 word_2.utg_word.normal_form(),
                 word_3.utg_word.normal_form() ]

        self.check_html_ok(self.request_html(url('linguistics:words:')), texts=texts)

    def test_filter_state(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [word_1.utg_word.normal_form(),
                 (word_2.utg_word.normal_form(), 0),
                 word_3.utg_word.normal_form() ]

        self.check_html_ok(self.request_html(url('linguistics:words:', state=relations.WORD_STATE.ON_REVIEW.value)), texts=texts)

    def test_filter_type(self):
        word_1, word_2, word_3 = self.create_words()

        texts = [(word_1.utg_word.normal_form(), 0),
                 (word_2.utg_word.normal_form(), 0),
                 word_3.utg_word.normal_form() ]

        self.check_html_ok(self.request_html(url('linguistics:words:', type=word_3.type.value)), texts=texts)



class NewRequestsTests(BaseRequestsTests):

    def test_type_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:new')), texts=['linguistics.words.type.not_specified'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type='www')), texts=['linguistics.words.type.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=666)), texts=['linguistics.words.type.not_found'], status_code=404)

    def test_parent_errors(self):
        word_type = utg_relations.WORD_TYPE.records[0]
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=word_type.value, parent='xxx')), texts=['linguistics.words.parent.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:new', type=word_type.value, parent=666)), texts=['linguistics.words.parent.not_found'], status_code=404)

    def test_displaying_fields_for_all_forms(self):
        for word_type in utg_relations.WORD_TYPE.records:
            requested_url = url('linguistics:words:new', type=word_type.value)

            texts = [('"field_%d"' % i, 2) for i in xrange(utg_words.Word.get_forms_number(word_type))]
            for static_property, required in word_type.properties.iteritems():
                texts.append(('"field_%s"' % static_property.__name__, 2))

            self.check_html_ok(self.request_html(requested_url), texts=texts)


    def test_displaying_fields_for_all_forms__with_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
            requested_url = url('linguistics:words:new', type=word.type.value, parent=word.id)

            texts = [('"field_%d"' % i, 2) for i in xrange(utg_words.Word.get_forms_number(word_type))]
            texts.extend(word.utg_word.forms)

            for static_property, required in word.type.properties.iteritems():
                texts.append(('"field_%s"' % static_property.__name__, 2))

            self.check_html_ok(self.request_html(requested_url), texts=texts)

    def test_not_equal_types(self):
        for word_type in utg_relations.WORD_TYPE.records:
            wrong_type = random.choice(utg_relations.WORD_TYPE.records)
            while wrong_type == word_type:
                wrong_type = random.choice(utg_relations.WORD_TYPE.records)

            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))

            requested_url = url('linguistics:words:new', type=wrong_type.value, parent=word.id)

            self.check_html_ok(self.request_html(requested_url), texts=['linguistics.words.new.unequal_types'])


    @mock.patch('the_tale.linguistics.prototypes.WordPrototype.has_on_review_copy', lambda self: True)
    def test_has_on_review_copy(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
            requested_url = url('linguistics:words:new', type=word.type.value, parent=word.id)
            self.check_html_ok(self.request_html(requested_url), texts=['linguistics.words.new.has_on_review_copy'])


class CreateRequestsTests(BaseRequestsTests):

    def test_type_errors(self):
        self.check_ajax_error(self.client.post(url('linguistics:words:create')), 'linguistics.words.type.not_specified')
        self.check_ajax_error(self.client.post(url('linguistics:words:create', type='www')), 'linguistics.words.type.wrong_format')
        self.check_ajax_error(self.client.post(url('linguistics:words:create', type=666)), 'linguistics.words.type.not_found')

    def get_post_data(self, word):

        data = {}

        for i, form in enumerate(word.forms):
            data['field_%d' % i] = form

        for static_property, required in word.type.properties.iteritems():
            if word.properties.is_specified(static_property):
                data['field_%s' % static_property.__name__] = word.properties.get(static_property)

        return data

    def test_create_with_all_fields(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type, prefix='w-')
            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_delta(prototypes.WordPrototype._db_count, 1):
                response = self.client.post(requested_url, self.get_post_data(word))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(word, last_prototype.utg_word)


    def test_create__with_on_review_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type)

            parent = prototypes.WordPrototype.create(word)

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                response = self.client.post(requested_url, self.get_post_data(word))

            last_prototype = prototypes.WordPrototype._db_latest()

            self.assertTrue(parent.created_at < last_prototype.created_at)

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(word, last_prototype.utg_word)

    def test_create__with_parent(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type)

            parent = prototypes.WordPrototype.create(word)
            parent.state = relations.WORD_STATE.IN_GAME
            parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value, parent=parent.id)

            with self.check_delta(prototypes.WordPrototype._db_count, 1):
                response = self.client.post(requested_url, self.get_post_data(word))

            self.assertTrue(prototypes.WordPrototype._db_filter(id=parent.id).exists())

            last_prototype = prototypes.WordPrototype._db_latest()

            self.check_ajax_ok(response, data={'next_url': url('linguistics:words:show', last_prototype.id)})

            self.assertEqual(word, last_prototype.utg_word)


    def test_create__parent_not_cpecified(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = utg_words.Word.create_test_word(word_type)

            parent = prototypes.WordPrototype.create(word)
            parent.state = random.choice(relations.WORD_STATE.records)
            parent.save()

            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_delta(prototypes.WordPrototype._db_count, 0):
                self.check_ajax_error(self.client.post(requested_url, self.get_post_data(word)),
                                      'linguistics.words.create.parent_exists')

    def test_form_errors(self):
        for word_type in utg_relations.WORD_TYPE.records:
            requested_url = url('linguistics:words:create', type=word_type.value)

            with self.check_not_changed(prototypes.WordPrototype._db_count):
                self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.form_errors')



    def test_not_equal_types(self):
        for word_type in utg_relations.WORD_TYPE.records:
            wrong_type = random.choice(utg_relations.WORD_TYPE.records)
            while wrong_type == word_type:
                wrong_type = random.choice(utg_relations.WORD_TYPE.records)

            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))

            requested_url = url('linguistics:words:create', type=wrong_type.value, parent=word.id)

            self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.unequal_types')


    @mock.patch('the_tale.linguistics.prototypes.WordPrototype.has_on_review_copy', lambda self: True)
    def test_has_on_review_copy(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
            requested_url = url('linguistics:words:create', type=word.type.value, parent=word.id)
            self.check_ajax_error(self.client.post(requested_url, {}), 'linguistics.words.create.has_on_review_copy')



class ShowRequestsTests(BaseRequestsTests):

    def test_word_errors(self):
        self.check_html_ok(self.request_html(url('linguistics:words:show', 'www')), texts=['linguistics.words.word.wrong_format'])
        self.check_html_ok(self.request_html(url('linguistics:words:show', 666)), texts=['linguistics.words.word.not_found'], status_code=404)

    def test_displaying_fields_for_all_forms(self):
        for word_type in utg_relations.WORD_TYPE.records:
            word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-', only_required=True))
            requested_url = url('linguistics:words:show', word.id)

            texts = []
            for property in utg_relations.PROPERTY_TYPE.records:
                if word.utg_word.properties.is_specified(property):
                    texts.append(word.utg_word.properties.get(property).text)

            for form in word.utg_word.forms:
                texts.append(form)

            self.check_html_ok(self.request_html(requested_url), texts=texts)

    def test_displaying_fields_words_with_optional_properties(self):
        word_type = utg_relations.WORD_TYPE.NOUN
        word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(word_type, prefix=u'w-'))
        word.utg_word.properties.update(utg_relations.NUMBER.PLURAL)
        word.save()

        requested_url = url('linguistics:words:show', word.id)

        texts = []
        for form in word.utg_word.forms[:6]:
            texts.append((form, 0))
        for form in word.utg_word.forms[6:]:
            texts.append(form)

        self.check_html_ok(self.request_html(requested_url), texts=texts)


class RemoveRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(RemoveRequestsTests, self).setUp()
        self.word_type = random.choice(utg_relations.WORD_TYPE.records)
        self.word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True))

        result, account_id, bundle_id = register_user('moderator', 'moderator@test.com', '111111')
        self.moderator = AccountPrototype.get_by_id(account_id)

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_word'])
        group.user_set.add(self.moderator._model)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:words:remove', self.word.id)

    def test_word_errors(self):
        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(url('linguistics:words:remove', 'www')), 'linguistics.words.word.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:words:remove', 666)), 'linguistics.words.word.not_found')

    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.WordPrototype._db_count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.moderation_rights')


    def test_remove(self):
        self.request_login(self.moderator.email)

        with self.check_delta(prototypes.WordPrototype._db_count, -1):
            self.check_ajax_ok(self.client.post(self.requested_url))



class InGameRequestsTests(BaseRequestsTests):

    def setUp(self):
        super(InGameRequestsTests, self).setUp()
        self.word_type = random.choice(utg_relations.WORD_TYPE.records)
        self.word = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True))

        result, account_id, bundle_id = register_user('moderator', 'moderator@test.com', '111111')
        self.moderator = AccountPrototype.get_by_id(account_id)

        group = sync_group(linguistics_settings.MODERATOR_GROUP_NAME, ['linguistics.moderate_word'])
        group.user_set.add(self.moderator._model)

        self.request_login(self.account_1.email)

        self.requested_url = url('linguistics:words:in-game', self.word.id)

    def test_word_errors(self):
        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(url('linguistics:words:in-game', 'www')), 'linguistics.words.word.wrong_format')
            self.check_ajax_error(self.client.post(url('linguistics:words:in-game', 666)), 'linguistics.words.word.not_found')

    def test_login_required(self):
        self.request_logout()

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'common.login_required')


    def test_moderation_rights(self):
        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
            self.check_ajax_error(self.client.post(self.requested_url, {}), 'linguistics.words.moderation_rights')


    def test_already_in_game(self):
        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count):
            with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count):
                self.check_ajax_ok(self.client.post(self.requested_url))


    def test_in_game(self):
        self.request_login(self.moderator.email)

        self.assertTrue(self.word.state.is_ON_REVIEW)

        with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count, 1):
            with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count, -1):
                self.check_ajax_ok(self.client.post(self.requested_url))

        self.word.reload()

        self.assertTrue(self.word.state.is_IN_GAME)


    def test_in_game__with_replace(self):
        self.request_login(self.moderator.email)

        self.word.state = relations.WORD_STATE.IN_GAME
        self.word.save()

        word_2 = prototypes.WordPrototype.create(utg_words.Word.create_test_word(self.word_type, prefix=u'w-', only_required=True))

        with self.check_not_changed(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.IN_GAME).count):
            with self.check_delta(prototypes.WordPrototype._db_filter(state=relations.WORD_STATE.ON_REVIEW).count, -1):
                with self.check_delta(prototypes.WordPrototype._db_count, -1):
                    self.check_ajax_ok(self.client.post(url('linguistics:words:in-game', word_2.id)))

        word_2.reload()

        self.assertEqual(prototypes.WordPrototype.get_by_id(self.word.id), None)
        self.assertTrue(word_2.state.is_IN_GAME)
