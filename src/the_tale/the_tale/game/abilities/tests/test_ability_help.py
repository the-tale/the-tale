
import smart_imports

smart_imports.all()


class HelpAbilityTest(pvp_helpers.PvPTestsMixin,
                      helpers.UseAbilityTaskMixin,
                      utils_testcase.TestCase):
    ABILITY = deck.help.Help

    def setUp(self):
        super().setUp()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]
        self.action_idl = self.hero.actions.current_action

        self.ability = self.ABILITY()

    def use_attributes(self, hero=None, storage=None):
        if hero is None:
            hero = self.hero

        if storage is None:
            storage = self.storage

        return super().use_attributes(hero=hero, storage=storage)

    def test_none(self):
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: None):
            with self.check_not_changed(lambda: self.hero.statistics.help_count):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_success(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.on_help') as on_help:
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(on_help.call_count, 1)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_be_helped', lambda hero: False)
    def test_help_restricted(self):
        with self.check_not_changed(lambda: self.hero.statistics.help_count):
            self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_help_when_battle(self):
        battle_info = self.create_pvp_battle(account_1=self.account)

        with self.check_not_changed(lambda: self.hero.statistics.help_count):
            self.assertEqual(self.ability.use(**self.use_attributes(hero=battle_info.hero_1,
                                                                    storage=battle_info.storage)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    def test_heal(self):
        self.hero.health = 1
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))
                self.assertTrue(self.hero.health > 1)

    def test_money(self):
        old_hero_money = self.hero.money
        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.MONEY):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))
                self.assertTrue(self.hero.money > old_hero_money)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport(self):
        move_place = self.p3
        if move_place.id == self.hero.position.place.id:
            move_place = self.p1

        action_move = actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                                          destination=move_place,
                                                                          path=navigation_path.simple_path(self.hero.position.x,
                                                                                                           self.hero.position.y,
                                                                                                           move_place.x,
                                                                                                           move_place.y),
                                                                          break_at=None)

        game_turn.increment()
        self.storage.process_turn()

        old_percents = action_move.percents

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.TELEPORT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()),
                                 (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                                  game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                                  ()))

        self.assertTrue(old_percents < action_move.percents)
        self.assertEqual(self.hero.actions.current_action.percents, action_move.percents)

    @mock.patch('the_tale.game.balance.constants.ANGEL_HELP_CRIT_TELEPORT_DISTANCE', 9999999999)
    @mock.patch('the_tale.game.balance.constants.ANGEL_HELP_TELEPORT_DISTANCE', 9999999999)
    @mock.patch('the_tale.game.heroes.objects.Hero.is_battle_start_needed', lambda self: False)
    def test_teleport__inplace_action_created(self):
        move_place = self.p3
        if move_place.id == self.hero.position.place.id:
            move_place = self.p1

        actions_prototypes.ActionMoveSimplePrototype.create(hero=self.hero,
                                                            destination=move_place,
                                                            path=navigation_path.simple_path(self.hero.position.x,
                                                                                             self.hero.position.y,
                                                                                             move_place.x,
                                                                                             move_place.y),
                                                            break_at=None)

        game_turn.increment()
        self.storage.process_turn()

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.TELEPORT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()),
                                 (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED,
                                  game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS,
                                  ()))

        self.assertEqual(self.hero.actions.current_action.TYPE, actions_prototypes.ActionInPlacePrototype.TYPE)

    def test_lighting(self):
        action_battle = actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        game_turn.increment()
        self.storage.process_turn()

        old_mob_health = action_battle.mob.health
        old_percents = action_battle.percents

        self.assertTrue(relations.HELP_CHOICES.LIGHTING in action_battle.help_choices)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.LIGHTING):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(old_mob_health > action_battle.mob.health)
        self.assertEqual(self.hero.actions.current_action.percents, action_battle.percents)
        self.assertTrue(old_percents < action_battle.percents)

    def test_lighting_when_mob_killed(self):
        action_battle = actions_prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        game_turn.increment()
        self.storage.process_turn()

        action_battle.mob.health = 0

        self.assertFalse(relations.HELP_CHOICES.LIGHTING in action_battle.help_choices)

    def test_resurrect(self):
        self.hero.kill()
        action_resurrect = actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.RESURRECT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                game_turn.increment()
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(self.hero.health, self.hero.max_health)
        self.assertEqual(self.hero.is_alive, True)
        self.assertEqual(action_resurrect.state, action_resurrect.STATE.PROCESSED)

    def test_process_turn_called_if_current_action_processed(self):

        self.hero.kill()
        actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.logic_storage.LogicStorage.process_turn__single_hero') as process_turn__single_hero:
            with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.RESURRECT):
                with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                    game_turn.increment()
                    self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(process_turn__single_hero.call_args_list, [mock.call(hero=self.hero,
                                                                              logger=None,
                                                                              continue_steps_if_needed=True)])

    def test_resurrect__two_times(self):
        self.hero.kill()
        actions_prototypes.ActionResurrectPrototype.create(hero=self.hero)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.RESURRECT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                game_turn.increment()
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.RESURRECT):
            with self.check_not_changed(lambda: self.hero.statistics.help_count):
                game_turn.increment()
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.IGNORE, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HABIT_MODE', actions_relations.ACTION_HABIT_MODE.AGGRESSIVE)
    def test_update_habits__aggressive_action(self):

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.HELP_AGGRESSIVE)])

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HABIT_MODE', actions_relations.ACTION_HABIT_MODE.PEACEFUL)
    def test_update_habits__unaggressive_action(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.HELP_UNAGGRESSIVE)])

    @mock.patch('the_tale.game.artifacts.effects.Health.REMOVE_ON_HELP', True)
    def test_return_child_gifts(self):
        not_child_gift, child_gift, removed_artifact = artifacts_storage.artifacts.all()[:3]

        child_gift.special_effect = artifacts_relations.ARTIFACT_EFFECT.CHILD_GIFT
        removed_artifact.rare_effect = artifacts_relations.ARTIFACT_EFFECT.HEALTH

        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(not_child_gift.create_artifact(level=1, power=0))

        self.hero.bag.put_artifact(child_gift.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(child_gift.create_artifact(level=1, power=0))

        self.hero.bag.put_artifact(removed_artifact.create_artifact(level=1, power=0))
        self.hero.bag.put_artifact(removed_artifact.create_artifact(level=1, power=0, rarity=artifacts_relations.RARITY.RARE))

        with self.check_delta(lambda: self.hero.statistics.gifts_returned, 2):
            with self.check_delta(lambda: self.hero.bag.occupation, -3):
                self.ability.use(**self.use_attributes())

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__no_companion(self):
        self.assertEqual(self.hero.companion, None)

        with self.check_not_changed(lambda: self.hero.statistics.help_count):
            self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, c.COMPANIONS_HEAL_AMOUNT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertTrue(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION_CRIT)

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__full_health(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.assertEqual(self.hero.companion.health, self.hero.companion.max_health)

        with self.check_not_changed(lambda: self.hero.companion.health):
            with self.check_not_changed(lambda: self.hero.statistics.help_count):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))

        self.assertFalse(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION)
        self.assertFalse(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION_CRIT)

    @mock.patch('the_tale.game.heroes.objects.Hero.might_crit_chance', 1)
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__crit(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.companion.health = 1

        with self.check_delta(lambda: self.hero.companion.health, c.COMPANIONS_HEAL_CRIT_AMOUNT):
            with self.check_delta(lambda: self.hero.statistics.help_count, 1):
                self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertFalse(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ANGEL_ABILITY_HEAL_COMPANION_CRIT)

    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__on_heal_called(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.companion.health = 1

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.on_heal_companion') as on_heal_companion:
            self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(on_heal_companion.call_count, 1)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HABIT_MODE', actions_relations.ACTION_HABIT_MODE.COMPANION)
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__on_heal_action_habits_changed(self):
        habit_effect = random.choice([ability for ability in companions_abilities_effects.ABILITIES.records if isinstance(ability.effect, companions_abilities_effects.ChangeHabits)])

        companion_record = next(companions_storage.companions.enabled_companions())
        companion_record.abilities = companions_abilities_container.Container(start=[habit_effect])
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.habit_honor.change(100)
        self.hero.habit_peacefulness.change(-100)

        self.hero.companion.health = 1

        with self.check_changed(lambda: self.hero.habit_honor.raw_value + self.hero.habit_peacefulness.raw_value):
            self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HABIT_MODE', actions_relations.ACTION_HABIT_MODE.COMPANION)
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.get_help_choice', lambda x: relations.HELP_CHOICES.HEAL_COMPANION)
    def test_heal_companion__on_heal_action_habits_not_changed(self):
        habit_effect = random.choice([ability for ability in companions_abilities_effects.ABILITIES.records if not isinstance(ability.effect, companions_abilities_effects.ChangeHabits)])

        companion_record = next(companions_storage.companions.enabled_companions())
        companion_record.abilities = companions_abilities_container.Container(start=[habit_effect])
        self.hero.set_companion(companions_logic.create_companion(companion_record))

        self.hero.habit_honor.change(100)
        self.hero.habit_peacefulness.change(-100)

        self.hero.companion.health = 1

        with self.check_not_changed(lambda: self.hero.habit_honor.raw_value + self.hero.habit_peacefulness.raw_value):
            self.assertEqual(self.ability.use(**self.use_attributes()), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))
