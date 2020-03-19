
import smart_imports

smart_imports.all()


class RequestsTestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(RequestsTestsBase, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_moderate = utils_permissions.sync_group('moderate companions', ['companions.moderate_companionrecord'])

        group_edit.user_set.add(self.account_2._model)
        group_edit.user_set.add(self.account_3._model)
        group_moderate.user_set.add(self.account_3._model)


class IndexRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()
        self.requested_url = utils_urls.url('game:companions:')
        self.requested_url_disabled = utils_urls.url('game:companions:', state=relations.STATE.DISABLED.value)

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-2'),
                                                         description='companion-description',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_2,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

    def test_no_items(self):
        models.CompanionRecord.objects.all().delete()
        storage.companions.refresh()
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 1),
                                                                         (self.companion_1.name, 0),
                                                                         (self.companion_2.name, 0)])

    def test_anonimouse_view(self):
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 0),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 0),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-companions-message', 0),
                                                                         ('pgf-create-companion-button', 1),
                                                                         (self.companion_1.name, 1),
                                                                         (self.companion_2.name, 0)])

    def test_normal_view__disabled_records(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 1),
                                                                                  ('pgf-create-companion-button', 0),
                                                                                  (self.companion_1.name, 0),
                                                                                  (self.companion_2.name, 0)])

    def test_editor_view__disabled_records(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 0),
                                                                                  ('pgf-create-companion-button', 1),
                                                                                  (self.companion_1.name, 0),
                                                                                  (self.companion_2.name, 1)])

    def test_moderator_view__disabled_records(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_disabled), texts=[('pgf-no-companions-message', 0),
                                                                                  ('pgf-create-companion-button', 1),
                                                                                  (self.companion_1.name, 0),
                                                                                  (self.companion_2.name, 1)])


class NewRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(NewRequestsTests, self).setUp()

        self.requested_url = utils_urls.url('game:companions:new')

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=['companions.no_edit_rights'])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('companions.no_edit_rights', 0)])


class CreateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()

        self.requested_url = utils_urls.url('game:companions:create')

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def post_data(self):
        data = {'description': 'some-description',
                'type': tt_beings_relations.TYPE.random(),
                'max_health': 650,
                'dedication': relations.DEDICATION.random(),
                'archetype': game_relations.ARCHETYPE.random(),
                'mode': relations.MODE.random(),
                'communication_verbal': tt_beings_relations.COMMUNICATION_VERBAL.CAN,
                'communication_gestures': tt_beings_relations.COMMUNICATION_GESTURES.CAN,
                'communication_telepathic': tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN,
                'intellect_level': tt_beings_relations.INTELLECT_LEVEL.NORMAL,

                'structure': tt_beings_relations.STRUCTURE.STRUCTURE_1,
                'features': [tt_beings_relations.FEATURE.FEATURE_2, tt_beings_relations.FEATURE.FEATURE_3],
                'movement': tt_beings_relations.MOVEMENT.MOVEMENT_3,
                'body': tt_beings_relations.BODY.BODY_4,
                'size': tt_beings_relations.SIZE.SIZE_5,
                'orientation': tt_beings_relations.ORIENTATION.HORIZONTAL,
                'weapon_1': artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                'material_1': tt_artifacts_relations.MATERIAL.MATERIAL_1,
                'power_type_1': artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL,
                'weapon_2': artifacts_relations.STANDARD_WEAPON.WEAPON_2,
                'material_2': tt_artifacts_relations.MATERIAL.MATERIAL_2,
                'power_type_2': artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL,
                'weapon_3': artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                'material_3': tt_artifacts_relations.MATERIAL.MATERIAL_3,
                'power_type_3': artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL,
                }
        data.update(linguistics_helpers.get_word_post_data(game_names.generator().get_test_name(name='name'), prefix='name'))
        data.update(helpers.get_abilities_post_data(helpers.FAKE_ABILITIES_CONTAINER_1),)
        return data

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'common.login_required')

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'companions.no_edit_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)

        post_data = self.post_data()

        with self.check_delta(models.CompanionRecord.objects.count, 1):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_delta(lambda: len(storage.companions), 1):
                    response = self.post_ajax_json(self.requested_url, post_data)

        new_companion = logic.get_last_companion()

        self.check_ajax_ok(response, data={'next_url': utils_urls.url('guide:companions:show', new_companion.id)})

        self.assertEqual(new_companion.description, 'some-description')
        self.assertTrue(new_companion.state.is_DISABLED)
        self.assertTrue(new_companion.communication_verbal.is_CAN)
        self.assertTrue(new_companion.communication_gestures.is_CAN)
        self.assertTrue(new_companion.communication_telepathic.is_CAN)
        self.assertTrue(new_companion.intellect_level.is_NORMAL)
        self.assertEqual(new_companion.type, post_data['type'])
        self.assertEqual(new_companion.max_health, post_data['max_health'])
        self.assertEqual(new_companion.dedication, post_data['dedication'])
        self.assertEqual(new_companion.archetype, post_data['archetype'])
        self.assertEqual(new_companion.mode, post_data['mode'])
        self.assertEqual(new_companion.name, 'name-нс,ед,им')

        self.assertTrue(new_companion.structure.is_STRUCTURE_1)
        self.assertEqual(new_companion.features, frozenset((tt_beings_relations.FEATURE.FEATURE_2, tt_beings_relations.FEATURE.FEATURE_3)))
        self.assertTrue(new_companion.movement.is_MOVEMENT_3)
        self.assertTrue(new_companion.body.is_BODY_4)
        self.assertTrue(new_companion.size.is_SIZE_5)
        self.assertTrue(new_companion.orientation.is_HORIZONTAL)
        self.assertEqual(new_companion.weapons, [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_1,
                                                                          material=tt_artifacts_relations.MATERIAL.MATERIAL_1,
                                                                          power_type=artifacts_relations.ARTIFACT_POWER_TYPE.NEUTRAL),
                                                 artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_2,
                                                                          material=tt_artifacts_relations.MATERIAL.MATERIAL_2,
                                                                          power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MAGICAL),
                                                 artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_3,
                                                                          material=tt_artifacts_relations.MATERIAL.MATERIAL_3,
                                                                          power_type=artifacts_relations.ARTIFACT_POWER_TYPE.PHYSICAL)])

        self.assertEqual(new_companion.abilities, helpers.FAKE_ABILITIES_CONTAINER_1)

    def test_form_errors(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_not_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_error(self.post_ajax_json(self.requested_url, {}), 'form_errors')


class ShowRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(ShowRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description-1',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-2'),
                                                         description='companion-description-2',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_2,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

        self.requested_url_1 = utils_urls.url('game:companions:show', self.companion_1.id)
        self.requested_url_2 = utils_urls.url('game:companions:show', self.companion_2.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_moderate = utils_permissions.sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_moderate.user_set.add(self.account_3._model)

    def test_anonimouse_view(self):
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_anonimouse_view__companion_disabled(self):
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('pgf-error-no_rights', 1),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0),
                                                                           'pgf-no-folclor'])

    def test_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Companion.create_from_object(self.companion_1))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Companion.create_from_object(self.companion_1))

        self.check_html_ok(self.request_html(self.requested_url_1), texts=[('pgf-no-folclor', 0),
                                                                           'folclor-1-caption',
                                                                           'folclor-2-caption'])

    def test_normal_view__companion_disabled(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                           ('pgf-error-no_rights', 1),
                                                                           ('pgf-edit-companion-button', 0),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_editor_view__companion_disabled(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 0)])

    def test_moderator_view__companion_disabled(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                           ('pgf-error-no_rights', 0),
                                                                           ('pgf-edit-companion-button', 1),
                                                                           ('pgf-enable-companion-button', 1)])


class InfoRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(InfoRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description-1',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.ENABLED)

        self.companion_2 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-2'),
                                                         description='companion-description-2',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_2,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

        self.requested_url_1 = utils_urls.url('game:companions:info', self.companion_1.id)
        self.requested_url_2 = utils_urls.url('game:companions:info', self.companion_2.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_moderate = utils_permissions.sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_moderate.user_set.add(self.account_3._model)

    def test_anonimouse_view(self):
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                                ('pgf-error-no_rights', 0)])

    def test_anonimouse_view__companion_disabled(self):
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                                ('pgf-error-no_rights', 1)])

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                                ('pgf-error-no_rights', 0)])

    def test_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.account_1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Companion.create_from_object(self.companion_1))
        blogs_helpers.create_post_for_meta_object(self.account_2, 'folclor-2-caption', 'folclor-2-text', meta_relations.Companion.create_from_object(self.companion_1))

        self.check_html_ok(self.request_html(self.requested_url_1), texts=[('pgf-no-folclor', 0),
                                                                           'folclor-1-caption',
                                                                           'folclor-2-caption'])

    def test_normal_view__companion_disabled(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 0),
                                                                                ('pgf-error-no_rights', 1)])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                                ('pgf-error-no_rights', 0)])

    def test_editor_view__companion_disabled(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                                ('pgf-error-no_rights', 0)])

    def test_moderator_view(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_1), texts=[(self.companion_1.description, 1),
                                                                                ('pgf-error-no_rights', 0)])

    def test_moderator_view__companion_disabled(self):
        self.request_login(self.account_3.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url_2), texts=[(self.companion_2.description, 1),
                                                                                ('pgf-error-no_rights', 0)])


class EditRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(EditRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description-1',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

        self.requested_url = utils_urls.url('game:companions:edit', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=['companions.no_edit_rights'])

    def test_editor_view(self):
        self.request_login(self.account_2.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('companions.no_edit_rights', 0),
                                                                         self.companion_1.name,
                                                                         self.companion_1.description])


class UpdateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(UpdateRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description-1',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         mode=relations.MODE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.CAN_NOT,
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.CAN_NOT,
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN_NOT,
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.LOW,
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

        self.requested_url = utils_urls.url('game:companions:update', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

    def post_data(self):
        data = {'description': 'new-description',
                'type': tt_beings_relations.TYPE.random(),
                'max_health': 650,
                'dedication': relations.DEDICATION.random(),
                'archetype': game_relations.ARCHETYPE.random(),
                'mode': relations.MODE.random(),
                'communication_verbal': tt_beings_relations.COMMUNICATION_VERBAL.CAN,
                'communication_gestures': tt_beings_relations.COMMUNICATION_GESTURES.CAN,
                'communication_telepathic': tt_beings_relations.COMMUNICATION_TELEPATHIC.CAN,
                'intellect_level': tt_beings_relations.INTELLECT_LEVEL.NORMAL,
                'structure': tt_beings_relations.STRUCTURE.STRUCTURE_2,
                'features': [tt_beings_relations.FEATURE.FEATURE_3, tt_beings_relations.FEATURE.FEATURE_4],
                'movement': tt_beings_relations.MOVEMENT.MOVEMENT_5,
                'body': tt_beings_relations.BODY.BODY_6,
                'size': tt_beings_relations.SIZE.SIZE_1,
                'orientation': tt_beings_relations.ORIENTATION.VERTICAL,
                'weapon_1': artifacts_relations.STANDARD_WEAPON.WEAPON_4,
                'material_1': tt_artifacts_relations.MATERIAL.MATERIAL_4,
                'power_type_1': artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL,
                'weapon_2': artifacts_relations.STANDARD_WEAPON.WEAPON_5,
                'material_2': tt_artifacts_relations.MATERIAL.MATERIAL_5,
                'power_type_2': artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL}
        data.update(linguistics_helpers.get_word_post_data(game_names.generator().get_test_name(name='new_name'), prefix='name'))
        data.update(helpers.get_abilities_post_data(helpers.FAKE_ABILITIES_CONTAINER_2),)
        return data

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'common.login_required')

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url, self.post_data()), 'companions.no_edit_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)

        post_data = self.post_data()

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_ok(self.post_ajax_json(self.requested_url, post_data),
                                       data={'next_url': utils_urls.url('guide:companions:show', self.companion_1.id)})

        # storage.companions.refresh()

        companion = storage.companions[self.companion_1.id]

        self.assertEqual(companion.description, 'new-description')
        self.assertTrue(companion.state.is_DISABLED)
        self.assertTrue(companion.communication_verbal.is_CAN)
        self.assertTrue(companion.communication_gestures.is_CAN)
        self.assertTrue(companion.communication_telepathic.is_CAN)
        self.assertTrue(companion.intellect_level.is_NORMAL)
        self.assertEqual(companion.type, post_data['type'])
        self.assertEqual(companion.max_health, post_data['max_health'])
        self.assertEqual(companion.dedication, post_data['dedication'])
        self.assertEqual(companion.mode, post_data['mode'])
        self.assertEqual(companion.name, 'new_name-нс,ед,им')
        self.assertEqual(companion.abilities, helpers.FAKE_ABILITIES_CONTAINER_2)

        self.assertTrue(companion.structure.is_STRUCTURE_2)
        self.assertEqual(companion.features, frozenset((tt_beings_relations.FEATURE.FEATURE_3, tt_beings_relations.FEATURE.FEATURE_4)))
        self.assertTrue(companion.movement.is_MOVEMENT_5)
        self.assertTrue(companion.body.is_BODY_6)
        self.assertTrue(companion.size.is_SIZE_1)
        self.assertTrue(companion.orientation.is_VERTICAL)
        self.assertEqual(companion.weapons, [artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_4,
                                                                      material=tt_artifacts_relations.MATERIAL.MATERIAL_4,
                                                                      power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_MAGICAL),
                                             artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.WEAPON_5,
                                                                      material=tt_artifacts_relations.MATERIAL.MATERIAL_5,
                                                                      power_type=artifacts_relations.ARTIFACT_POWER_TYPE.MOST_PHYSICAL)])

    def test_form_errors(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_not_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_error(self.post_ajax_json(self.requested_url, {}), 'form_errors')

        companion = storage.companions[self.companion_1.id]

        self.assertEqual(companion.description, self.companion_1.description)
        self.assertEqual(companion.name, self.companion_1.name)


class EnableRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(EnableRequestsTests, self).setUp()

        self.companion_1 = logic.create_companion_record(utg_name=game_names.generator().get_test_name('c-1'),
                                                         description='companion-description-1',
                                                         type=tt_beings_relations.TYPE.random(),
                                                         max_health=100,
                                                         dedication=relations.DEDICATION.random(),
                                                         archetype=game_relations.ARCHETYPE.random(),
                                                         abilities=helpers.FAKE_ABILITIES_CONTAINER_1,
                                                         mode=relations.MODE.random(),
                                                         communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                         communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                         communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                         intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                         structure=tt_beings_relations.STRUCTURE.random(),
                                                         features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                         movement=tt_beings_relations.MOVEMENT.random(),
                                                         body=tt_beings_relations.BODY.random(),
                                                         size=tt_beings_relations.SIZE.random(),
                                                         orientation=tt_beings_relations.ORIENTATION.random(),
                                                         weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                           material=tt_artifacts_relations.MATERIAL.random(),
                                                                                           power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                         state=relations.STATE.DISABLED)

        self.requested_url = utils_urls.url('game:companions:enable', self.companion_1.id)

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()
        self.account_3 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit companions', ['companions.create_companionrecord'])
        group_edit.user_set.add(self.account_2._model)

        group_edit = utils_permissions.sync_group('moderate companions', ['companions.moderate_companionrecord'])
        group_edit.user_set.add(self.account_3._model)

    def test_anonimouse_view(self):
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'common.login_required')

    def test_normal_user(self):
        self.request_login(self.account_1.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'companions.no_moderate_rights')

    def test_editor_user(self):
        self.request_login(self.account_2.email)
        self.check_ajax_error(self.post_ajax_json(self.requested_url), 'companions.no_moderate_rights')

    def test_moderator_user(self):
        self.request_login(self.account_3.email)

        with self.check_not_changed(models.CompanionRecord.objects.count):
            with self.check_changed(lambda: storage.companions._version):
                with self.check_not_changed(storage.companions.__len__):
                    self.check_ajax_ok(self.post_ajax_json(self.requested_url))

        companion = storage.companions[self.companion_1.id]

        self.assertTrue(companion.state.is_ENABLED)
