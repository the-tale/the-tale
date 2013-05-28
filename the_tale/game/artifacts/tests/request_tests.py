# coding: utf-8

from django.test import client
from django.core.urlresolvers import reverse

from textgen.words import Noun

from dext.utils import s11n

from common.utils.testcase import TestCase
from common.utils.permissions import sync_group

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user, login_url

from game.logic import create_test_map, DEFAULT_HERO_EQUIPMENT

from game.mobs.storage import mobs_storage

from game.artifacts.models import ArtifactRecord
from game.artifacts.storage import artifacts_storage
from game.artifacts.models import ARTIFACT_RECORD_STATE, ARTIFACT_TYPE, RARITY_TYPE
from game.artifacts.prototypes import ArtifactRecordPrototype


class BaseTestRequests(TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        artifacts_storage.sync(force=True)

        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')
        self.account1 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_3', 'test_user_3@test.com', '111111')
        self.account_3 = AccountPrototype.get_by_id(account_id)

        self.client = client.Client()

        self.request_login('test_user_1@test.com')

        group_create = sync_group('create artifact', ['artifacts.create_artifactrecord'])
        group_add = sync_group('add create_artifact', ['artifacts.moderate_artifactrecord'])

        group_create.account_set.add(self.account_2._model)
        group_add.account_set.add(self.account_3._model)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_artifacts(self):
        ArtifactRecord.objects.all().delete()
        artifacts_storage.clear()
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=(('pgf-no-artifacts-message', 1),))

    def test_simple(self):
        texts = ['loot_1', 'loot_2', 'boots_1', ('pgf-create-artifact-button', 0), ('pgf-artifact-state-filter', 0)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=texts)

    def test_create_artifact_button(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-create-artifact-button', 1)])

    def test_artifact_state_filter(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-artifact-state-filter', 1)])

        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=[('pgf-artifact-state-filter', 1)])

    def test_disabled_artifacts(self):
        ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=ARTIFACT_RECORD_STATE.DISABLED)
        texts = ['loot_1', 'loot_2', 'plate_1', ('bandit_loot', 0)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')), texts=texts)

    def test_filter_by_state_no_artifacts_message(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?state=%d' % ARTIFACT_RECORD_STATE.DISABLED)), texts=(('pgf-no-artifacts-message', 1),))

    def test_filter_by_state(self):
        texts = ['loot_1', 'loot_2', 'loot_3']
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?state=%d' % ARTIFACT_RECORD_STATE.ENABLED)), texts=texts)

    def test_filter_by_rarity_no_artifacts_message(self):
        texts = [('loot_1', 0), ('loot_2', 0), ('loot_3', 0), ('pgf-no-artifacts-message', 1)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?rarity=%d' % RARITY_TYPE.EPIC)), texts=texts)

    def test_filter_by_rarity(self):
        ArtifactRecordPrototype.create_random('helmet_2', type_=ARTIFACT_TYPE.HELMET, rarity=RARITY_TYPE.RARE)
        ArtifactRecordPrototype.create_random('plate_2', type_=ARTIFACT_TYPE.PLATE, rarity=RARITY_TYPE.RARE)
        ArtifactRecordPrototype.create_random('boots_2', type_=ARTIFACT_TYPE.BOOTS, rarity=RARITY_TYPE.RARE)

        texts = [('loot_1', 0), ('loot_2', 0), ('loot_3', 0), ('pgf-no-artifacts-message', 0), ('helmet_2', 1), ('plate_2', 1), ('boots_2', 1)]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?rarity=%d' % RARITY_TYPE.RARE)), texts=texts)

    def test_filter_by_type_no_artifacts_message(self):
        texts = [('loot_1', 0), ('plate_1', 0), ('loot_3', 0), ('pgf-no-artifacts-message', 1)]
        texts += [(uuid, 0) for uuid in DEFAULT_HERO_EQUIPMENT._ALL]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?type=%d' % ARTIFACT_TYPE.RING)), texts=texts)

    def test_filter_by_type(self):
        texts = [('loot_1', 1), ('loot_2', 1), ('loot_3', 1), ('pgf-no-artifacts-message', 0), ('helmet_2', 0), ('plate_2', 0), ('boots_2', 0)]
        texts += [(uuid, 0) for uuid in DEFAULT_HERO_EQUIPMENT._ALL]
        self.check_html_ok(self.request_html(reverse('guide:artifacts:')+('?type=%d' % ARTIFACT_TYPE.USELESS)), texts=texts)


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:new')
        self.assertRedirects(self.request_html(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_create_rights(self):
        self.check_html_ok(self.request_html(reverse('game:artifacts:new')), texts=[('artifacts.create_artifact_rights_required', 1),
                                                                                  ('pgf-new-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:artifacts:new')), texts=[('pgf-new-artifact-form', 2)])


class TestCreateRequests(BaseTestRequests):

    def setUp(self):
        super(TestCreateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.mob = mobs_storage.all()[0]

    def get_post_data(self):
        return {'name': 'artifact name',
                'level': 1,
                'rarity': RARITY_TYPE.RARE,
                'type': ARTIFACT_TYPE.RING,
                'description': 'artifact description',
                'mob': self.mob.id}

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), self.get_post_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login('test_user_1@test.com')
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), self.get_post_data()), 'artifacts.create_artifact_rights_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(reverse('game:artifacts:create'), {}), 'artifacts.create.form_errors')

    def test_simple(self):
        old_number = ArtifactRecord.objects.count()

        response = self.client.post(reverse('game:artifacts:create'), self.get_post_data())

        self.assertEqual(ArtifactRecord.objects.count(), old_number + 1)
        artifact_record = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.check_ajax_ok(response, data={'next_url': reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.assertEqual(artifact_record.name, 'artifact name')
        self.assertEqual(artifact_record.level, 1)
        self.assertEqual(artifact_record.rarity, RARITY_TYPE.RARE)
        self.assertEqual(artifact_record.type, ARTIFACT_TYPE.RING)
        self.assertEqual(artifact_record.description, 'artifact description')
        self.assertTrue(artifact_record.state.is_disabled)
        self.assertTrue(artifact_record.editor_id, self.account_2.id)
        self.assertTrue(artifact_record.mob.id, self.mob.id)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

    def test_wrong_artifact_id(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=['adsd'])), texts=[('artifacts.artifact.wrong_format', 1)])

    def test_no_artifact(self):
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[666])), texts=[('artifacts.artifact.not_found', 1)], status_code=404)

    def test_disabled_artifact_declined(self):
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[('artifacts.show.artifact_disabled', 1)], status_code=404)

    def test_disabled_artifact_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login('test_user_2@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_disabled_artifact_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        artifact = ArtifactRecordPrototype.create_random(uuid='bandit_loot', state=ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_simple(self):
        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(reverse('guide:artifacts:show', args=[artifact.id])), texts=[(artifact.name.capitalize(), 4),
                                                                                                        ('pgf-no-description', 0),
                                                                                                        ('pgf-moderate-button', 0),
                                                                                                        ('pgf-edit-button', 0)])

    def test_no_description(self):
        artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
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


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.artifact.state = ARTIFACT_RECORD_STATE.DISABLED
        self.artifact.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:edit', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_enabled_state(self):
        self.artifact.state = ARTIFACT_RECORD_STATE.ENABLED
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
                                                                                                            (self.artifact.name, 2), # +description
                                                                                                            (self.artifact.description, 1) ])



class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.check_ajax_ok(self.client.post(reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.mob = mobs_storage.all()[0]

    def get_create_data(self):
        return {'name': 'artifact name',
                'level': 1,
                'rarity': RARITY_TYPE.RARE,
                'type': ARTIFACT_TYPE.RING,
                'description': 'artifact description'}

    def get_update_data(self):
        return {'name': 'new artifact name',
                'level': 2,
                'rarity': RARITY_TYPE.EPIC,
                'type': ARTIFACT_TYPE.AMULET,
                'description': 'new artifact description',
                'mob': self.mob.id}

    def check_artifact(self, artifact, data):
        self.assertEqual(artifact.name, data['name'])
        self.assertEqual(artifact.level, data['level'])
        self.assertEqual(artifact.rarity, data['rarity'])
        self.assertEqual(artifact.type, data['type'])
        self.assertEqual(artifact.description, data['description'])

        mob = data.get('mob')
        if mob is not None:
            self.assertEqual(artifact.mob.id, mob)
        else:
            self.assertEqual(artifact.mob, None)
        self.assertTrue(artifact.state.is_disabled)
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

        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all()[0])
        self.artifact.state = ARTIFACT_RECORD_STATE.DISABLED
        self.artifact.save()

    def test_unlogined(self):
        self.request_logout()
        request_url = reverse('game:artifacts:moderate', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), login_url(request_url), status_code=302, target_status_code=200)

    def test_moderate_rights(self):
        self.check_html_ok(self.request_html(reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('artifacts.moderate_artifact_rights_required', 1),
                                                                                                                ('pgf-moderate-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login('test_user_3@test.com')
        self.check_html_ok(self.request_html(reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('pgf-moderate-artifact-form', 2),
                                                                                                                (self.artifact.name, 1 + 13), # description+name_forms
                                                                                                                (self.artifact.description, 1) ])


class TestModerateRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_logout()
        self.request_login('test_user_2@test.com')

        self.mob = mobs_storage.all()[0]

        self.check_ajax_ok(self.client.post(reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = ArtifactRecordPrototype(ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.name = Noun(normalized='new name 0',
                         forms=['new name %d' % i for i in xrange( Noun.FORMS_NUMBER)],
                         properties=(u'мр',))

        self.request_logout()
        self.request_login('test_user_3@test.com')

    def get_create_data(self):
        return {'name': 'artifact name',
                'level': 1,
                'rarity': RARITY_TYPE.RARE,
                'type': ARTIFACT_TYPE.RING,
                'description': 'artifact description',
                'mob': self.mob.id}

    def get_moderate_data(self, approved=True):
        return {'name_forms': s11n.to_json(self.name.serialize()),
                'uuid': 'new_uuid',
                'approved': approved,
                'level': 2,
                'rarity': RARITY_TYPE.EPIC,
                'type': ARTIFACT_TYPE.AMULET,
                'description': 'new artifact description'}

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

        self.assertEqual(artifact_record.uuid, 'new_uuid')
        self.assertEqual(artifact_record.name, 'new name 0')
        self.assertEqual(artifact_record.name_forms, self.name)
        self.assertEqual(artifact_record.level, 2)
        self.assertEqual(artifact_record.description, 'new artifact description')
        self.assertTrue(artifact_record.state.is_enabled)
        self.assertTrue(artifact_record.editor_id, self.account_3.id)
        self.assertEqual(artifact_record.mob, None)

    def test_simple_not_approved(self):
        self.check_ajax_ok(self.client.post(reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data(approved=False)))

        artifact_record = ArtifactRecordPrototype.get_by_id(self.artifact.id)

        self.assertTrue(artifact_record.state.is_disabled)
