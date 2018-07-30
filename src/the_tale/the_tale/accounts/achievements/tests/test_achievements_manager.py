
import smart_imports

smart_imports.all()


class AchievementsManagerTests(utils_testcase.TestCase, personal_messages_helpers.Mixin):

    def setUp(self):
        super(AchievementsManagerTests, self).setUp()

        game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        group_edit = utils_permissions.sync_group('edit achievement', ['achievements.edit_achievement'])

        group_edit.user_set.add(self.account_2._model)

        self.achievement_1 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=0, points=10,
                                                                    caption='achievement_1', description='description_1', approved=True)
        self.achievement_2 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.MONEY, type=relations.ACHIEVEMENT_TYPE.MONEY, barrier=5, points=10,
                                                                    caption='achievement_2', description='description_2', approved=False)
        self.achievement_3 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.TIME, type=relations.ACHIEVEMENT_TYPE.DEATHS, barrier=4, points=10,
                                                                    caption='achievement_3', description='description_3', approved=True)

        self.account_achievements_1 = prototypes.AccountAchievementsPrototype.get_by_account_id(self.account_1.id)
        self.account_achievements_1.achievements.add_achievement(self.achievement_1)
        self.account_achievements_1.save()

        self.worker = amqp_environment.environment.workers.achievements_manager
        self.worker.initialize()

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_add_achievements__not_tasks(self):
        self.worker.add_achievements()
        self.account_achievements_1.reload()
        self.assertEqual(len(self.account_achievements_1.achievements), 1)

    def test_add_achievements(self):
        prototypes.GiveAchievementTaskPrototype.create(account_id=self.account_1.id, achievement_id=self.achievement_3.id)
        self.assertFalse(self.account_achievements_1.has_achievement(self.achievement_3))

        with self.check_new_message(self.account_1.id, [accounts_logic.get_system_user_id()]):
            self.worker.add_achievements()

        self.account_achievements_1.reload()
        self.assertTrue(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertEqual(prototypes.GiveAchievementTaskPrototype._db_count(), 0)

    @mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements', lambda *argv, **kwargs: None)
    def test_add_achievements__all_accounts(self):

        prototypes.GiveAchievementTaskPrototype.create(account_id=None, achievement_id=self.achievement_3.id)

        account_achievements_2 = prototypes.AccountAchievementsPrototype.get_by_account_id(self.account_2.id)

        self.assertFalse(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertFalse(account_achievements_2.has_achievement(self.achievement_3))
        hero = heroes_logic.load_hero(account_id=self.account_1.id)
        hero.statistics.change_pve_deaths(self.achievement_3.barrier)
        heroes_logic.save_hero(hero)

        with self.check_no_messages(self.account_2.id):
            with self.check_no_messages(self.account_1.id):
                self.worker.add_achievements()

        self.account_achievements_1.reload()
        account_achievements_2.reload()

        self.assertTrue(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertFalse(account_achievements_2.has_achievement(self.achievement_3))

        self.assertEqual(prototypes.GiveAchievementTaskPrototype._db_count(), 0)

    @mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements', lambda *argv, **kwargs: None)
    def test_add_achievements__all_accounts__not_remove_already_received_achievements(self):
        self.account_achievements_1.achievements.add_achievement(self.achievement_3)
        self.account_achievements_1.save()

        prototypes.GiveAchievementTaskPrototype.create(account_id=None, achievement_id=self.achievement_3.id)

        account_achievements_2 = prototypes.AccountAchievementsPrototype.get_by_account_id(self.account_2.id)

        self.assertTrue(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertFalse(account_achievements_2.has_achievement(self.achievement_3))

        with self.check_no_messages(self.account_2.id):
            with self.check_no_messages(self.account_1.id):
                self.worker.add_achievements()

        self.account_achievements_1.reload()
        account_achievements_2.reload()

        self.assertTrue(self.account_achievements_1.has_achievement(self.achievement_3))
        self.assertFalse(account_achievements_2.has_achievement(self.achievement_3))

        self.assertEqual(prototypes.GiveAchievementTaskPrototype._db_count(), 0)

    def test_legendary_achievements(self):
        achievement_4 = prototypes.AchievementPrototype.create(group=relations.ACHIEVEMENT_GROUP.LEGENDS, type=relations.ACHIEVEMENT_TYPE.LEGENDS, barrier=0, points=0,
                                                               caption='achievement_4', description='description_4', approved=True)

        self.account_achievements_1.achievements.add_achievement(achievement_4)
        self.account_achievements_1.save()

        prototypes.GiveAchievementTaskPrototype.create(account_id=None, achievement_id=achievement_4.id)

        account_achievements_2 = prototypes.AccountAchievementsPrototype.get_by_account_id(self.account_2.id)

        self.assertTrue(self.account_achievements_1.has_achievement(achievement_4))
        self.assertFalse(account_achievements_2.has_achievement(achievement_4))

        with self.check_no_messages(self.account_2.id):
            with self.check_no_messages(self.account_1.id):
                self.worker.add_achievements()

        self.account_achievements_1.reload()
        account_achievements_2.reload()

        self.assertTrue(self.account_achievements_1.has_achievement(achievement_4))
        self.assertFalse(account_achievements_2.has_achievement(achievement_4))

        self.assertEqual(prototypes.GiveAchievementTaskPrototype._db_count(), 0)
