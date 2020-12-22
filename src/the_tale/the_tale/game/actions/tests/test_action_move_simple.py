import smart_imports

smart_imports.all()


def get_fast_transportation_points(clan_id, place_id):
    resource_id = emissaries_logic.resource_id(clan_id=clan_id,
                                               place_id=place_id)

    return emissaries_tt_services.events_currencies.cmd_balance(resource_id,
                                                                currency=emissaries_relations.EVENT_CURRENCY.FAST_TRANSPORTATION)


class MoveSimpleTests(clans_helpers.ClansTestsMixin,
                      utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action
        self.action_idl.state = self.action_idl.STATE.WAITING  # skip first steps

        self.hero.position.set_place(self.place_1)

        self.path = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                                to_x=self.place_2.x, to_y=self.place_2.y)

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=None)

    def test_create(self):
        self.assertEqual(self.action_move.path, self.path)
        self.assertEqual(self.action_move.destination, self.place_2)
        self.assertEqual(self.action_move.break_at, None)
        self.assertEqual(self.action_move.percents, 0)

    def test_full_move(self):
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        visited_cells = set()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            visited_cells.add((self.hero.position.cell_x, self.hero.position.cell_y))

        self.assertEqual(visited_cells, set(self.path._cells))

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_modify_speed(self):
        steps_count_1 = 0
        steps_count_2 = 0

        while len(self.hero.actions.actions_list) != 1:
            steps_count_1 += 1
            self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=None)

        while len(self.hero.actions.actions_list) != 1:
            steps_count_2 += 1
            with mock.patch('the_tale.game.heroes.objects.Hero.modify_move_speed',
                             mock.Mock(return_value=self.hero.move_speed * 3)):
                self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(steps_count_2 * 2 < steps_count_1)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_picked_up_in_road', lambda self: True)
    def test_picked_up(self):
        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.assertTrue(self.action_move.percents > 0)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_PICKED_UP_IN_ROAD)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_fly_probability', 1.0)
    def test_teleport_by_flying_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_FLY)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion__from_place(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertTrue(any(message.key.is_COMPANIONS_TELEPORT
                            for message in self.hero.journal.messages
                            if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 0)
    def test_teleport_by_teleportator_companion__from_place__no_teleportation(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.action_move.place_hero_in_current_place(create_action=False)

        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertNotEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, None)

        self.assertFalse(any(message.key.is_COMPANIONS_TELEPORT
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion__from_start(self):

        self.hero.actions.pop_action()

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=None)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertTrue(any(message.key.is_COMPANIONS_TELEPORT
                            for message in self.hero.journal.messages
                            if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 0.0)
    def test_teleport_by_teleportator_companion__from_start_no_teleportation(self):

        self.hero.actions.pop_action()

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=None)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertNotEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, None)

        self.assertFalse(any(message.key.is_COMPANIONS_TELEPORT
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport(self):

        with self.check_increased(lambda: self.action_move.percents):
            result = self.action_move.teleport(1,
                                               create_inplace_action=True,
                                               check_moving_state=False)

        self.assertTrue(result)

        self.action_move.teleport(100500,
                                  create_inplace_action=True,
                                  check_moving_state=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__zero_length_path(self):

        self.action_move.path = navigation_path.Path(cells=[(self.place_1.x, self.place_1.y)])

        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        with self.check_not_changed(lambda: self.action_move.percents):
            result = self.action_move.teleport(1, create_inplace_action=True)

        self.assertFalse(result)

        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__zero_length_path__moving_state(self):

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=navigation_path.Path(cells=[(0.5, 0.5)]),
                                                                       destination=None,
                                                                       break_at=None)

        with self.check_not_changed(lambda: self.action_move.percents):
            result = self.action_move.teleport(1, create_inplace_action=True)

        self.assertFalse(result)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__not_moving_state(self):

        self.action_move.state = self.action_move.STATE.IN_CITY

        with self.check_not_changed(lambda: self.action_move.percents):
            self.action_move.teleport(1, create_inplace_action=True)

        result = self.action_move.teleport(self.action_move.path.length, create_inplace_action=True)

        self.assertFalse(result)

        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_place(self):
        self.assertEqual(self.hero.actions.current_action.state,
                         prototypes.ActionMoveSimplePrototype.STATE.IN_CITY)
        self.assertNotEqual(self.hero.position.place_id, None)

        result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                    check_moving_state=False)

        self.assertTrue(result)
        self.assertEqual(self.hero.position.place.id, self.place_2.id)

        self.assertEqual(self.action_move.percents, 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__not_from_place(self):
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)

        result = self.action_move.teleport_to_place(create_inplace_action=True)
        self.assertTrue(result)

        self.assertEqual(self.hero.position.place.id, self.place_2.id)

        self.assertEqual(self.action_move.percents, 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__not_moving_state(self):
        self.action_move.state = self.action_move.STATE.IN_CITY

        result = self.action_move.teleport_to_place(create_inplace_action=True)

        self.assertFalse(result)

        self.assertEqual(self.hero.position.place.id, self.place_1.id)

        self.assertEqual(self.action_move.percents, 0)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__to_middle_place(self):
        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)
        self.action_move.path.append(path_2)

        self.assertEqual(self.hero.actions.current_action.state,
                         prototypes.ActionMoveSimplePrototype.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.action_move.teleport_to_place(create_inplace_action=True, check_moving_state=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertTrue(0 < self.action_move.percents < 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

        while self.action_move.state != self.action_move.STATE.MOVING:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.action_move.teleport_to_place(create_inplace_action=True)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)

        self.assertEqual(self.action_move.percents, 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end(self):
        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        result = self.action_move.teleport_to_end()

        self.assertTrue(result)

        self.assertEqual(self.hero.position.place.id, self.place_3.id)

        self.assertEqual(self.action_move.percents, 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end__not_moving_state(self):
        self.action_move.state = self.action_move.STATE.IN_CITY

        result = self.action_move.teleport_to_end()

        self.assertFalse(result)

        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        self.assertEqual(self.action_move.percents, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__length_is_0(self):

        self.action_move.percents = 1
        self.hero.position.set_place(self.place_2)

        with self.check_not_changed(lambda: self.action_move.percents):
            self.action_move.teleport(1, create_inplace_action=True)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__create_inplace_action(self):
        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.action_move.teleport(distance=100500,
                                  create_inplace_action=True,
                                  check_moving_state=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertTrue(0 < self.action_move.percents < 1)
        self.assertFalse(self.action_move.leader)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__does_not_create_inplace_action(self):
        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.action_move.teleport(distance=100500,
                                  create_inplace_action=False,
                                  check_moving_state=False)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)

        self.assertEqual(self.action_move.percents, 1)
        self.assertTrue(self.action_move.leader)

    def prepair_clan(self):
        self.prepair_forum_for_clans()
        clan = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan.id

        return clan

    def test_teleport_by_clan(self):
        self.prepair_clan()

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.assertTrue(self.action_move.teleport_with_clan())

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_by_clan__from_place_from_moving_state(self):
        clan = self.prepair_clan()

        self.hero.journal.messages.clear()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertNotEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, None)

        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_by_clan__from_place_from_in_city_state(self):
        clan = self.prepair_clan()

        self.action_move.place_hero_in_current_place(create_action=False)

        self.hero.journal.messages.clear()

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 1)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)

        self.assertTrue(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                            for message in self.hero.journal.messages
                            if message.key is not None))

    def test_teleport_by_clan__no_next_place(self):
        clan = self.prepair_clan()

        self.place_1.attrs.fast_transportation.add(clan.id)

        path_2 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_1.x+1, to_y=self.place_1.y+1)

        self.action_move.path = path_2

        self.assertFalse(self.action_move.teleport_with_clan())

        self.assertEqual(self.hero.position.place_id, self.place_1.id)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_try_to_teleport_by_clan(self):
        clan = self.prepair_clan()
        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.path.append(path_2)

        with self.check_delta(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=self.path,
                                                        destination=self.place_3,
                                                        break_at=None)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_teleport_by_clan__not_from_place(self):
        clan = self.prepair_clan()
        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=self.place_2,
                                                        break_at=None)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_teleport_by_clan__wrong_clan(self):
        clan = self.prepair_clan()
        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=self.place_2,
                                                        break_at=None)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: True)
    def test_battle(self):
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionBattlePvE1x1Prototype.TYPE)
        self.storage._test_save()

    def test_rest(self):
        self.hero.health = 1
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRestPrototype.TYPE)

        self.storage._test_save()

    def test_religion_ceremony_on_move(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.RELIGION_TYPE, heroes_relations.RELIGION_TYPE.PRAY)
        self.hero.last_religion_action_at_turn -= max(next(zip(*heroes_relations.RELIGION_TYPE.select('period'))))

        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionReligionCeremonyPrototype.TYPE)

        self.storage._test_save()

    def test_not_religion_ceremony_on_move_for_sacrifice(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.RELIGION_TYPE, heroes_relations.RELIGION_TYPE.SACRIFICE)
        self.hero.last_religion_action_at_turn -= max(next(zip(*heroes_relations.RELIGION_TYPE.select('period'))))

        self.action_move.state = self.action_move.STATE.MOVING

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertNotEqual(self.hero.actions.current_action.TYPE, prototypes.ActionReligionCeremonyPrototype.TYPE)

        self.storage._test_save()

    def test_religion_ceremony_after_battle_for_sacrifice(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.RELIGION_TYPE, heroes_relations.RELIGION_TYPE.SACRIFICE)
        self.hero.last_religion_action_at_turn -= max(next(zip(*heroes_relations.RELIGION_TYPE.select('period'))))

        self.action_move.state = self.action_move.STATE.BATTLE

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionReligionCeremonyPrototype.TYPE)

        self.storage._test_save()

    def test_resurrect(self):
        self.hero.kill()
        self.action_move.state = self.action_move.STATE.BATTLE
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionResurrectPrototype.TYPE)
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_inplace(self):
        self.action_move.percents = 0.99999
        self.hero.position.set_position(*self.action_move.path.coordinates(self.action_move.percents))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_stop_when_quest_required_replane(self):
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with mock.patch('the_tale.game.quests.container.QuestsContainer.has_quests', True):
            self.storage.process_turn(continue_steps_if_needed=False)
            self.assertFalse(self.action_move.replane_required)
            self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
            self.action_move.replane_required = True
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.PROCESSED)

    @mock.patch('the_tale.game.companions.objects.Companion.need_heal', True)
    def test_hero_need_heal_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_move.state, self.action_move.STATE.HEALING_COMPANION)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.companions.objects.Companion.need_heal', True)
    def test_hero_need_heal_companion__battle(self):
        self.action_move.state = self.action_move.STATE.BATTLE

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionHealCompanionPrototype.TYPE)
        self.assertEqual(self.action_move.state, self.action_move.STATE.HEALING_COMPANION)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_move_when_real_length_is_zero(self):
        self.action_move.percents = 0
        self.hero.position.set_place(self.action_move.destination)

        self.action_move.path._cells = [self.action_move.path.destination_coordinates()]
        self.action_move.path.length = 0

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 1)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_say_wisdom', lambda hero: True)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_EXP_PER_MOVE_PROBABILITY', 1.0)
    def test_companion_say_wisdom(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with self.check_delta(lambda: self.hero.experience, c.COMPANIONS_EXP_PER_MOVE_GET_EXP):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(any(message.key.is_COMPANIONS_SAY_WISDOM for message in self.hero.journal.messages))

        self.storage._test_save()

    def test_teleport_by_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.assertTrue(self.action_move.teleport_with_clan())

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    def test_teleport_by_clan__no_next_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        path_2 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_1.x+1, to_y=self.place_1.y+1)

        self.action_move.path = path_2

        self.assertFalse(self.action_move.teleport_with_clan())

        self.assertEqual(self.hero.position.place_id, self.place_1.id)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_try_to_teleport_by_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.path.append(path_2)

        with self.check_delta(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=self.path,
                                                        destination=self.place_3,
                                                        break_at=None)
            self.assertEqual(self.hero.actions.current_action.state,
                             prototypes.ActionMoveSimplePrototype.STATE.IN_CITY)
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_by_clan__not_from_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                    path=path_2,
                                                    destination=self.place_2,
                                                    break_at=None)

        self.assertEqual(self.hero.actions.current_action.state,
                         prototypes.ActionMoveSimplePrototype.STATE.MOVING)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.state,
                         prototypes.ActionMoveSimplePrototype.STATE.MOVING)

        self.assertEqual(self.hero.position.place_id, None)

        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))

    def test_teleport_by_clan__wrong_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id+1)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=self.place_2,
                                                        break_at=None)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))


class MoveSimpleNoDestinationTests(clans_helpers.ClansTestsMixin,
                                   utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action
        self.action_idl.state = self.action_idl.STATE.WAITING  # skip first steps

        self.hero.position.set_place(self.place_1)

        self.path = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                                to_x=self.place_1.x+1, to_y=self.place_1.y+1)

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=None,
                                                                       break_at=None)

    def check_finish_position(self):
        self.assertEqual(self.hero.position.place_id, None)
        self.assertEqual(self.hero.position.x, self.place_1.x+1)
        self.assertEqual(self.hero.position.y, self.place_1.y+1)

    def test_create(self):
        self.assertEqual(self.action_move.path, self.path)
        self.assertEqual(self.action_move.destination, None)
        self.assertEqual(self.action_move.break_at, None)
        self.assertEqual(self.action_move.percents, 0)

    def test_full_move(self):
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        visited_cells = set()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            visited_cells.add((self.hero.position.cell_x, self.hero.position.cell_y))

        self.assertEqual(visited_cells, set(self.path._cells))

        self.check_finish_position()

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_picked_up_in_road', lambda self: True)
    def test_picked_up(self):
        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.action_move.percents > 0)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_fly_probability', 1.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_FLY_DISTANCE', 0.5)
    def test_teleport_by_flying_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(0 < self.action_move.percents < 1)
        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_FLY)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 0.0)
    def test_teleport_by_teleportator_companion__no_place_found(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)

        with mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertTrue(0 < self.action_move.percents < 1)

        self.assertEqual(self.hero.position.place_id, None)

        self.assertFalse(any(message.key.is_COMPANIONS_TELEPORT
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport(self):

        with self.check_increased(lambda: self.action_move.percents):
            self.action_move.teleport(1,
                                      create_inplace_action=True,
                                      check_moving_state=False)

        result = self.action_move.teleport(self.action_move.path.length,
                                           create_inplace_action=True,
                                           check_moving_state=False)

        self.assertTrue(result)

        self.check_finish_position()

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_place(self):
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                    check_moving_state=False)

        self.assertFalse(result)

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.action_move.percents, 0)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_moving(self):
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)

        with self.check_not_changed(lambda: self.action_move.percents):
            result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                        check_moving_state=False)

        self.assertFalse(result)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_moving_state(self):
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)

        with self.check_not_changed(lambda: self.action_move.percents):
            result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                        check_moving_state=False)

        self.assertFalse(result)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end(self):
        result = self.action_move.teleport_to_end(check_moving_state=False)

        self.assertTrue(result)

        self.check_finish_position()

        self.assertEqual(self.action_move.percents, 1)
        self.assertTrue(self.action_move.leader)
        self.assertTrue(self.action_move.state, self.action_move.STATE.PROCESSED)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_move_when_real_length_is_zero(self):
        self.action_move.percents = 0
        self.hero.position.set_position(*self.path.destination_coordinates())

        self.action_move.path._cells = [self.action_move.path.destination_coordinates()]
        self.action_move.path.length = 0

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.PROCESSED)
        self.assertEqual(self.action_move.percents, 1)

    def test_teleport_by_clan__from_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.assertFalse(self.action_move.teleport_with_clan())

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_by_clan__from_moving(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.assertFalse(self.action_move.teleport_with_clan())

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))

    def test_try_to_teleport_by_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=self.path,
                                                        destination=None,
                                                        break_at=None)

        self.assertEqual(self.hero.position.place_id, self.place_1.id)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))

    def test_teleport_by_clan__not_from_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=None,
                                                        break_at=None)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))

    def test_teleport_by_clan__wrong_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id+1)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=None,
                                                        break_at=None)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN
                             for message in self.hero.journal.messages))


class MoveSimpleBreakAtTests(clans_helpers.ClansTestsMixin,
                             utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action
        self.action_idl.state = self.action_idl.STATE.WAITING  # skip first steps

        self.hero.position.set_place(self.place_1)

        self.path = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                                to_x=self.place_2.x, to_y=self.place_2.y)

        self.break_at = 0.75
        self.real_destination = self.path.coordinates(self.break_at)

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=self.break_at)

    def test_create(self):
        self.assertEqual(self.action_move.path, self.path)
        self.assertEqual(self.action_move.destination, self.place_2)
        self.assertEqual(self.action_move.break_at, self.break_at)
        self.assertEqual(self.action_move.percents, 0)

    def check_finish_position(self):
        self.assertEqual(self.action_move.state, self.action_move.STATE.PROCESSED)
        self.assertAlmostEqual(self.action_move.percents, self.break_at)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertAlmostEqual(self.hero.position.x, self.real_destination[0])
        self.assertAlmostEqual(self.hero.position.y, self.real_destination[1])

    def test_full_move(self):
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        visited_cells = set()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)
            visited_cells.add((self.hero.position.cell_x, self.hero.position.cell_y))

        self.check_finish_position()

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_picked_up_in_road', lambda self: True)
    def test_picked_up__from_place(self):
        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.action_move.percents > 0)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_PICKED_UP_IN_ROAD)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_picked_up__from_moving(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.can_picked_up_in_road', lambda self: False):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertFalse(any(message.key.is_ACTION_MOVE_SIMPLE_TO_PICKED_UP_IN_ROAD
                             for message in self.hero.journal.messages))

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with mock.patch('the_tale.game.heroes.objects.Hero.can_picked_up_in_road', lambda self: True):
            with self.check_increased(lambda: self.action_move.percents):
                self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(any(message.key.is_ACTION_MOVE_SIMPLE_TO_PICKED_UP_IN_ROAD
                            for message in self.hero.journal.messages))

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_fly_probability', 1.0)
    def test_teleport_by_flying_companion__from_place(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.percents, 0)
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.action_move.percents > 0)
        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_FLY)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_fly_probability', 1.0)
    def test_teleport_by_flying_companion__from_moving(self):
        self.storage.process_turn(continue_steps_if_needed=False)

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)

        with self.check_increased(lambda: self.action_move.percents):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.action_move.percents > 0)
        self.assertTrue(self.hero.journal.messages[-1].key.is_COMPANIONS_FLY)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.check_finish_position()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion__from_place(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.action_move.place_hero_in_current_place(create_action=False)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertFalse(any(message.key.is_COMPANIONS_TELEPORT
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_teleport_probability', 1.0)
    def test_teleport_by_teleportator_companion__from_start(self):

        self.hero.actions.pop_action()

        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.action_move = prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                       path=self.path,
                                                                       destination=self.place_2,
                                                                       break_at=self.break_at)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertFalse(any(message.key.is_COMPANIONS_TELEPORT
                             for message in self.hero.journal.messages
                             if message.key is not None))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport(self):

        with self.check_increased(lambda: self.action_move.percents):
            result = self.action_move.teleport(0.1,
                                               create_inplace_action=True,
                                               check_moving_state=False)

        self.assertTrue(result)

        self.action_move.teleport(100500,
                                  create_inplace_action=True,
                                  check_moving_state=False)

        self.check_finish_position()

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_place(self):
        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_1.id)

        result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                    check_moving_state=False)

        self.assertTrue(result)

        self.check_finish_position()

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_place__from_moving(self):
        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.action_move.state, self.action_move.STATE.MOVING)
        self.assertEqual(self.hero.position.place_id, None)

        result = self.action_move.teleport_to_place(create_inplace_action=True,
                                                    check_moving_state=False)

        self.assertTrue(result)

        self.check_finish_position()

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport_to_end(self):
        result = self.action_move.teleport_to_end(check_moving_state=False)

        self.assertTrue(result)

        self.check_finish_position()

    def test_teleport_by_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.action_move.path.append(path_2)

        self.assertTrue(self.action_move.teleport_with_clan())

        self.assertEqual(self.action_move.state, self.action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    def test_teleport_by_clan__no_next_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        path_2 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_1.x+1, to_y=self.place_1.y+1)

        self.action_move.path = path_2

        self.assertFalse(self.action_move.teleport_with_clan())

        self.assertEqual(self.hero.position.place_id, self.place_1.id)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_try_to_teleport_by_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        self.path.append(path_2)

        with self.check_delta(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=self.path,
                                                        destination=self.place_3,
                                                        break_at=self.break_at)
            self.storage.process_turn(continue_steps_if_needed=False)


        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    def test_teleport_by_clan__not_from_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=self.place_2,
                                                        break_at=self.break_at)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)

    def test_teleport_by_clan__wrong_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)

        self.hero.clan_id = clan.id

        self.place_1.attrs.fast_transportation.add(clan.id+1)

        self.hero.actions.pop_action()

        self.hero.position.set_position(x=0.5, y=0.5)

        path_2 = navigation_path.simple_path(from_x=0, from_y=0,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        with self.check_not_changed(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id)):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_2,
                                                        destination=self.place_2,
                                                        break_at=self.break_at)

        self.assertEqual(self.hero.position.x, 0.5)
        self.assertEqual(self.hero.position.y, 0.5)
        self.assertEqual(self.hero.position.place_id, None)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN)


class ComplexClanTeleportationTests(clans_helpers.ClansTestsMixin,
                                    utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action
        self.action_idl.state = self.action_idl.STATE.WAITING  # skip first steps

        self.hero.position.set_place(self.place_1)
        self.hero.journal.messages = collections.deque(maxlen=None)

    def prepair_clan(self):
        self.prepair_forum_for_clans()
        clan = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan.id

        return clan

    def test_full_paths_with_teleports(self):
        clan = self.prepair_clan()

        path_1 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        path_1.append(path_2)

        for place in places_storage.places.all():
            place.attrs.fast_transportation.add(clan.id)

        with self.check_delta(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_1.id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                        path=path_1,
                                                        destination=self.place_3,
                                                        break_at=None)

            self.assertEqual(self.hero.actions.current_action.state,
                             prototypes.ActionMoveSimplePrototype.STATE.IN_CITY)
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_IN_PLACE)
        self.assertEqual(self.hero.position.place_id, self.place_2.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

        while not self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action.state,
                         prototypes.ActionMoveSimplePrototype.STATE.IN_CITY)

        with self.check_delta(lambda: get_fast_transportation_points(clan_id=clan.id, place_id=self.place_2.id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 2)

    def test_teleport_from_middle(self):

        clan = self.prepair_clan()

        path_1 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        path_1.append(path_2)

        self.place_2.attrs.fast_transportation.add(clan.id)

        prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                    path=path_1,
                                                    destination=self.place_3,
                                                    break_at=None)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    def test_teleport_from_start(self):

        clan = self.prepair_clan()

        path_1 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        path_1.append(path_2)

        self.place_1.attrs.fast_transportation.add(clan.id)

        prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                    path=path_1,
                                                    destination=self.place_3,
                                                    break_at=None)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 1)

    def test_teleport_from_end(self):
        clan = self.prepair_clan()

        path_1 = navigation_path.simple_path(from_x=self.place_1.x, from_y=self.place_1.y,
                                             to_x=self.place_2.x, to_y=self.place_2.y)

        path_2 = navigation_path.simple_path(from_x=self.place_2.x, from_y=self.place_2.y,
                                             to_x=self.place_3.x, to_y=self.place_3.y)

        path_1.append(path_2)

        self.place_3.attrs.fast_transportation.add(clan.id)

        prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                    path=path_1,
                                                    destination=self.place_3,
                                                    break_at=None)

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.position.place_id, self.place_3.id)
        self.assertEqual(sum(1 for message in self.hero.journal.messages
                             if message.key.is_ACTION_MOVE_SIMPLE_TO_TELEPORT_WITH_CLAN), 0)
