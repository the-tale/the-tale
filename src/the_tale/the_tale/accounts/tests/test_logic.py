
import smart_imports

smart_imports.all()


class TestLogic(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

    def test_block_expired_accounts(self):
        fast_account = self.accounts_factory.create_account(is_fast=True)
        fast_account._model.created_at = datetime.datetime.fromtimestamp(0)
        fast_account._model.save()

        normal_account = self.accounts_factory.create_account()
        normal_account._model.created_at = datetime.datetime.fromtimestamp(0)
        normal_account._model.save()

        self.assertTrue(achievements_models.AccountAchievements.objects.all().count(), 2)
        self.assertEqual(models.Account.objects.all().count(), 2)
        self.assertEqual(heroes_models.Hero.objects.all().count(), 2)

        logic.block_expired_accounts(logger=logging.getLogger('dummy'))

        self.assertEqual(achievements_models.AccountAchievements.objects.all().count(), 1)
        self.assertEqual(heroes_models.Hero.objects.all().count(), 1)
        self.assertEqual(models.Account.objects.all().count(), 1)

        self.assertEqual(achievements_models.AccountAchievements.objects.filter(id=normal_account.id).count(), 1)
        self.assertEqual(heroes_models.Hero.objects.filter(id=normal_account.id).count(), 1)
        self.assertEqual(models.Account.objects.filter(id=normal_account.id).count(), 1)

    def test_get_account_id_by_email(self):
        self.assertEqual(logic.get_account_id_by_email('bla@bla.bla'), None)
        self.assertEqual(logic.get_account_id_by_email('test_user@test.com'), None)

        account = self.accounts_factory.create_account()

        self.assertEqual(logic.get_account_id_by_email(account.email), account.id)

    def test_initiate_transfer_money(self):
        sender = self.accounts_factory.create_account()
        recipient = self.accounts_factory.create_account()

        with mock.patch('the_tale.common.postponed_tasks.workers.refrigerator.Worker.cmd_wait_task') as cmd_wait_task:
            with self.check_delta(PostponedTaskPrototype._db_count, 1):
                task = logic.initiate_transfer_money(sender_id=sender.id,
                                                     recipient_id=recipient.id,
                                                     amount=1000,
                                                     comment='some comment')

        self.assertTrue(task.internal_logic.state.is_UNPROCESSED)
        self.assertTrue(task.internal_logic.step.is_INITIALIZE)
        self.assertEqual(task.internal_logic.sender_id, sender.id)
        self.assertEqual(task.internal_logic.recipient_id, recipient.id)
        self.assertEqual(task.internal_logic.transfer_transaction, None)
        self.assertEqual(task.internal_logic.commission_transaction, None)
        self.assertEqual(task.internal_logic.comment, 'some comment')
        self.assertEqual(task.internal_logic.amount, int(1000 * (1 - conf.settings.MONEY_SEND_COMMISSION)))
        self.assertEqual(task.internal_logic.commission, 1000 * conf.settings.MONEY_SEND_COMMISSION)


class TestGetAccountInfoLogic(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(self.account.id)

    def test_no_clan(self):
        info = logic.get_account_info(self.account, self.hero)
        self.assertEqual(info['clan'], None)

    def test_has_clan(self):
        forum_prototypes.CategoryPrototype.create(caption='category-1', slug=clans_conf.settings.FORUM_CATEGORY_SLUG, order=0)

        clan = clans_logic.create_clan(self.account, abbr='abbr', name='name', motto='motto', description='description')

        info = logic.get_account_info(self.account, self.hero)
        self.assertEqual(info['clan'],
                         {'id': clan.id,
                          'abbr': clan.abbr,
                          'name': clan.name})


class CardsForNewAccountTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        cards_tt_services.storage.cmd_debug_clear_service()

        self.account = self.accounts_factory.create_account()

        self.expected_cards = [
            cards_types.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(available_for_auction=False,
                                                                      type=cards_types.CARD.CHANGE_HERO_SPENDINGS,
                                                                      item=heroes_relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT),
            cards_types.CARD.HEAL_COMPANION_COMMON.effect.create_card(available_for_auction=False,
                                                                      type=cards_types.CARD.HEAL_COMPANION_COMMON),
            cards_types.CARD.ADD_EXPERIENCE_COMMON.effect.create_card(available_for_auction=False,
                                                                      type=cards_types.CARD.ADD_EXPERIENCE_COMMON),
            cards_types.CARD.CHANGE_ABILITIES_CHOICES.effect.create_card(available_for_auction=False,
                                                                         type=cards_types.CARD.CHANGE_ABILITIES_CHOICES),
            cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                  type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                  preference=heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
            cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                  type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                  preference=heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
            cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                  type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                  preference=heroes_relations.PREFERENCE_TYPE.PLACE),
            cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                  type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                  preference=heroes_relations.PREFERENCE_TYPE.FRIEND),
            cards_types.CARD.ADD_BONUS_ENERGY_RARE.effect.create_card(available_for_auction=False,
                                                                      type=cards_types.CARD.ADD_BONUS_ENERGY_RARE)]

    def test_change_and_load(self):
        cards = cards_tt_services.storage.cmd_get_items(self.account.id)

        self.assertEqual({card.item_full_type for card in cards.values()},
                         {card.item_full_type for card in self.expected_cards})
