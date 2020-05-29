
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
        self.check_html_ok(self.request_ajax_html(utils_urls.url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['common.login_required'])

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(utils_urls.url('game:cards:use-dialog', card=uuid.uuid4().hex)), texts=['pgf-error-card.wrong_value'])

    def test_has_cards(self):
        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[self.card])

        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(utils_urls.url('game:cards:use-dialog', card=self.card.uid)))

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

            self.check_html_ok(self.request_ajax_html(utils_urls.url('game:cards:use-dialog', card=self.card.uid)))


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
        self.check_html_ok(self.request_html(utils_urls.url('guide:cards:')), texts=texts)

    def test_rarity_filter(self):
        for rarity in relations.RARITY.records:
            texts = [card.text for card in types.CARD.records if card.rarity == rarity]
            self.check_html_ok(self.request_html(utils_urls.url('guide:cards:')), texts=texts)

    def test_availability_filter(self):
        for availability in relations.AVAILABILITY.records:
            texts = [card.text for card in types.CARD.records if card.availability == availability]
            self.check_html_ok(self.request_html(utils_urls.url('guide:cards:')), texts=texts)


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

        self.assertEqual(data['cards'], [new_card.ui_info()])

    def test_created__old_api(self):
        self.request_login(self.account.email)

        card_1 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())
        card_2 = objects.Card(types.CARD.ADD_GOLD_COMMON, uid=uuid.uuid4())

        logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2])

        response = self.post_ajax_json(logic.combine_cards_url(api_version='2.0'), {'card': [card_1.uid, card_2.uid]})

        account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)

        self.assertEqual(len(account_cards), 1)

        new_card = list(account_cards.values())[0]

        data = self.check_ajax_ok(response)

        self.assertEqual(data['card'], new_card.ui_info())

    def test_created__no_premium_cards(self):
        # account always use personal_only mode for not premium players
        self.assertTrue(self.account._model.cards_receive_mode.is_ALL)
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

        self.request_login(self.account.email)

        card_type = types.CARD.ADD_GOLD_COMMON
        self.assertTrue(card_type.availability.is_FOR_PREMIUMS)

        for i in range(100):
            card_1 = objects.Card(card_type, uid=uuid.uuid4())
            card_2 = objects.Card(card_type, uid=uuid.uuid4())

            logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2])

            response = self.post_ajax_json(logic.combine_cards_url(), {'card': [card_1.uid, card_2.uid]})

            account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)

            self.assertEqual(len(account_cards), 1)

            new_card = list(account_cards.values())[0]

            self.assertTrue(new_card.type.availability.is_FOR_ALL)

            data = self.check_ajax_ok(response)

            self.assertEqual(data['cards'], [new_card.ui_info()])

            tt_services.storage.cmd_debug_clear_service()

    def test_created__allow_premium_cards(self):
        self.account.prolong_premium(30)
        self.account.set_cards_receive_mode(relations.RECEIVE_MODE.ALL)
        self.account.save()

        self.request_login(self.account.email)

        card_type = types.CARD.ADD_GOLD_COMMON
        self.assertTrue(card_type.availability.is_FOR_PREMIUMS)

        premium_constructed = False

        for i in range(100):
            card_1 = objects.Card(card_type, uid=uuid.uuid4())
            card_2 = objects.Card(card_type, uid=uuid.uuid4())

            logic.change_cards(self.hero.account_id, operation_type='#test', to_add=[card_1, card_2])

            response = self.post_ajax_json(logic.combine_cards_url(), {'card': [card_1.uid, card_2.uid]})

            account_cards = tt_services.storage.cmd_get_items(self.hero.account_id)

            self.assertEqual(len(account_cards), 1)

            new_card = list(account_cards.values())[0]

            premium_constructed = premium_constructed or new_card.type.availability.is_FOR_PREMIUMS

            data = self.check_ajax_ok(response)

            self.assertEqual(data['cards'], [new_card.ui_info()])

            tt_services.storage.cmd_debug_clear_service()

        self.assertTrue(premium_constructed)

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


class TakeCardCallbackTests(CardsRequestsTestsBase, tt_api_testcase.TestCaseMixin):

    def setUp(self):
        super().setUp()

        self.postprocess_remove = tt_protocol_timers_pb2.CallbackAnswer.PostprocessType.Value('REMOVE')
        self.postprocess_restart = tt_protocol_timers_pb2.CallbackAnswer.PostprocessType.Value('RESTART')

    def create_data(self, secret, account_id=None):
        if account_id is None:
            account_id = self.account.id

        timers = accounts_tt_services.players_timers.cmd_get_owner_timers(account_id)

        new_card_timer = None

        for timer in timers:
            if timer.type.is_CARDS_MINER:
                new_card_timer = timer
                break

        speed = new_card_timer.speed if new_card_timer else 666

        return tt_protocol_timers_pb2.CallbackBody(timer=tt_protocol_timers_pb2.Timer(owner_id=account_id,
                                                                                      entity_id=0,
                                                                                      type=0,
                                                                                      speed=speed),
                                                   callback_data='xy',
                                                   secret=secret).SerializeToString()

    def test_no_post_data(self):
        self.check_ajax_error(self.post_ajax_json(utils_urls.url('game:cards:tt-take-card-callback')), 'common.wrong_tt_post_data', status_code=500)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    def test_wrong_secret_key(self):
        data = self.create_data(secret='wrong.secret')
        self.check_ajax_error(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data), 'common.wrong_tt_secret', status_code=500)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_no_account(self):
        account_id = 9999999

        data = self.create_data(secret=django_settings.TT_SECRET, account_id=account_id)
        answer = self.check_protobuf_ok(self.post_protobuf(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                        answer_type=tt_protocol_timers_pb2.CallbackAnswer)

        self.assertEqual(answer.postprocess_type, self.postprocess_remove)

        cards = tt_services.storage.cmd_get_items(account_id)
        self.assertEqual(cards, {})

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_account_removed(self):
        tt_services.storage.cmd_debug_clear_service()

        accounts_data_protection.first_step_removing(self.account)

        data = self.create_data(secret=django_settings.TT_SECRET,)
        answer = self.check_protobuf_ok(self.post_protobuf(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                        answer_type=tt_protocol_timers_pb2.CallbackAnswer)

        self.assertEqual(answer.postprocess_type, self.postprocess_remove)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(cards, {})

    @mock.patch('tt_logic.common.checkers.is_player_participate_in_game', mock.Mock(return_value=False))
    def test_does_not_participate_in_game(self):
        data = self.create_data(secret=django_settings.TT_SECRET)
        answer = self.check_protobuf_ok(self.post_protobuf(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                        answer_type=tt_protocol_timers_pb2.CallbackAnswer)

        self.assertEqual(answer.postprocess_type, self.postprocess_restart)

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
        self.account.set_cards_receive_mode(relations.RECEIVE_MODE.ALL)
        self.account.save()

        tt_services.storage.cmd_debug_clear_service()

        data = self.create_data(secret=django_settings.TT_SECRET)
        answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                        answer_type=tt_protocol_timers_pb2.CallbackAnswer)

        self.assertEqual(answer.postprocess_type, self.postprocess_restart)

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
        answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                        answer_type=tt_protocol_timers_pb2.CallbackAnswer)

        self.assertEqual(answer.postprocess_type, self.postprocess_restart)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 1)
        self.assertTrue(list(cards.values())[0].storage.is_NEW)
        self.assertFalse(list(cards.values())[0].available_for_auction)

        self.check_cards_timer_speed(tt_cards_constants.NORMAL_PLAYER_SPEED)

    def test_no_premium_cards_for_not_premium_player(self):

        # account always use personal_only mode for not premium players
        self.assertTrue(self.account._model.cards_receive_mode.is_ALL)
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

        accounts_tt_services.players_timers.cmd_change_timer_speed(owner_id=self.account.id,
                                                                   speed=tt_cards_constants.PREMIUM_PLAYER_SPEED,
                                                                   type=accounts_relations.PLAYER_TIMERS_TYPES.CARDS_MINER)

        self.check_cards_timer_speed(tt_cards_constants.PREMIUM_PLAYER_SPEED)

        for i in range(100):
            data = self.create_data(secret=django_settings.TT_SECRET)
            answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                            answer_type=tt_protocol_timers_pb2.CallbackAnswer)

            self.assertEqual(answer.postprocess_type, self.postprocess_restart)

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 100)

        for card in cards.values():
            self.assertFalse(card.available_for_auction)
            self.assertTrue(card.type.availability.is_FOR_ALL)

    def test_premium_cards_for_premium_player(self):

        self.check_cards_timer_speed(tt_cards_constants.NORMAL_PLAYER_SPEED)

        self.account.prolong_premium(30)
        self.account.set_cards_receive_mode(relations.RECEIVE_MODE.ALL)
        self.account.save()

        tt_services.storage.cmd_debug_clear_service()

        for i in range(100):
            data = self.create_data(secret=django_settings.TT_SECRET)
            answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                            answer_type=tt_protocol_timers_pb2.CallbackAnswer)

            self.assertEqual(answer.postprocess_type, self.postprocess_restart)

        card_types = set()

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 100)

        for card in cards.values():
            card_types.add(card.type.availability)

        self.assertEqual(card_types,
                         {relations.AVAILABILITY.FOR_ALL,
                          relations.AVAILABILITY.FOR_PREMIUMS})

    def test_only_not_premium_cards_for_premium_player(self):

        self.check_cards_timer_speed(tt_cards_constants.NORMAL_PLAYER_SPEED)

        self.account.prolong_premium(30)
        self.account.set_cards_receive_mode(relations.RECEIVE_MODE.PERSONAL_ONLY)
        self.account.save()

        tt_services.storage.cmd_debug_clear_service()

        for i in range(100):
            data = self.create_data(secret=django_settings.TT_SECRET)
            answer = self.check_protobuf_ok(self.post_ajax_binary(utils_urls.url('game:cards:tt-take-card-callback'), data),
                                            answer_type=tt_protocol_timers_pb2.CallbackAnswer)

            self.assertEqual(answer.postprocess_type, self.postprocess_restart)

        card_types = set()

        cards = tt_services.storage.cmd_get_items(self.account.id)
        self.assertEqual(len(cards), 100)

        for card in cards.values():
            card_types.add(card.type.availability)

        self.assertEqual(card_types,
                         {relations.AVAILABILITY.FOR_ALL})


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


class ChangeReceiveModeRequestTests(CardsRequestsTestsBase):

    def setUp(self):
        super().setUp()

        self.url_personal_only = logic.change_receive_mode_url(relations.RECEIVE_MODE.PERSONAL_ONLY)
        self.url_all = logic.change_receive_mode_url(relations.RECEIVE_MODE.ALL)

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(self.url_all, {}), 'common.login_required')

    def test_not_premium(self):
        self.request_login(self.account.email)

        self.check_ajax_error(self.post_ajax_json(self.url_all, {}), 'common.premium_account')

    def test_success(self):
        self.request_login(self.account.email)

        self.account.prolong_premium(30)
        self.account.save()

        self.assertTrue(self.account.cards_receive_mode().is_ALL)

        self.check_ajax_ok(self.post_ajax_json(self.url_personal_only))
        self.account.reload()
        self.assertTrue(self.account.cards_receive_mode().is_PERSONAL_ONLY)

        self.check_ajax_ok(self.post_ajax_json(self.url_all))
        self.account.reload()
        self.assertTrue(self.account.cards_receive_mode().is_ALL)
