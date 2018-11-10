
import smart_imports

smart_imports.all()


class CardsRequestsTestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(CardsRequestsTestsBase, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        tt_services.storage.cmd_debug_clear_service()

        self.card = objects.Card(types.CARD.KEEPERS_GOODS_COMMON, uid=uuid.uuid4())

        self.building_1 = places_logic.create_building(person=self.place_1.persons[0], utg_name=game_names.generator().get_test_name('building-1-name'))


class UseDialogRequestTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_html_ok(self.request_ajax_html(dext_urls.url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['common.login_required'])

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(dext_urls.url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['pgf-error-card.wrong_value'])

    def test_has_cards(self):
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(dext_urls.url('game:cards:use-dialog', card=self.card.uid)))

    def test_every_card(self):
        self.request_login(self.account.email)

        for card_type in types.CARD.records:
            if card_type in (types.CARD.GET_COMPANION_UNCOMMON,
                             types.CARD.GET_COMPANION_RARE,
                             types.CARD.GET_COMPANION_EPIC,
                             types.CARD.GET_COMPANION_LEGENDARY):
                continue

            card = card_type.effect.create_card(available_for_auction=True, type=card_type)
            logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

            self.check_html_ok(self.request_ajax_html(dext_urls.url('game:cards:use-dialog', card=self.card.uid)))


class UseRequestTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(uuid.uuid4().hex), {}), 'common.login_required')

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(uuid.uuid4().hex)), 'card.wrong_value')

    def test_form_invalid(self):
        self.request_login(self.account.email)

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(self.card.uid), {'value': 6666666}), 'form_errors')

    def test_success(self):
        self.request_login(self.account.email)

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        response = self.post_ajax_json(logic.use_card_url(self.card.uid), {'value': self.place_1.id})
        task = PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        task.remove()


class TestIndexRequests(CardsRequestsTestsBase):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_simple(self):
        texts = [card.text for card in types.CARD.records]
        self.check_html_ok(self.request_html(dext_urls.url('guide:cards:')), texts=texts)

    def test_rarity_filter(self):
        for rarity in relations.RARITY.records:
            texts = [card.text for card in types.CARD.records if card.rarity == rarity]
            self.check_html_ok(self.request_html(dext_urls.url('guide:cards:')), texts=texts)

    def test_availability_filter(self):
        for availability in relations.AVAILABILITY.records:
            texts = [card.text for card in types.CARD.records if card.availability == availability]
            self.check_html_ok(self.request_html(dext_urls.url('guide:cards:')), texts=texts)


class GetCardRequestsTests(CardsRequestsTestsBase):

    def setUp(self):
        super(GetCardRequestsTests, self).setUp()

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.receive_cards_url()), 'common.login_required')

    def test_no_new_cards(self):
        self.request_login(self.account.email)

        response = self.post_ajax_json(logic.receive_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(data['cards'], [])

    def test_has_new_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        logic.change_cards(owner_id=self.account.id,
                           operation_type='#test',
                           storage=relations.STORAGE.NEW,
                           to_add=cards)

        response = self.post_ajax_json(logic.receive_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(len(data['cards']), 2)

        self.assertEqual({card.uid.hex for card in cards},
                         {card['uid'] for card in data['cards']})


class CombineCardsRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url()), 'common.login_required')

    def test_created(self):
        self.request_login(self.account.email)

        card_1 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2])

        response = self.post_ajax_json(logic.combine_cards_url(), {'card': [card_1.uid, card_2.uid]})

        account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)

        self.assertEqual(len(account_cards), 1)

        new_card = list(account_cards.values())[0]

        data = self.check_ajax_ok(response)

        self.assertEqual(data['card'], new_card.ui_info())

    def test_wrong_cards(self):
        self.request_login(self.account.email)

        with self.check_not_changed(PostponedTaskPrototype._db_count):
            self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url(), {'card': [uuid.uuid4().hex]}),
                                  'card.wrong_value')


class MoveToStorageRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url()), 'common.login_required')

    def test_move(self):
        self.request_login(self.account.email)
        card_1 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_3 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2, card_3])

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertFalse(any(card['in_storage'] for card in data['cards']))

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card_1.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))

        for card in data['cards']:
            if card['uid'] in (card_1.uid.hex, card_3.uid.hex):
                self.assertTrue(card['in_storage'])
            else:
                self.assertFalse(card['in_storage'])

    def test_already_moved(self):
        self.request_login(self.account.email)
        card = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex]}))
        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertTrue(data['cards'][0]['in_storage'])

    def test_no_card(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url(), {'card': [uuid.uuid4().hex]}), 'card.wrong_value')

    def test_no_card__in_list(self):
        self.request_login(self.account.email)
        card = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_error(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card.uid.hex, uuid.uuid4().hex]}), 'card.wrong_value')


class MoveToHandRequestsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url()), 'common.login_required')

    def test_move(self):
        self.request_login(self.account.email)
        card_1 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_3 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2, card_3])
        self.check_ajax_ok(self.post_ajax_json(logic.move_to_storage_url(), {'card': [card_1.uid.hex, card_2.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertTrue(any(card['in_storage'] for card in data['cards']))

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card_1.uid.hex, card_3.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))

        for card in data['cards']:
            if card['uid'] in (card_1.uid.hex, card_3.uid.hex):
                self.assertFalse(card['in_storage'])
            else:
                self.assertTrue(card['in_storage'])

    def test_already_moved(self):
        self.request_login(self.account.email)
        card = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_ok(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card.uid.hex]}))

        data = self.check_ajax_ok(self.request_json(logic.get_cards_url()))
        self.assertFalse(data['cards'][0]['in_storage'])

    def test_no_card(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url(), {'card': [uuid.uuid4().hex]}), 'card.wrong_value')

    def test_no_card__in_list(self):
        self.request_login(self.account.email)
        card = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card])

        self.check_ajax_error(self.post_ajax_json(logic.move_to_hand_url(), {'card': [card.uid.hex, uuid.uuid4().hex]}), 'card.wrong_value')


class TakeCardCallbackTests(CardsRequestsTestsBase):

    def create_data(self, secret):
        timers = accounts_tt_services.players_timers.cmd_get_owner_timers(self.account.id)

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        return tt_protocol_timers_pb2.CallbackBody(timer=tt_protocol_timers_pb2.Timer(owner_id=self.account.id,
                                                                                      entity_id=0,
                                                                                      type=0,
                                                                                      speed=new_card_timer.speed),
                                                   callback_data='xy',
                                                   secret=secret).SerializeToString()

    def test_no_post_data(self):
        self.check_ajax_error(self.post_ajax_json(dext_urls.url('game:cards:tt-take-card-callback')), 'common.wrong_tt_post_data', status_code=500)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')
        self.check_ajax_error(self.post_ajax_binary(dext_urls.url('game:cards:tt-take-card-callback'), data), 'common.wrong_tt_secret', status_code=500)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_does_not_participate_in_game(self):
        data = self.create_data(secret=django_settings.TT_SECRET)
        self.check_ajax_error(self.post_ajax_binary(dext_urls.url('game:cards:tt-take-card-callback'), data), 'common.player_does_not_participate_in_game')

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    def check_cards_timer_speed(self, speed):
        timers = accounts_tt_services.players_timers.cmd_get_owner_timers(self.account.id)

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        self.assertEqual(new_card_timer.speed, speed)

    def test_premium(self):

        self.check_cards_timer_speed(tt_cards_constants.NORMAL_PLAYER_SPEED)

        self.account.prolong_premium(30)
        self.account.save()

        data = self.create_data(secret=django_settings.TT_SECRET)
        self.check_ajax_ok(self.post_ajax_binary(dext_urls.url('game:cards:tt-take-card-callback'), data))

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 1)
        self.assertTrue(list(cards.values())[0].storage.is_NEW)
        self.assertTrue(list(cards.values())[0].available_for_auction)

        self.check_cards_timer_speed(tt_cards_constants.PREMIUM_PLAYER_SPEED)

    def test_not_premium(self):

        accounts_tt_services.players_timers.cmd_change_timer_speed(owner_id=self.account.id,
                                                                   speed=tt_cards_constants.PREMIUM_PLAYER_SPEED,
                                                                   type=accounts_relations.PLAYER_TIMERS_TYPES.CARDS_MINER)

        self.check_cards_timer_speed(tt_cards_constants.PREMIUM_PLAYER_SPEED)

        data = self.create_data(secret=django_settings.TT_SECRET)
        self.check_ajax_ok(self.post_ajax_binary(dext_urls.url('game:cards:tt-take-card-callback'), data))

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 1)
        self.assertTrue(list(cards.values())[0].storage.is_NEW)
        self.assertFalse(list(cards.values())[0].available_for_auction)

        self.check_cards_timer_speed(tt_cards_constants.NORMAL_PLAYER_SPEED)


class GetCardsTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_ajax_error(self.request_ajax_json(logic.get_cards_url()), 'common.login_required')

    def test_no_cards(self):
        self.request_login(self.account.email)

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(data['cards'], [])
        self.assertEqual(data['new_cards'], 0)
        self.assertEqual(data['new_card_timer'], {'border': tt_cards_constants.RECEIVE_TIME,
                                                  'finish_at': data['new_card_timer']['finish_at'],
                                                  'id': data['new_card_timer']['id'],
                                                  'owner_id': self.account.id,
                                                  'resources': 0.0,
                                                  'resources_at': data['new_card_timer']['resources_at'],
                                                  'speed': 1.0,
                                                  'type': accounts_relations.PLAYER_TIMERS_TYPES.CARDS_MINER.value})

    def test_has_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        logic.change_cards(owner_id=self.account.id,
                           operation_type='#test',
                           storage=relations.STORAGE.FAST,
                           to_add=cards)

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)
        self.assertEqual(len(data['cards']), 2)

        self.assertEqual({card.uid.hex for card in cards},
                         {card['uid'] for card in data['cards']})

    def test_has_not_received_cards(self):
        self.request_login(self.account.email)

        cards = [logic.create_card(allow_premium_cards=True, available_for_auction=True),
                 logic.create_card(allow_premium_cards=True, available_for_auction=True)]

        logic.change_cards(owner_id=self.account.id,
                           operation_type='#test',
                           storage=relations.STORAGE.NEW,
                           to_add=cards)

        visible_card = logic.create_card(allow_premium_cards=True, available_for_auction=True)

        logic.change_cards(owner_id=self.account.id,
                           operation_type='#test',
                           storage=relations.STORAGE.FAST,
                           to_add=[visible_card])

        response = self.request_ajax_json(logic.get_cards_url())

        data = self.check_ajax_ok(response)

        self.assertEqual(data['new_cards'], 2)
        self.assertEqual(len(data['cards']), 1)

        self.assertEqual(visible_card.uid.hex, data['cards'][0]['uid'])
