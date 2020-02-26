
import smart_imports

smart_imports.all()


class IdlenessActionTest(clans_helpers.ClansTestsMixin,
                         utils_testcase.TestCase):

    def setUp(self):
        super(IdlenessActionTest, self).setUp()

        self.places = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)

        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

    def test_create(self):
        self.assertEqual(self.action_idl.leader, True)
        self.assertEqual(self.action_idl.percents, 1.0)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.BEFORE_FIRST_STEPS)
        self.storage._test_save()

    def test_first_steps(self):
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionFirstStepsPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.FIRST_STEPS)
        self.assertEqual(self.action_idl.bundle_id, self.hero.account_id)
        self.storage._test_save()

    def test_first_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.FIRST_STEPS

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)
        self.assertEqual(self.action_idl.bundle_id, self.hero.account_id)
        self.storage._test_save()

    def test_reset_percents_on_quest_end(self):
        self.action_idl.percents = 1.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(self.action_idl.percents, 0.0)

    def test_inplace(self):
        self.action_idl.percents = 1.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionInPlacePrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.IN_PLACE)
        self.storage._test_save()

    def test_waiting(self):
        self.action_idl.percents = 0.0
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.IN_PLACE
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.WAITING)
        self.storage._test_save()

    def test_regenerate_energy_action_create(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, heroes_relations.ENERGY_REGENERATION.PRAY)
        self.hero.last_energy_regeneration_at_turn -= max(next(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))))

        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0.0

        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionRegenerateEnergyPrototype.TYPE)
        self.storage._test_save()

    def test_regenerate_energy_action_not_create_for_sacrifice(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE, heroes_relations.ENERGY_REGENERATION.SACRIFICE)
        self.hero.last_energy_regeneration_at_turn -= max(next(zip(*heroes_relations.ENERGY_REGENERATION.select('period'))))
        self.storage.process_turn()
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.storage._test_save()

    def test_full_waiting(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        for i in range(c.TURNS_TO_IDLE * self.hero.level):
            self.storage.process_turn()
            game_turn.increment()
            self.assertEqual(len(self.hero.actions.actions_list), 1)
            self.assertEqual(self.hero.actions.current_action, self.action_idl)

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        self.action_idl.force_quest_action(quest_kwargs={})

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    def test_initiate_quest_just_after_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.action_idl.percents = 0

        self.action_idl.force_quest_action(quest_kwargs={})

        self.storage.process_turn()

        self.assertEqual(len(self.hero.actions.actions_list), 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionQuestPrototype.TYPE)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_wild_terrain__after_quest(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.QUEST
        self.hero.position.set_position(0, 0)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveSimplePrototype.TYPE)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_return_from_wild_terrain__after_resurrect(self):
        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.RESURRECT
        self.hero.position.set_position(0, 0)
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionMoveSimplePrototype.TYPE)

    def test_resurrect(self):
        self.hero.is_alive = False
        self.storage.process_turn()
        self.assertEqual(self.hero.actions.number, 2)
        self.assertEqual(self.hero.actions.current_action.TYPE, prototypes.ActionResurrectPrototype.TYPE)

    def get_task_board_points(self, clan_id, place_id):
        resource_id = emissaries_logic.resource_id(clan_id=clan_id,
                                                   place_id=place_id)

        return emissaries_tt_services.events_currencies.cmd_balance(resource_id,
                                                                    currency=emissaries_relations.EVENT_CURRENCY.TASK_BOARD)

    def test_task_board__not_hero_clan(self):

        self.prepair_forum_for_clans()

        clan_1 = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan_1.id

        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(account_2, uid=2)

        self.hero.position.place.attrs.task_board.add(clan_2.id)

        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        with self.check_not_changed(lambda: self.get_task_board_points(clan_1.id, self.hero.position.place_id)):
            with self.check_not_changed(lambda: self.action_idl.state):
                self.storage.process_turn()

        self.assertTrue(0 < self.action_idl.percents < 1)

    @mock.patch('tt_logic.emissaries.constants.TASK_BOARD_PLACES_NUMBER', 1)
    def test_task_board__hero_clan(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan.id
        self.hero.position.place.attrs.task_board.add(clan.id)

        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        with self.check_delta(lambda: self.get_task_board_points(clan.id, self.hero.position.place_id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            with self.check_changed(lambda: self.action_idl.state):
                self.storage.process_turn()

        self.assertEqual(self.action_idl.percents, 1)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_IDLENESS_TASK_BOARD)

    @mock.patch('tt_logic.emissaries.constants.TASK_BOARD_PLACES_NUMBER', 2)
    def test_task_board_in_near_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan.id
        self.hero.position.set_place(self.places[0])

        self.assertTrue(navigation_logic.manhattan_distance(self.places[0].x,
                                                            self.places[0].y,
                                                            self.places[2].x,
                                                            self.places[2].y) <= 2)

        self.places[2].attrs.task_board.add(clan.id)

        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        with self.check_delta(lambda: self.get_task_board_points(clan.id, self.places[2].id),
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            with self.check_not_changed(lambda: self.get_task_board_points(clan.id, self.places[0].id)):
                with self.check_changed(lambda: self.action_idl.state):
                    self.storage.process_turn()

        self.assertEqual(self.action_idl.percents, 1)
        self.assertEqual(self.action_idl.state, prototypes.ActionIdlenessPrototype.STATE.QUEST)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_QUEST)

        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_IDLENESS_TASK_BOARD)

    @mock.patch('tt_logic.emissaries.constants.TASK_BOARD_PLACES_NUMBER', 1)
    def test_task_board_in_far_place(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(self.account, uid=1)
        self.hero.clan_id = clan.id
        self.hero.position.set_place(self.places[0])

        self.assertTrue(navigation_logic.manhattan_distance(self.places[0].x,
                                                            self.places[0].y,
                                                            self.places[2].x,
                                                            self.places[2].y) > 1)

        self.places[2].attrs.task_board.add(clan.id)

        self.action_idl.state = prototypes.ActionIdlenessPrototype.STATE.WAITING
        self.action_idl.percents = 0

        with self.check_not_changed(lambda: self.get_task_board_points(clan.id, self.places[2].id)):
            with self.check_not_changed(lambda: self.get_task_board_points(clan.id, self.places[0].id)):
                with self.check_not_changed(lambda: self.action_idl.state):
                    self.storage.process_turn()

        self.assertTrue(0 < self.action_idl.percents < 1)
