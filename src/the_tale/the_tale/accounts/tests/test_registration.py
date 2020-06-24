
import smart_imports

smart_imports.all()


def raise_exception(*argv, **kwargs):
    raise Exception('unknown error')


class TestRegistration(utils_testcase.TestCase):

    def setUp(self):
        super(TestRegistration, self).setUp()
        game_logic.create_test_map()
        tt_services.players_timers.cmd_debug_clear_service()

    def test_successfull_result(self):

        self.assertEqual(achievements_prototypes.AccountAchievementsPrototype._db_count(), 0)
        self.assertEqual(collections_prototypes.AccountItemsPrototype._db_count(), 0)

        result, account_id, bundle_id = logic.register_user('test_user', 'test_user@test.com', '111111')

        # test result
        self.assertTrue(result.is_OK)
        self.assertTrue(bundle_id is not None)

        # test basic structure
        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')

        self.assertTrue(not account.is_fast)

        hero = heroes_logic.load_hero(account_id=account.id)

        # test hero equipment
        self.assertEqual(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.PANTS).id, 'default_pants')
        self.assertEqual(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.BOOTS).id, 'default_boots')
        self.assertEqual(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.PLATE).id, 'default_plate')
        self.assertEqual(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.GLOVES).id, 'default_gloves')
        self.assertEqual(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.HAND_PRIMARY).id, 'default_weapon')

        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.HAND_SECONDARY) is None)
        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.HELMET) is None)
        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.SHOULDERS) is None)
        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.CLOAK) is None)
        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.AMULET) is None)
        self.assertTrue(hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.RING) is None)

        self.assertEqual(heroes_models.HeroPreferences.objects.all().count(), 1)
        self.assertEqual(heroes_models.HeroPreferences.objects.get(hero_id=hero.id).religion_type,
                         hero.preferences.religion_type)

        self.assertEqual(account.referer, None)
        self.assertEqual(account.referer_domain, None)
        self.assertEqual(account.referral_of_id, None)
        self.assertEqual(account.action_id, None)

        self.assertEqual(account.is_bot, False)

        self.assertEqual(achievements_prototypes.AccountAchievementsPrototype._db_count(), 1)
        self.assertEqual(collections_prototypes.AccountItemsPrototype._db_count(), 1)

        timers = tt_services.players_timers.cmd_get_owner_timers(owner_id=account.id)

        self.assertEqual(len(timers), 1)

    def test_successfull_result__referer(self):
        referer = 'https://example.com/forum/post/1/'

        _, account_id, _ = logic.register_user('test_user', 'test_user@test.com', '111111', referer=referer)

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.nick, 'test_user')
        self.assertEqual(account.email, 'test_user@test.com')
        self.assertEqual(account.referer, referer)
        self.assertEqual(account.referer_domain, 'example.com')

    def test_successfull_result__referral(self):
        _, owner_id, _ = logic.register_user('test_user', 'test_user@test.com', '111111')
        _, account_id, _ = logic.register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id=owner_id)

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, owner_id)

    def test_successfull_result__unexisted_referral(self):
        _, account_id, _ = logic.register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id=666)

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, None)

    def test_successfull_result__wrong_referral(self):
        _, owner_id, _ = logic.register_user('test_user', 'test_user@test.com', '111111')
        _, account_id, _ = logic.register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id='%dxxx' % owner_id)

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.referral_of_id, None)

    def test_successfull_result__action(self):
        _, account_id, _ = logic.register_user('test_user_2', 'test_user_2@test.com', '111111', action_id='action')

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.action_id, 'action')

    def test_successfull_result__unexisted_action(self):
        _, account_id, _ = logic.register_user('test_user_2', 'test_user_2@test.com', '111111', action_id=None)

        account = prototypes.AccountPrototype.get_by_id(account_id)

        self.assertEqual(account.action_id, None)

    def test_duplicate_nick(self):
        result, account_id, bundle_id = logic.register_user('test_user', 'test_user@test.com', '111111')
        self.assertTrue(result.is_OK)
        self.assertTrue(bundle_id is not None)
        result, account_id, bundle_id = logic.register_user('test_user', 'test_user2@test.com', '111111')
        self.assertTrue(result.is_DUPLICATE_USERNAME)
        self.assertTrue(bundle_id is None)

    def test_duplicate_email(self):
        result, account_id, bundle_id = logic.register_user('test_user', 'test_user@test.com', '111111')
        self.assertTrue(result.is_OK)
        self.assertTrue(bundle_id is not None)
        result, account_id, bundle_id = logic.register_user('test_user2', 'test_user@test.com', '111111')
        self.assertTrue(result.is_DUPLICATE_EMAIL)
        self.assertTrue(bundle_id is None)

    def test_successfull_result__is_bot(self):
        _, account_id, _ = logic.register_user('test_user', 'test_user@test.com', '111111', is_bot=True)
        account = prototypes.AccountPrototype.get_by_id(account_id)
        self.assertEqual(account.is_bot, True)

    def test_successfull_result__is_bot_and_fast(self):
        self.assertRaises(exceptions.BotIsFastError, logic.register_user, 'test_user', is_bot=True)
