
import smart_imports

smart_imports.all()


class CollectDataTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

    def test(self):
        report = data_protection.collect_data(self.account.id)

        self.assertCountEqual(report, [('hero:short_name', self.hero.name),
                                       ('hero:long_name', self.hero.utg_name.serialize()),
                                       ('hero:description', logic.get_hero_description(self.hero.id))])


class RemoveDataTests(clans_helpers.ClansTestsMixin,
                      utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.accounts = [self.accounts_factory.create_account(),
                         self.accounts_factory.create_account()]

    @contextlib.contextmanager
    def check_heroes_not_changed(self):
        with self.check_not_changed(lambda: logic.load_hero(self.accounts[0].id).saved_at):
            with self.check_not_changed(lambda: logic.load_hero(self.accounts[1].id).saved_at):
                yield

    def mark_removed(self, delta=0, sync_save_time=True):
        removed_at = datetime.datetime.now() + datetime.timedelta(seconds=delta)
        accounts_models.Account.objects.filter(id=self.accounts[0].id).update(removed_at=removed_at)

        if sync_save_time:
            heroes_models.Hero.objects.filter(id=self.accounts[0].id).update(saved_at=removed_at)

    def test_account_not_removed(self):
        with self.check_heroes_not_changed():
            with self.assertRaises(NotImplementedError):
                data_protection.remove_data(self.accounts[0].id)

    def test_require_hero_release__due_removed_time(self):

        self.mark_removed()

        with self.check_heroes_not_changed():
            with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_account_release_required') as cmd_account_release_required:
                self.assertFalse(data_protection.remove_data(self.accounts[0].id))

        self.assertEqual(cmd_account_release_required.call_args_list,
                         [mock.call(self.accounts[0].id)])

    def test_require_hero_release__due_save_time(self):

        self.mark_removed(delta=-conf.settings.REMOVE_HERO_DELAY)

        with self.check_heroes_not_changed():
            with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_account_release_required') as cmd_account_release_required:
                self.assertFalse(data_protection.remove_data(self.accounts[0].id))

        self.assertEqual(cmd_account_release_required.call_args_list,
                         [mock.call(self.accounts[0].id)])

    def test_success(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.accounts[0], 1)

        logic.set_hero_description(hero_id=self.accounts[0].id, text='description')

        #######################
        # configure hero
        hero = logic.load_hero(self.accounts[0].id)

        hero.preferences.set(relations.PREFERENCE_TYPE.PLACE, self.places[0])

        hero.update_with_account_data(is_fast=False,
                                      premium_end_at=datetime.datetime.now(),
                                      active_end_at=datetime.datetime.now(),
                                      ban_end_at=datetime.datetime.now(),
                                      might=100500,
                                      actual_bills=[10034, 1231231],
                                      clan_id=clan.id)

        logic.save_hero(hero)

        self.assertNotEqual(hero.preferences.serialize(), preferences.HeroPreferences().serialize())
        #######################

        self.mark_removed(delta=-conf.settings.REMOVE_HERO_DELAY, sync_save_time=False)

        with self.check_changed(lambda: logic.load_hero(self.accounts[0].id).utg_name):
            with self.check_increased(lambda: logic.load_hero(self.accounts[0].id).saved_at):
                with self.check_not_changed(lambda: logic.load_hero(self.accounts[1].id).saved_at):
                    with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_account_release_required') as cmd_account_release_required:
                        self.assertTrue(data_protection.remove_data(self.accounts[0].id))

        self.assertEqual(cmd_account_release_required.call_args_list, [])

        self.assertEqual(logic.get_hero_description(self.accounts[0].id), '')

        hero = logic.load_hero(self.accounts[0].id)

        self.assertEqual(hero.preferences.place, None)

        zero = datetime.datetime.fromtimestamp(0)

        self.assertFalse(hero.is_fast)
        self.assertEqual(hero.premium_state_end_at, zero)
        self.assertEqual(hero.active_state_end_at, zero)
        self.assertEqual(hero.ban_state_end_at, zero)
        self.assertEqual(hero.might, 0)
        self.assertEqual(hero.actual_bills, [])
        self.assertEqual(hero.clan_id, None)
