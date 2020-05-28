
import smart_imports

smart_imports.all()


class AccountPrototypeTests(utils_testcase.TestCase, personal_messages_helpers.Mixin):

    def setUp(self):
        super(AccountPrototypeTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()
        self.account = self.accounts_factory.create_account()
        self.fast_account = self.accounts_factory.create_account(is_fast=True)

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_create(self):
        self.assertTrue(self.account.active_end_at > datetime.datetime.now() + datetime.timedelta(seconds=conf.settings.ACTIVE_STATE_TIMEOUT - 60))

    def test_get_achievement_type_value(self):
        for achievement_type in achievements_relations.ACHIEVEMENT_TYPE.records:
            if achievement_type.source.is_GAME_OBJECT:
                continue
            if achievement_type.source.is_NONE:
                continue
            self.account.get_achievement_type_value(achievement_type)

    @mock.patch('the_tale.accounts.conf.settings.ACTIVE_STATE_REFRESH_PERIOD', 0)
    def test_update_active_state__expired(self):
        self.assertTrue(self.account.is_update_active_state_needed)
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as cmd_mark_hero_as_active:
            self.account.update_active_state()
        self.assertEqual(cmd_mark_hero_as_active.call_count, 1)

    def test_update_active_state__not_expired(self):
        self.assertFalse(self.account.is_update_active_state_needed)

    def test_prolong_premium__for_new_premium(self):
        self.account._model.premium_end_at = datetime.datetime.now() - datetime.timedelta(days=100)

        self.account.prolong_premium(days=30)

        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=29) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=31) > self.account.premium_end_at)

    def test_prolong_premium__for_existed_premium(self):
        self.account._model.premium_end_at = datetime.datetime.now() + datetime.timedelta(days=100)

        self.account.prolong_premium(days=30)

        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=129) < self.account.premium_end_at)
        self.assertTrue(datetime.datetime.now() + datetime.timedelta(days=131) > self.account.premium_end_at)

    def test_is_premium(self):
        self.assertFalse(self.account.is_premium)
        self.account.prolong_premium(days=1)
        self.assertTrue(self.account.is_premium)

    def is_technical(self):
        self.assertFalse(self.account.is_technical)
        self.assertTrue(logic.get_system_user().is_technical)
        self.assertTrue(self.accounts_factory.create_account(is_bot=True).is_technical)

    def test_cards_receive_mode__not_premium(self):
        self.assertFalse(self.account.is_premium)

        self.account.set_cards_receive_mode(cards_relations.RECEIVE_MODE.PERSONAL_ONLY)
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

        self.account.set_cards_receive_mode(cards_relations.RECEIVE_MODE.ALL)
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

    def test_cards_receive_mode__premium(self):
        self.account.prolong_premium(days=1)
        self.assertTrue(self.account.is_premium)

        self.account.set_cards_receive_mode(cards_relations.RECEIVE_MODE.PERSONAL_ONLY)
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

        self.account.set_cards_receive_mode(cards_relations.RECEIVE_MODE.ALL)
        self.assertTrue(self.account.cards_receive_mode().is_ALL)

    def test_notify_about_premium_expiration(self):
        with self.check_new_message(self.account.id, [logic.get_system_user_id()]):
            self.account.notify_about_premium_expiration()

    def test_send_premium_expired_notifications(self):
        with self.check_new_message(self.account.id, [logic.get_system_user_id()]):
            account_1 = self.account
            account_2 = self.accounts_factory.create_account()
            account_3 = self.accounts_factory.create_account()
            account_4 = self.accounts_factory.create_account()

            account_1.prolong_premium(conf.settings.PREMIUM_EXPIRED_NOTIFICATION_IN.days - 1)
            account_1.save()

            account_3.prolong_premium(conf.settings.PREMIUM_EXPIRED_NOTIFICATION_IN.days - 1)
            account_3.save()

            account_4.prolong_premium(conf.settings.PREMIUM_EXPIRED_NOTIFICATION_IN.days + 1)
            account_4.save()

            zero_time = datetime.datetime.fromtimestamp(0)

            self.assertEqual(account_1._model.premium_expired_notification_send_at, zero_time)
            self.assertEqual(account_2._model.premium_expired_notification_send_at, zero_time)
            self.assertEqual(account_3._model.premium_expired_notification_send_at, zero_time)
            self.assertEqual(account_4._model.premium_expired_notification_send_at, zero_time)

            prototypes.AccountPrototype.send_premium_expired_notifications()

            account_1.reload()
            account_2.reload()
            account_3.reload()
            account_4.reload()

            self.assertNotEqual(account_1._model.premium_expired_notification_send_at, zero_time)
            self.assertEqual(account_2._model.premium_expired_notification_send_at, zero_time)
            self.assertNotEqual(account_3._model.premium_expired_notification_send_at, zero_time)
            self.assertEqual(account_4._model.premium_expired_notification_send_at, zero_time)

            current_time = datetime.datetime.now()

            self.assertTrue(current_time - datetime.timedelta(seconds=60) < account_1._model.premium_expired_notification_send_at < current_time)
            self.assertTrue(current_time - datetime.timedelta(seconds=60) < account_3._model.premium_expired_notification_send_at < current_time)

    def test_set_clan_id(self):
        self.assertEqual(self.account.clan_id, None)

        forum_category = forum_prototypes.CategoryPrototype.create(caption='clan-category',
                                                                   slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                   order=0)

        forum_subcategory = forum_prototypes.SubCategoryPrototype.create(category=forum_category,
                                                                         caption='xxx',
                                                                         order=0,
                                                                         restricted=True)

        clan = clans_logic.create_clan(owner=self.accounts_factory.create_account(),
                                       name='xxx',
                                       abbr='yyy',
                                       motto='zzz',
                                       description='qqq')

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as cmd_update_hero_with_account_data:
            self.account.set_clan_id(clan.id)

        self.assertEqual(self.account.clan_id, clan.id)
        self.assertEqual(models.Account.objects.get(id=self.account.id).clan_id, clan.id)

        self.assertEqual(cmd_update_hero_with_account_data.call_count, 1)
        self.assertEqual(cmd_update_hero_with_account_data.call_args[1]['clan_id'], clan.id)

    def test_ban_game(self):
        self.assertFalse(self.account.is_ban_game)
        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as cmd_update_hero_with_account_data:
            self.account.ban_game(days=1)
        self.assertEqual(cmd_update_hero_with_account_data.call_count, 1)
        self.assertEqual(cmd_update_hero_with_account_data.call_args[1]['ban_end_at'], self.account.ban_game_end_at)
        self.assertTrue(self.account.is_ban_game)
        self.account._model.ban_game_end_at = datetime.datetime.now()
        self.assertFalse(self.account.is_ban_game)

    def test_ban_forum(self):
        self.assertFalse(self.account.is_ban_forum)
        self.account.ban_forum(days=1)
        self.assertTrue(self.account.is_ban_forum)
        self.account._model.ban_forum_end_at = datetime.datetime.now()
        self.assertFalse(self.account.is_ban_forum)

    def test_bank_account__not_created(self):
        bank_account = self.account.bank_account

        self.assertTrue(bank_account.is_fake)
        self.assertEqual(bank_account.amount, 0)

    def test_referral_removing(self):
        account_2 = self.accounts_factory.create_account(referral_of_id=self.account.id, is_fast=True)

        self.account.remove()

        # child account must not be removed
        self.assertEqual(prototypes.AccountPrototype.get_by_id(account_2.id).referral_of_id, None)

    def test_set_might(self):
        with mock.patch('the_tale.accounts.achievements.storage.AchievementsStorage.verify_achievements') as verify_achievements:
            self.account.set_might(666)

        self.assertEqual(verify_achievements.call_args_list, [mock.call(account_id=self.account.id,
                                                                        type=achievements_relations.ACHIEVEMENT_TYPE.KEEPER_MIGHT,
                                                                        old_value=0,
                                                                        new_value=666)])

    @mock.patch('the_tale.game.bills.conf.settings.MIN_VOTES_PERCENT', 0.6)
    @mock.patch('the_tale.game.bills.prototypes.BillPrototype.time_before_voting_end', datetime.timedelta(seconds=0))
    # fixt segmentation fault when testing with sqlite
    def test_1_update_actual_bills(self):
        forum_category = forum_models.Category.objects.create(caption='category-1', slug='category-1')
        forum_models.SubCategory.objects.create(caption=bills_conf.settings.FORUM_CATEGORY_UID + '-caption',
                                                uid=bills_conf.settings.FORUM_CATEGORY_UID,
                                                category=forum_category)

        self.account.update_actual_bills()
        self.assertEqual(self.account.actual_bills, [])

        bill_data = bills_bills.place_change_modifier.PlaceModifier(place_id=self.place_1.id,
                                                                    modifier_id=places_modifiers.CITY_MODIFIERS.TRADE_CENTER,
                                                                    modifier_name=places_modifiers.CITY_MODIFIERS.TRADE_CENTER.text,
                                                                    old_modifier_name=None)
        bill = bills_prototypes.BillPrototype.create(self.account, 'bill-1-caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')

        self.account.update_actual_bills()
        self.assertEqual(self.account.actual_bills, [])

        data = bill.user_form_initials
        data['approved'] = True
        form = bills_bills.place_change_modifier.PlaceModifier.ModeratorForm(data)
        self.assertTrue(form.is_valid())
        bill.update_by_moderator(form)

        bill.apply()

        self.account.update_actual_bills()
        self.assertEqual(self.account.actual_bills, [utils_logic.to_timestamp(bill.voting_end_at)])


class AccountPrototypeBanTests(utils_testcase.TestCase):

    def setUp(self):
        super(AccountPrototypeBanTests, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_ban_game(self):
        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.ban_game(2)

        self.assertEqual(cmd_update_hero.call_count, 1)

        self.account.reload()

        self.assertTrue(self.account.is_ban_game)
        self.assertTrue(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_forum)

        self.assertTrue(datetime.timedelta(days=1) < self.account._model.ban_game_end_at - datetime.datetime.now() < datetime.timedelta(days=3))

    def test_ban_game__extend(self):
        self.account.ban_game(3)

        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.ban_game(2)

        self.assertEqual(cmd_update_hero.call_count, 1)

        self.account.reload()

        self.assertTrue(self.account.is_ban_game)
        self.assertTrue(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_forum)

        self.assertTrue(datetime.timedelta(days=4) < self.account._model.ban_game_end_at - datetime.datetime.now() < datetime.timedelta(days=6))

    def test_ban_game__reset(self):
        self.account.ban_game(2)

        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.reset_ban_game()

        self.assertEqual(cmd_update_hero.call_count, 1)

        self.account.reload()

        self.assertFalse(self.account.is_ban_game)
        self.assertFalse(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_forum)

        self.assertTrue(self.account._model.ban_game_end_at < datetime.datetime.now())

    def test_ban_forum(self):
        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.ban_forum(2)

        self.assertEqual(cmd_update_hero.call_count, 0)

        self.account.reload()

        self.assertTrue(self.account.is_ban_forum)
        self.assertTrue(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_game)

        self.assertTrue(datetime.timedelta(days=1) < self.account._model.ban_forum_end_at - datetime.datetime.now() < datetime.timedelta(days=3))

    def test_ban_forum__extend(self):
        self.account.ban_forum(3)

        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.ban_forum(2)

        self.assertEqual(cmd_update_hero.call_count, 0)

        self.account.reload()

        self.assertTrue(self.account.is_ban_forum)
        self.assertTrue(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_game)

        self.assertTrue(datetime.timedelta(days=4) < self.account._model.ban_forum_end_at - datetime.datetime.now() < datetime.timedelta(days=6))

    def test_ban_forum__reset(self):
        self.account.ban_forum(2)

        with mock.patch('the_tale.accounts.prototypes.AccountPrototype.cmd_update_hero') as cmd_update_hero:
            self.account.reset_ban_forum()

        self.assertEqual(cmd_update_hero.call_count, 0)

        self.account.reload()

        self.assertFalse(self.account.is_ban_forum)
        self.assertFalse(self.account.is_ban_any)
        self.assertFalse(self.account.is_ban_game)

        self.assertTrue(self.account._model.ban_forum_end_at < datetime.datetime.now())
