
import smart_imports

smart_imports.all()


class PostMixin(object):
    def get_create_data(self, mob=None):
        word = game_names.generator().get_test_name(name='artifact')
        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({
            'level': 1,
            'type': relations.ARTIFACT_TYPE.RING,
            'power_type': relations.ARTIFACT_POWER_TYPE.NEUTRAL,
            'rare_effect': relations.ARTIFACT_EFFECT.POISON,
            'epic_effect': relations.ARTIFACT_EFFECT.GREAT_PHYSICAL_DAMAGE,
            'special_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
            'weapon_type': tt_artifacts_relations.WEAPON_TYPE.TYPE_1,
            'material': tt_artifacts_relations.MATERIAL.MATERIAL_3,
            'description': 'artifact description',
            'mob': '' if mob is None else mob.id})

        return data

    def get_moderate_data(self, approved=True):
        data = self.get_update_data()
        data['approved'] = approved
        data['uuid'] = 'new_uuid'
        return data

    def get_update_data(self, mob=None):
        word = game_names.generator().get_test_name(name='new name')
        data = linguistics_helpers.get_word_post_data(word, prefix='name')

        data.update({
            'level': 2,
            'type': relations.ARTIFACT_TYPE.AMULET,
            'power_type': relations.ARTIFACT_POWER_TYPE.MAGICAL,
            'rare_effect': relations.ARTIFACT_EFFECT.NO_EFFECT,
            'epic_effect': relations.ARTIFACT_EFFECT.POISON,
            'special_effect': relations.ARTIFACT_EFFECT.CHILD_GIFT,
            'weapon_type': tt_artifacts_relations.WEAPON_TYPE.TYPE_5,
            'material': tt_artifacts_relations.MATERIAL.MATERIAL_7,
            'description': 'new artifact description',
            'mob': '' if mob is None else mob.id})

        return data


class BaseTestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()
        storage.artifacts.sync(force=True)

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        self.request_login(self.account_1.email)

        group_create = utils_permissions.sync_group('create artifact', ['artifacts.create_artifactrecord'])
        group_add = utils_permissions.sync_group('add create_artifact', ['artifacts.moderate_artifactrecord'])

        group_create.user_set.add(self.account_2._model)
        group_add.user_set.add(self.account_3._model)


class TestIndexRequests(BaseTestRequests):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_no_artifacts(self):
        models.ArtifactRecord.objects.all().delete()
        storage.artifacts.clear()
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=(('pgf-no-artifacts-message', 1),))

    def test_simple(self):
        texts = ['loot_1', 'loot_2', 'boots_1', ('pgf-create-artifact-button', 0), ('pgf-filter-state', 0)]
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=texts)

    def test_create_artifact_button(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=[('pgf-create-artifact-button', 1)])

    def test_artifact_state_filter(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=[('pgf-filter-state', 1)])

        self.request_logout()
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=[('pgf-filter-state', 1)])

    def test_disabled_artifacts(self):
        logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        texts = ['loot_1', 'loot_2', 'plate_1', ('bandit_loot', 0)]
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:')), texts=texts)

    def test_filter_by_state_no_artifacts_message(self):
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:') + ('?state=%d' % relations.ARTIFACT_RECORD_STATE.DISABLED.value)), texts=(('pgf-no-artifacts-message', 1),))

    def test_filter_by_state(self):
        texts = ['loot_1', 'loot_2', 'loot_3']
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:') + ('?state=%d' % relations.ARTIFACT_RECORD_STATE.ENABLED.value)), texts=texts)

    def test_filter_by_type_no_artifacts_message(self):
        texts = [('loot_1', 0), ('plate_1', 0), ('loot_3', 0), ('pgf-no-artifacts-message', 1)]
        texts += [(uid, 0) for uid in heroes_relations.EQUIPMENT_SLOT.default_uids()]
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:') + ('?type=%d' % relations.ARTIFACT_TYPE.RING.value)), texts=texts)

    def test_filter_by_type(self):
        texts = [('loot_1', 1), ('loot_2', 1), ('loot_3', 1), ('pgf-no-artifacts-message', 0), ('helmet_2', 0), ('plate_2', 0), ('boots_2', 0)]
        texts += [(uid, 0) for uid in heroes_relations.EQUIPMENT_SLOT.default_uids()]
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:') + ('?type=%d' % relations.ARTIFACT_TYPE.USELESS.value)), texts=texts)


class TestNewRequests(BaseTestRequests):

    def setUp(self):
        super(TestNewRequests, self).setUp()

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:artifacts:new')
        self.assertRedirects(self.request_html(request_url), accounts_logic.login_page_url(request_url), status_code=302, target_status_code=200)

    def test_create_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:new')), texts=[('artifacts.create_artifact_rights_required', 1),
                                                                                           ('pgf-new-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:new')), texts=[('pgf-new-artifact-form', 2)])


class TestCreateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestCreateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

        self.mob = mobs_storage.mobs.all()[0]

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:create'), self.get_create_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:create'), self.get_create_data()), 'artifacts.create_artifact_rights_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:create'), {}), 'artifacts.create.form_errors')

    def test_simple(self):

        with self.check_delta(models.ArtifactRecord.objects.count, 1):
            response = self.client.post(django_reverse('game:artifacts:create'), self.get_create_data())

        artifact_record = logic.construct_from_model(models.ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.assertEqual(artifact_record.name, 'artifact-нс,ед,им')
        self.assertEqual(artifact_record.level, 1)
        self.assertTrue(artifact_record.type.is_RING)
        self.assertEqual(artifact_record.description, 'artifact description')
        self.assertTrue(artifact_record.state.is_DISABLED)
        self.assertTrue(artifact_record.rare_effect.is_POISON)
        self.assertTrue(artifact_record.epic_effect.is_GREAT_PHYSICAL_DAMAGE)
        self.assertTrue(artifact_record.weapon_type.is_TYPE_1)
        self.assertTrue(artifact_record.material.is_MATERIAL_3)
        self.assertEqual(artifact_record.editor_id, self.account_2.id)
        self.assertEqual(artifact_record.mob, None)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

    def test_wrong_artifact_id(self):
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=['adsd'])), texts=[('artifacts.artifact.wrong_format', 1)])

    def test_no_artifact(self):
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[666])), texts=[('artifacts.artifact.not_found', 1)], status_code=404)

    def test_disabled_artifact_declined(self):
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[('artifacts.artifact_disabled', 1)], status_code=404)

    def test_disabled_artifact_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_disabled_artifact_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[artifact.name.capitalize()])

    def test_simple(self):
        artifact = logic.construct_from_model(models.ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[(artifact.name.capitalize(), 4),
                                                                                                                 ('pgf-no-description', 0),
                                                                                                                 ('pgf-moderate-button', 0),
                                                                                                                 ('pgf-edit-button', 0),
                                                                                                                 'pgf-no-folclor'])

    def test_folclor(self):
        blogs_helpers.prepair_forum()

        artifact = logic.construct_from_model(models.ArtifactRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Artifact.create_from_object(artifact))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Artifact.create_from_object(artifact))

        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-no-folclor', 0),
                                                                                                                 'folclor-1-caption',
                                                                                                                 'folclor-2-caption'])

    def test_no_description(self):
        artifact = storage.artifacts.all()[0]
        artifact.description = ''
        logic.save_artifact_record(artifact)
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-no-description', 1)])

    def test_edit_button(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        artifact = logic.construct_from_model(models.ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-moderate-button', 0),
                                                                                                                 ('pgf-edit-button', 1)])

    def test_moderate_button(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        artifact = logic.construct_from_model(models.ArtifactRecord.objects.all()[0])
        self.check_html_ok(self.request_html(django_reverse('guide:artifacts:show', args=[artifact.id])), texts=[('pgf-moderate-button', 1),
                                                                                                                 ('pgf-edit-button', 0)])


class TestInfoRequests(BaseTestRequests):

    def setUp(self):
        super(TestInfoRequests, self).setUp()

    def test_wrong_artifact_id(self):
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', 'adsd')), texts=[('artifacts.artifact.wrong_format', 1)])

    def test_no_artifact(self):
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', 666)), texts=[('artifacts.artifact.not_found', 1)], status_code=404)

    def test_disabled_artifact_disabled(self):
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[('artifacts.artifact_disabled', 1)], status_code=404)

    def test_disabled_artifact_accepted_for_create_rights(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[artifact.name.capitalize()])

    def test_disabled_artifact_accepted_for_add_rights(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        artifact = logic.create_random_artifact_record(uuid='bandit_loot', state=relations.ARTIFACT_RECORD_STATE.DISABLED)
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[artifact.name.capitalize()])

    def test_simple(self):
        artifact = models.ArtifactRecord.objects.all()[0]
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[(artifact.name.capitalize(), 1),
                                                                                                         ('pgf-no-description', 0),
                                                                                                         ('pgf-moderate-button', 0),
                                                                                                         ('pgf-edit-button', 0),
                                                                                                         'pgf-no-folclor'])

    def test_folclor(self):
        blogs_helpers.prepair_forum()

        artifact = logic.construct_from_model(models.ArtifactRecord.objects.all()[0])

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Artifact.create_from_object(artifact))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Artifact.create_from_object(artifact))

        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[('pgf-no-folclor', 0),
                                                                                                         'folclor-1-caption',
                                                                                                         'folclor-2-caption'])

    def test_no_description(self):
        artifact = storage.artifacts.all()[0]
        artifact.description = ''
        logic.save_artifact_record(artifact)
        self.check_html_ok(self.request_html(dext_urls.url('guide:artifacts:info', artifact.id)), texts=[('pgf-no-description', 1)])


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        self.artifact = storage.artifacts.all()[0]
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.DISABLED
        logic.save_artifact_record(self.artifact)

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:artifacts:edit', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), accounts_logic.login_page_url(request_url), status_code=302, target_status_code=200)

    def test_enabled_state(self):
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.ENABLED
        logic.save_artifact_record(self.artifact)
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('artifacts.disabled_state_required', 1),
                                                                                                                     ('pgf-edit-artifact-form', 0)])

    def test_create_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('artifacts.create_artifact_rights_required', 1),
                                                                                                                     ('pgf-edit-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:edit', args=[self.artifact.id])), texts=[('pgf-edit-artifact-form', 2),
                                                                                                                     self.artifact.name,
                                                                                                                     (self.artifact.description, 1)])


class TestUpdateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

        self.check_ajax_ok(self.client.post(django_reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = logic.construct_from_model(models.ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.mob = mobs_storage.mobs.all()[0]

    def check_artifact(self, artifact, data):
        self.assertEqual(artifact.name, data['name_0'])
        self.assertEqual(artifact.level, data['level'])
        self.assertEqual(artifact.type, data['type'])
        self.assertEqual(artifact.rare_effect, data['rare_effect'])
        self.assertEqual(artifact.epic_effect, data['epic_effect'])
        self.assertEqual(artifact.weapon_type, data['weapon_type'])
        self.assertEqual(artifact.material, data['material'])
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
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data()), 'common.login_required')

    def test_create_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data()), 'artifacts.create_artifact_rights_required')
        self.check_artifact(logic.load_by_id(self.artifact.id), self.get_create_data())

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:update', args=[self.artifact.id]), {}), 'artifacts.update.form_errors')
        self.check_artifact(logic.load_by_id(self.artifact.id), self.get_create_data())

    def test_simple(self):
        response = self.client.post(django_reverse('game:artifacts:update', args=[self.artifact.id]), self.get_update_data())

        artifact_record = logic.load_by_id(self.artifact.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.check_artifact(artifact_record, self.get_update_data())


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        self.artifact = storage.artifacts.all()[0]
        self.artifact.state = relations.ARTIFACT_RECORD_STATE.DISABLED
        logic.save_artifact_record(self.artifact)

    def test_unlogined(self):
        self.request_logout()
        request_url = django_reverse('game:artifacts:moderate', args=[self.artifact.id])
        self.assertRedirects(self.request_html(request_url), accounts_logic.login_page_url(request_url), status_code=302, target_status_code=200)

    def test_moderate_rights(self):
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('artifacts.moderate_artifact_rights_required', 1),
                                                                                                                         ('pgf-moderate-artifact-form', 0)])

    def test_simple(self):
        self.request_logout()
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(django_reverse('game:artifacts:moderate', args=[self.artifact.id])), texts=[('pgf-moderate-artifact-form', 2),
                                                                                                                         self.artifact.name,
                                                                                                                         (self.artifact.description, 1)])


class TestModerateRequests(BaseTestRequests, PostMixin):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        self.request_logout()
        self.request_login(self.account_2.email)

        self.mob = mobs_storage.mobs.all()[0]

        self.check_ajax_ok(self.client.post(django_reverse('game:artifacts:create'), self.get_create_data()))
        self.artifact = logic.construct_from_model(models.ArtifactRecord.objects.all().order_by('-created_at')[0])

        self.name = game_names.generator().get_test_name(name='new name')

        self.request_logout()
        self.request_login(self.account_3.email)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data()), 'common.login_required')

    def test_moderate_rights(self):
        self.request_logout()
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data()), 'artifacts.moderate_artifact_rights_required')
        self.assertEqual(logic.load_by_id(self.artifact.id).uuid, self.artifact.uuid)

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:artifacts:moderate', args=[self.artifact.id]), {}), 'artifacts.moderate.form_errors')
        self.assertEqual(logic.load_by_id(self.artifact.id).uuid, self.artifact.uuid)

    def test_simple(self):
        response = self.client.post(django_reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data())

        artifact_record = logic.load_by_id(self.artifact.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('guide:artifacts:show', args=[artifact_record.id])})

        self.assertEqual(artifact_record.name, 'new name-нс,ед,им')
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
        self.check_ajax_ok(self.client.post(django_reverse('game:artifacts:moderate', args=[self.artifact.id]), self.get_moderate_data(approved=False)))

        artifact_record = logic.load_by_id(self.artifact.id)

        self.assertTrue(artifact_record.state.is_DISABLED)
