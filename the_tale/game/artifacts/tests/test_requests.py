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

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.heroes import relations as heroes_relations

from ..models import ArtifactRecord
from ..storage import artifacts_storage
from .. import relations
from ..prototypes import ArtifactRecordPrototype
from .. import meta_relations

from the_tale.linguistics.tests import helpers as linguistics_helpers


class PostMixin(object):
    def get_create_data(self, mob=None):
        word = names.generator.get_test_name(name='artifact')
        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({
                'level': 1,
                'type': relations.ARTIFACT_TYPE.RING,
                'power_type': relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                'rare_effect': relations.ARTIFACT_EFFECT.POISON,
                'epic_effect': relations.ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE,
                'special_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
                'description': 'artifact description',
                'mob':  u'' if mob is None else mob.id})

        return data

    def get_moderate_data(self, approved=True):
        data = self.get_update_data()
        data['approved'] = approved
        data['uuid'] = 'new_uuid'
        return data

    def get_update_data(self, mob=None):
        word = names.generator.get_test_name(name='new name')
        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({
                'level': 2,
                'type': relations.ARTIFACT_TYPE.AMULET,
                'power_type': relations.ARTIFACT_POWER_TYPE.MAGICAL,
                'rare_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
                'epic_effect': relations.ARTIFACT_EFFECT.POISON,
                'special_effect': relations.ARTIFACT_EFFECT.CHILD_GIFT,
                'description': 'new artifact description',
                'mob': u'' if mob is None else mob.id})

        return data



class BaseTestRequests(TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        artifacts_storage.sync(force=True)

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account_1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.request_login('test_user_1@test.com')

        group_create = sync_group('create artifact', ['artifacts.create_artifactrecord'])
        group_add = sync_group('add create_artifact', ['artifacts.moderate_artifactrecord'])

        group_create.user_set.add(self.account_2._model)
        group_add.user_set.add(self.account_3._model)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_artifacts(self):
        ArtifactRecord.objects.all().delete()
        artifacts_storage.clear()
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=(('pgf-no-artifacts-message', 1),))

    def test_simple(self):
        texts = ['loot_1', 'loot_2', 'boots_1', ('pgf-create-artifact-button', 0), ('pgf-filter-state', 0)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=texts)

    def test_create_artifact_button(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-create-artifact-button', 1)])

    def test_artifact_state_filter(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-filter-state', 1)])

        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-filter-state', 1)])

    def test_disabled_artifacts(self):
        ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        texts = ['loot_1', 'loot_2', 'plate_1', ('bandit_loot', 0)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=texts)

    def test_filter_by_state_no_artifacts_message(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?state=%d' % relations.ARTIFACT_RECORD_STATE.DISABLED.value)), texts=(('pgf-no-artifacts-message', 1),))

    def test_filter_by_state(self):
        texts = ['loot_1', 'loot_2', 'loot_3']
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?state=%d' % relations.ARTIFACT_RECORD_STATE.ENABLED.value)), texts=texts)

    def test_filter_by_type_no_artifacts_message(self):
        texts = [('loot_1', 0), ('plate_1', 0), ('loot_3', 0), ('pgf-no-artifacts-message', 1)]
        texts += [(uid, 0) for uid in heroes_relations.EQUIPMENT_SLOT.default_uids()]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?type=%d' % relations.ARTIFACT_TYPE.RING.value)), texts=texts)

    def test_filter_by_type(self):
        texts = [('loot_1', 1), ('loot_2', 1), ('loot_3', 1), ('pgf-no-artifacts-message', 0), ('helmet_2', 0), ('plate_2', 0), ('boots_2', 0)]
        texts += [(uid, 0) for uid in heroes_relations.EQUIPMENT_SLOT.default_uids() ]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?type=%d' % relations.ARTIFACT_TYPE.USELESS.value)), texts=texts)


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:new')
        self.assertRedirects(self.request_html(request_url), login_page_url(request_url), status_code=302, target_status_code=200)

    def test_create_rights(self):
        self.check_html_ok(self.request_html(reverse('game:artifacts:new')), texts=[('artifacts.create_artifact_rights_required', 1),
                                                                                  ('pgf-new-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:artifacts:new')), texts=[('pgf-new-artifact-form', 2)])


class TestCreateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestCreateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.mob = mobs_storage.all()[0]

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), self.get_create_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), self.get_create_data()), 'artifacts.create_artifact_rights_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), {}), 'artifacts.create.form_errors')

    def test_simple(self):

        with self.check_delta(ArtifactRecordPrototype._db_count, 1):
            response = self.client.post(reverse('game:artifacts:create'), self.get_create_data())

        artifact_record = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.check_ajax_ok(response, data={'next_url': reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.assertEqual(artifact_record.name, u'artifact-нс,ед,им')
        self.assertEqual(artifact_record.level, 1)
        self.assertTrue(artifact_record.type.is_RING)
        self.assertEqual(artifact_record.description, 'artifact description')
        self.assertTrue(artifact_record.state.is_DISABLED)
        self.assertTrue(artifact_record.rare_effect.is_POISON)
        self.assertTrue(artifact_record.epic_effect.is_GREAT_PHYSICAL_DAMAGE)
        self.assertEqual(artifact_record.editor_id, self.account_2.id)
        self.assertEqual(artifact_record.mob, None)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

    def test_wrong_artifact_id(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=['adsd'])), texts=[('artifacts.artifact.wrong_format', 1)])

    def test_no_artifact(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[666])), texts=[('artifacts.artifact.not_found', 1)], status_code=404)

    def test_disabled_artifact_declined(self):
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('artifacts.artifact_disabled', 1)], status_code=404)

    def test_disabled_artifact_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_disabled_artifact_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_simple(self):
        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[(artifact.name.capitalize(), 5),
                                                                                                        ('pgf-no-description', 0),
                                                                                                        ('pgf-moderate-button', 0),
                                                                                                        ('pgf-edit-button', 0),
                                                                                                        'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Artifact.create_from_object(artifact))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Artifact.create_from_object(artifact))

        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-no-folclor', 0),
                                                                                                          'folclor-1-caption',
                                                                                                          'folclor-2-caption'])

    def test_no_description(self):
        artifact = artifacts_storage.all()[0]
        artifact.description = ''
        artifact.save()
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-no-description', 1)])

    def test_edit_button(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-moderate-button', 0),
                                                                                                        ('pgf-edit-button', 1)])

    def test_moderate_button(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-moderate-button', 1),
                                                                                                        ('pgf-edit-button', 0)])

class TestInfoRequests(BaseTestRequests):

    def setUp(self):
        super(TestInfoRequests, self).setUp()

    def test_wrong_artifact_id(self):
        self.check_html_ok(self.request_html(url('guide:artifacts:info', 'adsd')), texts=[('artifacts.artifact.wrong_format', 1)])

    def test_no_artifact(self):
        self.check_html_ok(self.request_html(url('guide:artifacts:info', 666)), texts=[('artifacts.artifact.not_found', 1)], status_code=404)

    def test_disabled_artifact_disabled(self):
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[('artifacts.artifact_disabled', 1)], status_code=404)

    def test_disabled_artifact_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[artifact.name.capitalize()])

    def test_disabled_artifact_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[artifact.name.capitalize()])

    def test_simple(self):
        artifact = ArtifactRecordPrototype._db_get_object(0)
        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[(artifact.name.capitalize(), 1),
                                                                                               ('pgf-no-description', 0),
                                                                                               ('pgf-moderate-button', 0),
                                                                                               ('pgf-edit-button', 0),
                                                                                               'pgf-no-folclor'])

    def test_folclor(self):
        from the_tale.blogs.tests import helpers as blogs_helpers

        blogs_helpers.prepair_forum()

        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Artifact.create_from_object(artifact))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Artifact.create_from_object(artifact))

        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[('pgf-no-folclor', 0),
                                                                                               'folclor-1-caption',
                                                                                               'folclor-2-caption'])


    def test_no_description(self):
        artifact = artifacts_storage.all()[0]
        artifact.description = ''
        artifact.save()
        self.check_html_ok(self.request_html(url('guide:artifacts:info', artifact.id)), texts=[('pgf-no-description', 1)])



class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.artifact = artifacts_storage.all()[0]
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.DISABLED
        self.artifact.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:edit', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), login_page_url(request_url), status_code=302, target_status_code=200)

    def test_enabled_state(self):
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.ENABLED
        self.artifact.save()
        self.check_html_ok(self.request_html(reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('artifacts.disabled_state_required', 1),
                                                                                                            ('pgf-edit-artifact-form', 0)])

    def test_create_rights(self):
        self.check_html_ok(self.request_html(reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('artifacts.create_artifact_rights_required', 1),
                                                                                                            ('pgf-edit-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('pgf-edit-artifact-form', 2),
                                                                                                            self.artifact.name,
                                                                                                            (self.artifact.description, 1) ])



class TestUpdateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.check_ajax_ok(self.client.post(reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.mob = mobs_storage.all()[0]

    def check_artifact(self, artifact, data):
        self.assertEqual(artifact.name, data['name_0'])
        self.assertEqual(artifact.level, data['level'])
        self.assertEqual(artifact.type, data['type'])
        self.assertEqual(artifact.rare_effect, data['rare_effect'])
        self.assertEqual(artifact.epic_effect, data['epic_effect'])
        self.assertEqual(artifact.power_type, data['power_type'])
        self.assertEqual(artifact.description, data['description'])

        mob = data.get('mob')
        if mob:
            self.assertEqual(artifact.mob.id, mob)
        else:
            self.assertEqual(artifact.mob, None)
        self.assertTrue(artifact.state.is_DISABLED)
        self.assertTrue(artifact.editor_id, self.account_2.id)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data()), 'artifacts.create_artifact_rights_required')
        self.check_artifact(ArtifactRecordPrototype.get_by_id(self.artifact.id), self.get_create_data())

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:artifacts:update', args=[self.artifact.id]), {}), 'artifacts.update.form_errors')
        self.check_artifact(ArtifactRecordPrototype.get_by_id(self.artifact.id), self.get_create_data())

    def test_simple(self):
        response = self.client.post(reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data())

        artifact_record = ArtifactRecordPrototype.get_by_id(self.artifact.id)

        self.check_ajax_ok(response, data={'next_url': reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.check_artifact(artifact_record, self.get_update_data())


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        self.artifact = artifacts_storage.all()[0]
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.DISABLED
        self.artifact.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:moderate', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), login_page_url(request_url), status_code=302, target_status_code=200)

    def test_moderate_rights(self):
        self.check_html_ok(self.request_html(reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('artifacts.moderate_artifact_rights_required', 1),
                                                                                                                ('pgf-moderate-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('pgf-moderate-artifact-form', 2),
                                                                                                                self.artifact.name,
                                                                                                                (self.artifact.description, 1) ])


class TestModerateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.mob = mobs_storage.all()[0]

        self.check_ajax_ok(self.client.post(reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.name = names.generator.get_test_name(name='new name')

        self.request_logout()
        self.request_login('test_user_3@test.com')

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data()), 'common.login_required')

    def test_moderate_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data()), 'artifacts.moderate_artifact_rights_required')
        self.assertEqual(ArtifactRecordPrototype.get_by_id(self.artifact.id).uuid, self.artifact.uuid)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), {}), 'artifacts.moderate.form_errors')
        self.assertEqual(ArtifactRecordPrototype.get_by_id(self.artifact.id).uuid, self.artifact.uuid)

    def test_simple(self):
        response = self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data())

        artifact_record = ArtifactRecordPrototype.get_by_id(self.artifact.id)

        self.check_ajax_ok(response, data={'next_url': reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.assertEqual(artifact_record.name, u'new name-нс,ед,им')
        self.assertEqual(artifact_record.utg_name, self.name)
        self.assertEqual(artifact_record.level, 2)
        self.assertEqual(artifact_record.description, 'new artifact description')
        self.assertTrue(artifact_record.state.is_ENABLED)
        self.assertTrue(artifact_record.type.is_AMULET)
        self.assertTrue(artifact_record.rare_effect.is_NO_EFFECT)
        self.assertTrue(artifact_record.epic_effect.is_POISON)
        self.assertTrue(artifact_record.power_type.is_MAGICAL)
        self.assertTrue(artifact_record.editor_id, self.account_3.id)
        self.assertEqual(artifact_record.mob, None)

    def test_simple_not_approved(self):
        self.check_ajax_ok(self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data(approved=False)))

        artifact_record = ArtifactRecordPrototype.get_by_id(self.artifact.id)

        self.assertTrue(artifact_record.state.is_DISABLED)
