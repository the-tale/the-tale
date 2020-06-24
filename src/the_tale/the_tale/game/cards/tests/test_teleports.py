
import smart_imports

smart_imports.all()


class ShortTeleportTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.SHORT_TELEPORT

    def setUp(self):
        super(ShortTeleportTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero.position.set_place(self.place_1)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_moving(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_use(self):
        path_1 = navigation_path.simple_path(self.hero.position.x,
                                             self.hero.position.y,
                                             self.place_2.x,
                                             self.place_2.y)
        path_2 = navigation_path.simple_path(self.place_2.x,
                                             self.place_2.y,
                                             self.place_3.x,
                                             self.place_3.y)
        path_1.append(path_2)

        action_move = actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                          destination=self.place_3,
                                                                          path=path_1,
                                                                          break_at=None)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.state == actions_prototypes.ActionMoveSimplePrototype.STATE.MOVING)

        self.assertTrue(self.hero.actions.current_action.percents < 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(action_move.state, action_move.STATE.IN_CITY)
        self.assertEqual(self.hero.actions.current_action.TYPE, actions_prototypes.ActionInPlacePrototype.TYPE)

        self.assertEqual(self.hero.position.place.id, self.place_2.id)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        while not action_move.leader:
            self.storage.process_turn(continue_steps_if_needed=False)

        self.storage.process_turn(continue_steps_if_needed=False)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions),
                         (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                          game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                          ()))

        self.assertTrue(self.hero.position.place.id, self.place_3.id)
        self.assertEqual(action_move.state, action_move.STATE.IN_CITY)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_use__wrong_state(self):
        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            destination=self.place_3,
                                                            path=navigation_path.simple_path(self.hero.position.x,
                                                                                             self.hero.position.y,
                                                                                             self.place_3.x,
                                                                                             self.place_3.y),
                                                            break_at=None)

        self.hero.actions.current_action.state = actions_prototypes.ActionMoveSimplePrototype.STATE.IN_CITY

        with self.check_not_changed(lambda: self.hero.actions.current_action.percents):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertTrue(self.hero.position.place.id, self.place_1.id)


class LongTeleportTests(helpers.CardsTestMixin, utils_testcase.TestCase):
    CARD = types.CARD.LONG_TELEPORT

    def setUp(self):
        super(LongTeleportTests, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1.id)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero.position.set_place(self.place_1)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_moving(self):
        self.assertFalse(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_use(self):
        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            destination=self.place_3,
                                                            path=navigation_path.simple_path(self.hero.position.x,
                                                                                             self.hero.position.y,
                                                                                             self.place_3.x,
                                                                                             self.place_3.y),
                                                            break_at=None)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertTrue(self.hero.actions.current_action.state == actions_prototypes.ActionMoveSimplePrototype.STATE.MOVING)

        self.assertTrue(self.hero.actions.current_action.percents < 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.position.place.id, self.place_3.id)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_use__wrong_state(self):
        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            destination=self.place_3,
                                                            path=navigation_path.simple_path(self.hero.position.x,
                                                                                             self.hero.position.y,
                                                                                             self.place_3.x,
                                                                                             self.place_3.y),
                                                            break_at=None)

        self.hero.actions.current_action.state = actions_prototypes.ActionMoveSimplePrototype.STATE.IN_CITY

        with self.check_not_changed(lambda: self.hero.actions.current_action.percents):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(storage=self.storage, hero=self.hero))
            self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertTrue(self.hero.position.place.id, self.place_1.id)
