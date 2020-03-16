
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

        logic.block_expired_accounts(logger=mock.Mock())

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

        for _ in range(5):
            self.expected_cards.append(cards_types.CARD.STOP_IDLENESS.effect.create_card(available_for_auction=False,
                                                                                         type=cards_types.CARD.STOP_IDLENESS))

    def test_change_and_load(self):
        cards = cards_tt_services.storage.cmd_get_items(self.account.id)

        self.assertEqual({card.item_full_type for card in cards.values()},
                         {card.item_full_type for card in self.expected_cards})


class ChangeCredentialsTests(utils_testcase.TestCase, personal_messages_helpers.Mixin):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.fast_account = self.accounts_factory.create_account(is_fast=True)

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_change_credentials(self):
        self.assertTrue(prototypes.AccountPrototype.get_by_id(self.fast_account.id).is_fast)

        cards_tt_services.storage.cmd_debug_clear_service()

        with self.check_delta(lambda: len(cards_tt_services.storage.cmd_get_items(self.fast_account.id)),
                              conf.settings.FREE_CARDS_FOR_REGISTRATION), \
             mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as fake_cmd, \
             mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
                logic.change_credentials(account=self.fast_account,
                                         new_email='fast_user@test.ru',
                                         new_password=django_auth_hashers.make_password('222222'),
                                         new_nick='test_nick')

        self.assertEqual(cmd_run_account_method.call_count, 0)

        self.assertEqual(django_auth.authenticate(nick='test_nick', password='222222').id, self.fast_account.id)
        self.assertFalse(prototypes.AccountPrototype.get_by_id(self.fast_account.id).is_fast)
        self.assertEqual(fake_cmd.call_count, 1)
        self.assertFalse(fake_cmd.call_args[1]['is_fast'])

        cards = list(cards_tt_services.storage.cmd_get_items(self.fast_account.id).values())

        self.assertTrue(all(card.type.availability.is_FOR_ALL for card in cards))
        self.assertFalse(all(card.available_for_auction for card in cards))

    def test_change_credentials__not_registration(self):
        self.assertFalse(prototypes.AccountPrototype.get_by_id(self.account.id).is_fast)

        cards_tt_services.storage.cmd_debug_clear_service()

        with self.check_not_changed(lambda: len(cards_tt_services.storage.cmd_get_items(self.account.id))), \
             mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as fake_cmd, \
             mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
                logic.change_credentials(account=self.account,
                                         new_email='x_user@test.ru',
                                         new_password=django_auth_hashers.make_password('222222'),
                                         new_nick='test_nick')

        self.assertEqual(django_auth.authenticate(nick='test_nick', password='222222').id, self.account.id)
        self.assertFalse(prototypes.AccountPrototype.get_by_id(self.account.id).is_fast)
        self.assertEqual(fake_cmd.call_count, 0)

    def test_change_credentials__with_referral(self):
        self.fast_account._model.referral_of = self.account._model
        self.fast_account.save()

        self.assertTrue(prototypes.AccountPrototype.get_by_id(self.fast_account.id).is_fast)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as fake_cmd:
            with mock.patch('the_tale.accounts.workers.accounts_manager.Worker.cmd_run_account_method') as cmd_run_account_method:
                logic.change_credentials(account=self.fast_account,
                                         new_email='fast_user@test.ru',
                                         new_password=django_auth_hashers.make_password('222222'),
                                         new_nick='test_nick')

        self.assertEqual(cmd_run_account_method.call_count, 1)
        self.assertEqual(cmd_run_account_method.call_args, mock.call(account_id=self.account.id,
                                                                     method_name=prototypes.AccountPrototype.update_referrals_number.__name__,
                                                                     data={}))

        self.assertEqual(django_auth.authenticate(nick='test_nick', password='222222').id, self.fast_account.id)
        self.assertFalse(prototypes.AccountPrototype.get_by_id(self.fast_account.id).is_fast)
        self.assertEqual(fake_cmd.call_count, 1)
        self.assertFalse(fake_cmd.call_args[1]['is_fast'])

    def test_change_credentials_password(self):
        nick = self.account.nick
        email = self.account.email

        logic.change_credentials(account=self.account,
                                 new_password=django_auth_hashers.make_password('222222'))

        self.assertEqual(post_service_models.Message.objects.all().count(), 0)

        self.assertEqual(self.account.email, email)
        user = django_auth.authenticate(nick=nick, password='222222')
        self.assertEqual(user.id, self.account.id)

    def test_change_credentials_nick(self):

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_update_hero_with_account_data') as fake_cmd:
            logic.change_credentials(account=self.account,
                                     new_nick='test_nick')

        self.assertEqual(post_service_models.Message.objects.all().count(), 0)
        self.assertEqual(fake_cmd.call_count, 0)
        self.assertEqual(django_auth.authenticate(nick='test_nick', password='111111').id, self.account.id)

    def test_change_credentials_email(self):
        nick = self.account.nick

        logic.change_credentials(account=self.account,
                                 new_email='test_user@test.ru')

        self.assertEqual(post_service_models.Message.objects.all().count(), 0)

        self.assertEqual(self.account.email, 'test_user@test.ru')
        self.assertEqual(django_auth.authenticate(nick=nick, password='111111').id, self.account.id)
        self.assertEqual(django_auth.authenticate(nick=nick, password='111111').nick, nick)


class MaxMoneyToTransferTests(bank_helpers.BankTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        bank_prototypes.AccountPrototype.get_for_or_create(entity_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                           entity_id=self.account.id,
                                                           currency=bank_relations.CURRENCY_TYPE.PREMIUM)

    def test_no_transactions(self):
        self.assertEqual(logic.max_money_to_transfer(self.account), 0)

    def prepair_data(self, account_2, account_3):
        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=self.account.id,
                            sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                            sender_id=0,
                            amount=1,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=xsolla_prototypes.BANK_OPERATION_UID)

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=self.account.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                            sender_id=0,
                            amount=10,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=shop_goods.PURCHAGE_UID.format(shop_price_list.SUBSCRIPTION_INFINIT_UID))

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=account_2.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=self.account.id,
                            amount=100,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=accounts_postponed_tasks.TRANSFER_MONEY_UID)

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=self.account.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=account_3.id,
                            amount=1000,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=accounts_postponed_tasks.TRANSFER_MONEY_UID)

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=account_2.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=self.account.id,
                            amount=10000,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid='xxx-yyy')

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=self.account.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=account_3.id,
                            amount=1000000,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid='zzz-xxx')

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=account_2.id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=account_3.id,
                            amount=10000000,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=accounts_postponed_tasks.TRANSFER_MONEY_UID)

    def test_complex_history(self):
        self.prepair_data(account_2=self.accounts_factory.create_account(),
                          account_3=self.accounts_factory.create_account())

        self.assertEqual(logic.max_money_to_transfer(self.account), 1 - 10 - 100 + 1000)

    def test_complex_history__multiple_transactions(self):
        self.prepair_data(account_2=self.accounts_factory.create_account(),
                          account_3=self.accounts_factory.create_account())

        self.prepair_data(account_2=self.accounts_factory.create_account(),
                          account_3=self.accounts_factory.create_account())

        self.assertEqual(logic.max_money_to_transfer(self.account), 2 * (1 - 10 - 100 + 1000))

    def test_complex_history__below_zero(self):
        self.prepair_data(account_2=self.accounts_factory.create_account(),
                          account_3=self.accounts_factory.create_account())

        self.create_invoice(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            recipient_id=self.accounts_factory.create_account().id,
                            sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                            sender_id=self.account.id,
                            amount=6666666,
                            state=bank_relations.INVOICE_STATE.CONFIRMED,
                            operation_uid=accounts_postponed_tasks.TRANSFER_MONEY_UID)

        self.assertEqual(logic.max_money_to_transfer(self.account), 1 - 10 - 100 + 1000 - 6666666)
