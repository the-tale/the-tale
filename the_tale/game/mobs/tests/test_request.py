# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase
from the_tale.common.utils.permissions import sync_group

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user, login_page_url

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game import relations as game_relations

from the_tale.game.map.relations import TERRAIN

from the_tale.linguistics.tests import helpers as linguistics_helpers

from ..models import MobRecord
from ..storage import mobs_storage
from ..relations import MOB_RECORD_STATE, MOB_TYPE
from ..prototypes import MobRecordPrototype
from .. import meta_relations



class PostMixin(object):
    def get_create_data(self):
        word = names.generator.get_test_name(name='mob name')

        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update( { 'level': 666,
                'terrains': [TERRAIN.PLANE_GRASS, TERRAIN.HILLS_GRASS],
                'abilities': ['hit', 'strong_hit', 'sidestep'],
                'type': MOB_TYPE.CIVILIZED,
                'archetype': game_relations.ARCHETYPE.NEUTRAL,
                'global_action_probability': 0.5,
                'description': 'mob description'} )

        return data

    def get_update_data(self):
        word = names.generator.get_test_name(name='new name')

        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update( {'level': 667,
                'terrains': [TERRAIN.PLANE_JUNGLE, TERRAIN.HILLS_JUNGLE],
                'abilities': ['hit', 'speedup'],
                'type': MOB_TYPE.BARBARIAN,
                'archetype': game_relations.ARCHETYPE.MAGICAL,
                'global_action_probability': 0.1,
                'description': 'new description'})

        return data

    def get_moderate_data(self, approved=True):
        data = self.get_update_data()
        data['approved'] = approved
        data['uuid'] = 'new_uuid'
        return data



class BaseTestRequests(TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        mobs_storage.sync(force=True)

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.request_login('test_user_1@test.com')

        group_create = sync_group('create mob', ['mobs.create_mobrecord'])
        group_add = sync_group('add mob', ['mobs.moderate_mobrecord'])

        group_create.user_set.add(self.account_2._model)
        group_add.user_set.add(self.account_3._model)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_mobs(self):
        MobRecord.objects.all().delete()
        mobs_storage.clear()
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=(('pgf-no-mobs-message', 1),))

    def test_simple(self):
        texts = ['mob_1', 'mob_2', 'mob_3', ('pgf-create-mob-button', 0), ('pgf-filter-state', 0)]
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=texts)

    def test_create_mob_button(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=[('pgf-create-mob-button', 1)])

    def test_mob_state_filter(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=[('pgf-filter-state', 1)])

        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=[('pgf-filter-state', 1)])

    def test_disabled_mobs(self):
        MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        texts = ['mob_1', 'mob_2', 'mob_3', ('bandit', 0)]
        self.check_html_ok(self.request_html(reverse('guide:mobs:')), texts=texts)

    def test_filter_by_state_no_mobs_message(self):
        self.check_html_ok(self.request_html(reverse('guide:mobs:')+('?state=%d' % MOB_RECORD_STATE.DISABLED.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_state(self):
        texts = ['mob_1', 'mob_2', 'mob_3']
        self.check_html_ok(self.request_html(reverse('guide:mobs:')+('?state=%d' % MOB_RECORD_STATE.ENABLED.value)), texts=texts)

    def test_filter_by_terrain_no_mobs_message(self):
        MobRecord.objects.all().delete()
        mobs_storage.clear()
        MobRecordPrototype.create_random(uuid='bandit', terrains=[TERRAIN.PLANE_GRASS])
        self.check_html_ok(self.request_html(reverse('guide:mobs:')+('?terrain=%d' % TERRAIN.HILLS_GRASS.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_terrain(self):
        MobRecord.objects.all().delete()
        mobs_storage.clear()
        MobRecordPrototype.create_random(uuid='bandit', terrains=[TERRAIN.PLANE_GRASS])
        self.check_html_ok(self.request_html(reverse('guide:mobs:')+('?terrain=%d' % TERRAIN.PLANE_GRASS.value)), texts=['bandit'])

    def test_filter_by_type_no_mobs_message(self):
        MobRecord.objects.all().delete()
        mobs_storage.clear()
        MobRecordPrototype.create_random(uuid='bandit', type=MOB_TYPE.COLDBLOODED)
        self.check_html_ok(self.request_html(url('guide:mobs:', type=MOB_TYPE.CIVILIZED.value)), texts=(('pgf-no-mobs-message', 1),))

    def test_filter_by_type(self):
        MobRecord.objects.all().delete()
        mobs_storage.clear()
        MobRecordPrototype.create_random(uuid='bandit', type=MOB_TYPE.COLDBLOODED)
        self.check_html_ok(self.request_html(url('guide:mobs:', type=MOB_TYPE.COLDBLOODED.value)), texts=['bandit'])


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:mobs:new')
        self.check_redirect(request_url, login_page_url(request_url))

    def test_create_rights(self):
        self.check_html_ok(self.request_html(reverse('game:mobs:new')), texts=[('mobs.create_mob_rights_required', 1),
                                                                             ('pgf-new-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:mobs:new')), texts=[('pgf-new-mob-form', 2)])


class TestCreateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestCreateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:mobs:create'), self.get_create_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:mobs:create'), self.get_create_data()), 'mobs.create_mob_rights_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:mobs:create'), {}), 'mobs.create.form_errors')

    def test_simple(self):
        self.assertEqual(MobRecord.objects.count(), 3)

        response = self.client.post(reverse('game:mobs:create'), self.get_create_data())

        self.assertEqual(MobRecord.objects.count(), 4)
        mob_record = MobRecordPrototype(MobRecord.objects.all().order_by('-created_at')[0])

        self.check_ajax_ok(response, data={'next_url': reverse('guide:mobs:show', args=[mob_record.id])})

        self.assertEqual(mob_record.name, u'mob name-нс,ед,им')
        self.assertEqual(mob_record.level, 666)
        self.assertEqual(mob_record.terrains, frozenset([TERRAIN.PLANE_GRASS, TERRAIN.HILLS_GRASS]))
        self.assertEqual(mob_record.abilities, frozenset(['hit', 'strong_hit', 'sidestep']) )
        self.assertEqual(mob_record.description, 'mob description')
        self.assertTrue(mob_record.state.is_DISABLED)
        self.assertTrue(mob_record.type.is_CIVILIZED)
        self.assertTrue(mob_record.archetype.is_NEUTRAL)
        self.assertEqual(mob_record.global_action_probability, 0.5)
        self.assertTrue(mob_record.editor_id, self.account_2.id)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

    def test_wrong_mob_id(self):
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=['adsd'])), texts=[('mobs.mob.wrong_format', 1)])

    def test_no_mob(self):
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[666])), texts=[('mobs.mob.not_found', 1)], status_code=404)

    def test_disabled_mob_declined(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[('mobs.mob_disabled', 1)], status_code=404)

    def test_disabled_mob_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[mob.name.capitalize()])

    def test_disabled_mob_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[mob.name.capitalize()])

    def test_simple(self):
        mob = MobRecordPrototype(MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[(mob.name.capitalize(), 5),
                                                                                              ('pgf-no-description', 0),
                                                                                              ('pgf-moderate-button', 0),
                                                                                              ('pgf-edit-button', 0),
                                                                                              'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        mob = MobRecordPrototype(MobRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Mob.create_from_object(mob))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Mob.create_from_object(mob))

        self.check_html_ok(self.request_html(url('guide:mobs:show', mob.id)), texts=[('pgf-no-folclor', 0),
                                                                                     'folclor-1-caption',
                                                                                     'folclor-2-caption'])


    def test_no_description(self):
        mob = mobs_storage.all()[0]
        mob.description = ''
        mob.save()
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-no-description', 1)])

    def test_edit_button(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        mob = MobRecordPrototype(MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-moderate-button', 0),
                                                                                              ('pgf-edit-button', 1)])

    def test_moderate_button(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        mob = MobRecordPrototype(MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:mobs:show', args=[mob.id])), texts=[('pgf-moderate-button', 1),
                                                                                              ('pgf-edit-button', 0)])

class TestInfoRequests(BaseTestRequests):

    def setUp(self):
        super(TestInfoRequests, self).setUp()

    def test_wrong_mob_id(self):
        self.check_html_ok(self.request_html(url('guide:mobs:info', 'adsd')), texts=[('mobs.mob.wrong_format', 1)])

    def test_no_mob(self):
        self.check_html_ok(self.request_html(url('guide:mobs:info', 666)), texts=[('mobs.mob.not_found', 1)], status_code=404)

    def test_disabled_mob_declined(self):
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[('mobs.mob_disabled', 1)], status_code=404)

    def test_disabled_mob_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[mob.name.capitalize()])

    def test_disabled_mob_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        mob = MobRecordPrototype.create_random(uuid='bandit', state=MOB_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[mob.name.capitalize()])

    def test_simple(self):
        mob = MobRecordPrototype(MobRecord.objects.all()[0])
        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[(mob.name.capitalize(), 1),
                                                                                   ('pgf-no-description', 0),
                                                                                   ('pgf-moderate-button', 0),
                                                                                   ('pgf-edit-button', 0),
                                                                                   'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        mob = MobRecordPrototype(MobRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Mob.create_from_object(mob))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Mob.create_from_object(mob))

        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[('pgf-no-folclor', 0),
                                                                                     'folclor-1-caption',
                                                                                     'folclor-2-caption'])


    def test_no_description(self):
        mob = mobs_storage.all()[0]
        mob.description = ''
        mob.save()
        self.check_html_ok(self.request_html(url('guide:mobs:info', mob.id)), texts=[('pgf-no-description', 1)])


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.mob = mobs_storage.all()[0]
        self.mob.state = MOB_RECORD_STATE.DISABLED
        self.mob.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:mobs:edit', args=[self.mob.id])
        self.check_redirect(request_url, login_page_url(request_url))

    def test_enabled_state(self):
        self.mob.state = MOB_RECORD_STATE.ENABLED
        self.mob.save()
        self.check_html_ok(self.request_html(reverse('game:mobs:edit', args=[self.mob.id])), texts=[('mobs.disabled_state_required', 1),
                                                                                                  ('pgf-edit-mob-form', 0)])

    def test_create_rights(self):
        self.check_html_ok(self.request_html(reverse('game:mobs:edit', args=[self.mob.id])), texts=[('mobs.create_mob_rights_required', 1),
                                                                                                  ('pgf-edit-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:mobs:edit', args=[self.mob.id])), texts=[('pgf-edit-mob-form', 2),
                                                                                                  self.mob.name,
                                                                                                  (self.mob.description, 1) ])



class TestUpdateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.check_ajax_ok(self.client.post(reverse('game:mobs:create'), self.get_create_data()))
        self.mob = MobRecordPrototype(MobRecord.objects.all().order_by('-created_at')[0])


    def check_mob(self, mob, data):
        self.assertEqual(mob.name, data['name_0'])
        self.assertEqual(mob.level, data['level'])
        self.assertEqual(mob.terrains, frozenset(data['terrains']) )
        self.assertEqual(mob.abilities, frozenset(data['abilities']) )
        self.assertEqual(mob.description, data['description'])
        self.assertTrue(mob.state.is_DISABLED)
        self.assertTrue(mob.type, data['type'])
        self.assertTrue(mob.archetype, data['archetype'])
        self.assertTrue(mob.global_action_probability, data['global_action_probability'])
        self.assertTrue(mob.editor_id, self.account_2.id)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data()), 'mobs.create_mob_rights_required')
        self.check_mob(MobRecordPrototype.get_by_id(self.mob.id), self.get_create_data())

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:mobs:update', args=[self.mob.id]), {}), 'mobs.update.form_errors')
        self.check_mob(MobRecordPrototype.get_by_id(self.mob.id), self.get_create_data())

    def test_simple(self):
        response = self.client.post(reverse('game:mobs:update', args=[self.mob.id]), self.get_update_data())

        mob_record = MobRecordPrototype.get_by_id(self.mob.id)

        self.check_ajax_ok(response, data={'next_url': reverse('guide:mobs:show', args=[mob_record.id])})

        self.check_mob(mob_record, self.get_update_data())


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        self.mob = mobs_storage.all()[0]
        self.mob.state = MOB_RECORD_STATE.DISABLED
        self.mob.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:mobs:moderate', args=[self.mob.id])
        self.check_redirect(request_url, login_page_url(request_url))

    def test_moderate_rights(self):
        self.check_html_ok(self.request_html(reverse('game:mobs:moderate', args=[self.mob.id])), texts=[('mobs.moderate_mob_rights_required', 1),
                                                                                                      ('pgf-moderate-mob-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('game:mobs:moderate', args=[self.mob.id])), texts=[('pgf-moderate-mob-form', 2),
                                                                                                       self.mob.name,
                                                                                                      (self.mob.description, 1) ])


class TestModerateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.check_ajax_ok(self.client.post(reverse('game:mobs:create'), self.get_create_data()))
        self.mob = MobRecordPrototype(MobRecord.objects.all().order_by('-created_at')[0])

        self.name = names.generator.get_test_name(name='new name')

        self.request_logout()
        self.request_login('test_user_3@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data()), 'common.login_required')

    def test_moderate_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data()), 'mobs.moderate_mob_rights_required')
        self.assertEqual(MobRecordPrototype.get_by_id(self.mob.id).uuid, self.mob.uuid)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:mobs:moderate', args=[self.mob.id]), {}), 'mobs.moderate.form_errors')
        self.assertEqual(MobRecordPrototype.get_by_id(self.mob.id).uuid, self.mob.uuid)

    def test_simple(self):
        response = self.client.post(reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data())

        mob_record = MobRecordPrototype.get_by_id(self.mob.id)

        self.check_ajax_ok(response, data={'next_url': reverse('guide:mobs:show', args=[mob_record.id])})

        self.assertEqual(mob_record.uuid, self.mob.uuid)
        self.assertEqual(mob_record.name, u'new name-нс,ед,им')
        self.assertEqual(mob_record.utg_name, self.name)
        self.assertEqual(mob_record.level, 667)
        self.assertEqual(mob_record.terrains, frozenset([TERRAIN.PLANE_JUNGLE, TERRAIN.HILLS_JUNGLE]))
        self.assertEqual(mob_record.abilities, frozenset(['hit', 'speedup']) )
        self.assertEqual(mob_record.description, 'new description')
        self.assertTrue(mob_record.state.is_ENABLED)
        self.assertTrue(mob_record.type.is_BARBARIAN)
        self.assertTrue(mob_record.archetype.is_MAGICAL)
        self.assertTrue(mob_record.editor_id, self.account_3.id)

    def test_simple_not_approved(self):
        self.check_ajax_ok(self.client.post(reverse('game:mobs:moderate', args=[self.mob.id]), self.get_moderate_data(approved=False)))

        mob_record = MobRecordPrototype.get_by_id(self.mob.id)

        self.assertTrue(mob_record.state.is_DISABLED)
