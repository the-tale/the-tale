
import smart_imports

smart_imports.all()


class HeroRequestsTestBase(utils_testcase.TestCase):

    def setUp(self):
        super(HeroRequestsTestBase, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.request_login(self.account.email)


class HeroIndexRequestsTests(HeroRequestsTestBase):

    def test_index(self):
        chronicle_tt_services.chronicle.cmd_debug_clear_service()

        response = self.request_html(utils_urls.url('game:heroes:'))
        self.assertRedirects(response, '/', status_code=302, target_status_code=200)


class MyHeroRequestsTests(HeroRequestsTestBase):

    def test_unloginned(self):
        self.request_logout()
        request_url = utils_urls.url('game:heroes:my-hero')
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_redirect(self):
        self.check_redirect(utils_urls.url('game:heroes:my-hero'), utils_urls.url('game:heroes:show', self.hero.id))


class HeroPageRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(HeroPageRequestsTests, self).setUp()

    def test_wrong_hero_id(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', 'dsdsd')), texts=[('heroes.hero.wrong_format', 1)])

    def test_own_hero_page(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)),
                           texts=(('pgf-health-percents', 2),
                                  ('pgf-experience-percents', 2),
                                  ('pgf-physic-power value', 1),
                                  ('pgf-magic-power value', 1),
                                  ('pgf-money', 1),
                                  ('"pgf-health"', 2),
                                  ('pgf-max-health', 2),
                                  ('pgf-choose-ability-button', 2),
                                  ('pgf-free-destiny-points', 7),
                                  ('pgf-no-destiny-points', 2),
                                  ('pgf-settings-container', 2),
                                  ('pgf-settings-tab-button', 2),
                                  ('pgf-moderation-container', 0),
                                  'pgf-no-folclor'))

    def test_other_hero_page(self):
        texts = (('pgf-health-percents', 2),
                 ('pgf-experience-percents', 0),
                 ('pgf-physic-power value', 1),
                 ('pgf-magic-power value', 1),
                 ('pgf-money', 1),
                 ('"pgf-health"', 2),
                 ('pgf-max-health', 2),
                 ('pgf-choose-ability-button', 0),
                 ('pgf-no-destiny-points', 0),
                 ('pgf-free-destiny-points', 1),
                 ('pgf-settings-container', 0),
                 ('pgf-settings-tab-button', 1),
                 ('pgf-moderation-container', 0),
                 'pgf-no-folclor')

        self.request_logout()
        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)), texts=texts)

        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)
        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)), texts=texts)

    def test_folclor(self):
        blogs_helpers.prepair_forum()

        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(), 'folclor-1-caption', 'folclor-1-text',
                                                  meta_relations.Hero.create_from_object(self.hero))
        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(), 'folclor-2-caption', 'folclor-2-text',
                                                  meta_relations.Hero.create_from_object(self.hero))
        blogs_helpers.create_post_for_meta_object(self.accounts_factory.create_account(), 'folclor-3-caption', 'folclor-3-text',
                                                  meta_relations.Hero.create_from_object(self.hero))

        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)), texts=(('pgf-no-folclor', 0), 'folclor-1-caption', 'folclor-2-caption', 'folclor-3-caption'))

    def test_moderation_tab(self):
        account_2 = self.accounts_factory.create_account()
        self.request_login(account_2.email)

        group = utils_permissions.sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(account_2._model)

        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)), texts=['pgf-moderation-container'])


class ChangeHeroRequestsTests(HeroRequestsTestBase):

    def test_hero_page(self):
        self.check_html_ok(self.request_html(utils_urls.url('game:heroes:show', self.hero.id)), texts=[jinja2.escape(self.hero.name)])

    def get_post_data(self,
                      name='новое имя',
                      gender=game_relations.GENDER.MALE,
                      race=game_relations.RACE.DWARF,
                      description='some description'):

        data = {'gender': gender,
                'race': race,
                'description': description}
        data.update(linguistics_helpers.get_word_post_data(game_names.generator().get_test_name(name=name), prefix='name'))
        return data

    def test_chane_hero_ownership(self):
        account_2 = self.accounts_factory.create_account()
        self.request_logout()
        self.request_login(account_2.email)
        self.check_ajax_error(self.client.post(utils_urls.url('game:heroes:change-hero', self.hero.id), self.get_post_data()),
                              'heroes.not_owner')

    def test_change_hero_form_errors(self):
        self.check_ajax_error(self.client.post(utils_urls.url('game:heroes:change-hero', self.hero.id), {}),
                              'heroes.change_name.form_errors')

    def test_change_hero(self):
        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(utils_urls.url('game:heroes:change-hero', self.hero.id), self.get_post_data())
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertEqual(task.internal_logic.name, game_names.generator().get_test_name(name='новое имя', properties=[utg_relations.NUMBER.SINGULAR]))
        self.assertEqual(task.internal_logic.gender, game_relations.GENDER.MALE)
        self.assertEqual(task.internal_logic.race, game_relations.RACE.DWARF)

        self.assertEqual(logic.get_hero_description(self.hero.id), 'some description')


class ResetNameRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ResetNameRequestsTests, self).setUp()

        self.account_2 = self.accounts_factory.create_account()

        group = utils_permissions.sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_2._model)

        self.request_login(self.account_2.email)

    def test_chane_hero_moderation(self):
        self.request_logout()
        self.request_login(self.account.email)

        self.check_ajax_error(self.client.post(utils_urls.url('game:heroes:reset-name', self.hero.id)), 'heroes.moderator_rights_required')

    def test_change_hero(self):
        self.hero.set_utg_name(game_names.generator().get_test_name('x'))
        logic.save_hero(self.hero)

        self.assertEqual(PostponedTask.objects.all().count(), 0)
        response = self.client.post(utils_urls.url('game:heroes:reset-name', self.hero.id))
        self.assertEqual(PostponedTask.objects.all().count(), 1)

        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        self.assertNotEqual(task.internal_logic.name, self.hero.name)
        self.assertEqual(task.internal_logic.gender, self.hero.gender)
        self.assertEqual(task.internal_logic.race, self.hero.race)


class ResetDescriptionRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super().setUp()

        self.account_2 = self.accounts_factory.create_account()

        group = utils_permissions.sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_2._model)

        self.request_login(self.account_2.email)

    def test_chane_hero_moderation(self):
        self.request_logout()
        self.request_login(self.account.email)

        logic.set_hero_description(hero_id=self.hero.id, text='test-description')

        self.check_ajax_error(self.client.post(utils_urls.url('game:heroes:reset-description', self.hero.id)),
                              'heroes.moderator_rights_required')

        self.assertEqual(logic.get_hero_description(hero_id=self.hero.id), 'test-description')

    def test_change_hero(self):
        logic.set_hero_description(hero_id=self.hero.id, text='test-description')

        self.check_ajax_ok(self.client.post(utils_urls.url('game:heroes:reset-description', self.hero.id)))

        self.assertEqual(logic.get_hero_description(hero_id=self.hero.id), '')


class ForceSaveRequestsTests(HeroRequestsTestBase):

    def setUp(self):
        super(ForceSaveRequestsTests, self).setUp()

        self.account_2 = self.accounts_factory.create_account()

        group = utils_permissions.sync_group('accounts moderators group', ['accounts.moderate_account'])
        group.user_set.add(self.account_2._model)

        self.request_login(self.account_2.email)

    def test_no_moderation_rights(self):
        self.request_logout()
        self.request_login(self.account.email)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_force_save') as cmd_force_save:
            self.check_ajax_error(self.client.post(utils_urls.url('game:heroes:force-save', self.hero.id)), 'heroes.moderator_rights_required')

        self.assertEqual(cmd_force_save.call_args_list, [])

    def test_force_save(self):
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_force_save') as cmd_force_save:
            self.check_ajax_ok(self.client.post(utils_urls.url('game:heroes:force-save', self.hero.id)))

        self.assertEqual(cmd_force_save.call_args_list, [mock.call(account_id=self.hero.account_id)])
