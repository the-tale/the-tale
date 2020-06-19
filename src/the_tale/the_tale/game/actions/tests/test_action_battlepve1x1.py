
import smart_imports

smart_imports.all()


class BattlePvE1x1ActionTest(utils_testcase.TestCase):

    def setUp(self):
        super(BattlePvE1x1ActionTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account.id)
        self.hero = self.storage.accounts_to_heroes[account.id]

        self.hero.level = 6
        self.hero.health = self.hero.max_health

        # do half of tests with companion
        if random.random() < 0.5:
            companion_record = next(companions_storage.companions.enabled_companions())
            companion = companions_logic.create_companion(companion_record)
            self.hero.set_companion(companion)
            self.hero.companion.health = 1

        self.action_idl = self.hero.actions.current_action

        with mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 0):
            self.action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

    def tearDown(self):
        pass

    def test_create(self):
        self.assertEqual(self.action_idl.leader, False)
        self.assertEqual(self.action_battle.leader, True)
        self.assertEqual(self.action_battle.bundle_id, self.action_idl.bundle_id)
        self.assertEqual(self.action_battle.percents, 0.0)
        self.assertEqual(self.action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)
        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_mob_killed(self):
        self.assertEqual(self.hero.statistics.pve_kills, 0)
        self.action_battle.mob.health = 0
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertEqual(self.hero.statistics.pve_kills, 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 0)
    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_no_loot(self):

        self.action_battle.mob.health = 0

        with self.check_not_changed(lambda: self.hero.bag.occupation):
            with self.check_not_changed(lambda: self.hero.statistics.loot_had):
                with self.check_not_changed(lambda: self.hero.statistics.artifacts_had):
                    self.storage.process_turn()

        self.assertTrue(any(m.key.is_ACTION_BATTLEPVE1X1_NO_LOOT for m in self.hero.journal.messages))

        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_loot(self):

        self.action_battle.mob.health = 0

        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            with self.check_delta(lambda: self.hero.statistics.loot_had, 1):
                with self.check_not_changed(lambda: self.hero.statistics.artifacts_had):
                    self.storage.process_turn()

        self.assertTrue(any(m.key.is_ACTION_BATTLEPVE1X1_PUT_LOOT for m in self.hero.journal.messages))

        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_artifacts(self):
        self.action_battle.mob.health = 0

        with self.check_delta(lambda: self.hero.bag.occupation, 1):
            with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                with self.check_not_changed(lambda: self.hero.statistics.loot_had):
                    self.storage.process_turn()

        self.assertTrue(any(m.key.is_ACTION_BATTLEPVE1X1_PUT_LOOT for m in self.hero.journal.messages))

        self.storage._test_save()

    def fill_bag(self, power):
        for i in range(self.hero.max_bag_size):
            artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts, 1,
                                                                               rarity=artifacts_relations.RARITY.NORMAL)
            artifact.power = power
            self.hero.put_loot(artifact)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_replace_loot(self):

        self.action_battle.mob.health = 0

        self.fill_bag(power.Power(0, 0))

        with self.check_not_changed(lambda: self.hero.bag.occupation):
            with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                self.storage.process_turn()

        self.assertTrue(any(m.key.is_ACTION_BATTLEPVE1X1_REPLACE_LOOT_WHEN_NO_SPACE for m in self.hero.journal.messages))

        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.balance.constants.GET_LOOT_PROBABILITY', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_can_not_replace_loot(self):

        self.action_battle.mob.health = 0

        self.fill_bag(power.Power(666, 666))

        with self.check_not_changed(lambda: self.hero.bag.occupation):
            with self.check_not_changed(lambda: self.hero.statistics.artifacts_had):
                self.storage.process_turn()

        self.assertTrue(any(m.key.is_ACTION_BATTLEPVE1X1_PUT_LOOT_NO_SPACE for m in self.hero.journal.messages))

        self.storage._test_save()

    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_killed(self):
        self.assertEqual(self.hero.statistics.pve_deaths, 0)
        self.hero.health = 0
        self.storage.process_turn(continue_steps_if_needed=False)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        self.storage._test_save()

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 1)
    @mock.patch('the_tale.game.actions.prototypes.battle.make_turn', lambda a, b, c: None)
    def test_hero_and_mob_killed(self):
        self.hero.health = 0
        self.action_battle.mob.health = 0
        with self.check_not_changed(lambda: self.hero.statistics.artifacts_had):
            with self.check_not_changed(lambda: self.hero.bag.occupation):
                self.storage.process_turn(continue_steps_if_needed=False)
        self.assertTrue(self.hero.journal.messages[-1].key.is_ACTION_BATTLEPVE1X1_JOURNAL_HERO_AND_MOB_KILLED)
        self.assertEqual(len(self.hero.actions.actions_list), 1)
        self.assertEqual(self.hero.actions.current_action, self.action_idl)
        self.assertTrue(not self.hero.is_alive)
        self.assertEqual(self.hero.statistics.pve_deaths, 1)
        self.storage._test_save()

    def test_full_battle(self):

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            game_turn.increment()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    def test_full_battle__with_companion(self):
        battle_ability = random.choice([ability
                                        for ability in companions_abilities_effects.ABILITIES.records
                                        if isinstance(ability.effect, companions_abilities_effects.BaseBattleAbility)])

        companion_record = next(companions_storage.companions.enabled_companions())
        companion_record.abilities = companions_abilities_container.Container(start=(battle_ability,))

        companion = companions_logic.create_companion(companion_record)
        self.hero.set_companion(companion)

        self.hero.reset_accessors_cache()

        while len(self.hero.actions.actions_list) != 1:
            self.storage.process_turn()
            game_turn.increment()

        self.assertTrue(self.action_idl.leader)

        self.storage._test_save()

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage_probability', 0.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL', 0.0)
    @mock.patch('the_tale.game.balance.constants.COMPANIONS_EATEN_CORPSES_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.mobs.objects.Mob.mob_type', tt_beings_relations.TYPE.ANIMAL)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_eat_corpses', lambda hero: True)
    def test_full_battle__with_companion__eat_corpse(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.reset_accessors_cache()

        self.hero.companion.health = 10

        while self.hero.actions.current_action.TYPE == prototypes.ActionBattlePvE1x1Prototype.TYPE:
            self.storage.process_turn(continue_steps_if_needed=False)
            game_turn.increment()

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.companion.health, 10 + c.COMPANIONS_EATEN_CORPSES_HEAL_AMOUNT)

        self.storage._test_save()

    def test_bit_mob(self):
        old_mob_health = self.action_battle.mob.health
        old_action_percents = self.action_battle.percents

        self.action_battle.bit_mob(0.33)

        self.assertTrue(self.action_battle.mob.health < old_mob_health)
        self.assertTrue(self.action_battle.percents > old_action_percents)

    def test_bit_mob_and_kill(self):

        self.action_battle.bit_mob(1)

        self.assertEqual(self.action_battle.mob.health, self.action_battle.mob.max_health - 1)
        self.assertTrue(0 < self.action_battle.percents < 1)

        self.assertEqual(self.action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)

        self.action_battle.bit_mob(self.action_battle.mob.max_health)
        self.assertEqual(self.action_battle.mob.health, 0)
        self.assertEqual(self.action_battle.percents, 1)

        self.assertEqual(self.action_battle.state, self.action_battle.STATE.PROCESSED)

    @mock.patch('the_tale.game.balance.constants.KILL_BEFORE_BATTLE_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.heroes.habits.Honor.interval', game_relations.HABIT_HONOR_INTERVAL.LEFT_3)
    def test_kill_before_start(self):

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_do_exorcism', lambda hero: True)
    def test_companion_exorcims__demon(self):
        self.check_companion_exorcims(tt_beings_relations.TYPE.DEMON)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_do_exorcism', lambda hero: True)
    def test_companion_exorcims__supernatural(self):
        self.check_companion_exorcims(tt_beings_relations.TYPE.SUPERNATURAL)

    def check_companion_exorcims(self, mob_type):
        self.companion_record = companions_logic.create_random_companion_record('exorcist',
                                                                                state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        mob_record = mobs_logic.create_random_mob_record('demon', type=mob_type)
        mob = mobs_objects.Mob(record_id=mob_record.id, level=self.hero.level, is_boss=False)

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_companion_do_exorcism', lambda hero: True)
    def test_companion_exorcims__not_demon_or_supernatural(self):

        self.companion_record = companions_logic.create_random_companion_record('exorcist', state=companions_relations.STATE.ENABLED)
        self.hero.set_companion(companions_logic.create_companion(self.companion_record))

        not_demon_record = mobs_logic.create_random_mob_record('demon',
                                                               type=tt_beings_relations.TYPE.random(exclude=(tt_beings_relations.TYPE.DEMON,
                                                                                                             tt_beings_relations.TYPE.SUPERNATURAL, )))
        not_demon = mobs_objects.Mob(record_id=not_demon_record.id, level=self.hero.level, is_boss=False)

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=not_demon)

        self.assertEqual(action_battle.percents, 0.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.BATTLE_RUNNING)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, action_battle)

    @mock.patch('the_tale.game.balance.constants.PEACEFULL_BATTLE_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_3)
    def test_peacefull_battle(self):

        self.hero.actions.pop_action()

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mobs_storage.mobs.create_mob_for_hero(self.hero))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_leave_battle_in_fear', lambda self: True)
    def test_fear_battle(self):

        self.hero.actions.pop_action()

        mob = next((m for m in mobs_storage.mobs.all() if m.type.is_CIVILIZED))

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 0):
            action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob.create_mob(self.hero, is_boss=False))

        self.assertEqual(action_battle.percents, 1.0)
        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

        self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(self.hero.actions.current_action, self.action_idl)

    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_PROBABILITY', 1.01)
    @mock.patch('the_tale.game.balance.constants.EXP_FOR_KILL_DELTA', 0)
    @mock.patch('the_tale.game.heroes.habits.Peacefulness.interval', game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_3)
    def test_experience_for_kill(self):
        mob = mobs_storage.mobs.create_mob_for_hero(self.hero)
        mob.health = 0

        with self.check_delta(lambda: self.hero.statistics.pve_kills, 1):
            with mock.patch('the_tale.game.heroes.objects.Hero.add_experience') as add_experience:
                with mock.patch('the_tale.game.actions.prototypes.ActionBattlePvE1x1Prototype.process_artifact_breaking') as process_artifact_breaking:
                    action_battle = prototypes.ActionBattlePvE1x1Prototype.create(hero=self.hero, mob=mob)
                    self.storage.process_turn(continue_steps_if_needed=False)

        self.assertEqual(add_experience.call_args_list, [mock.call(c.EXP_FOR_KILL)])
        self.assertEqual(process_artifact_breaking.call_count, 1)

        self.assertEqual(action_battle.state, self.action_battle.STATE.PROCESSED)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.objects.Artifact.can_be_broken', lambda self: True)
    def test_process_artifact_breaking__no_equipment(self):
        self.hero.equipment._remove_all()
        old_power = self.hero.power.clone()
        self.action_battle.process_artifact_breaking()
        self.assertEqual(old_power, self.hero.power)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.objects.Artifact.can_be_broken', lambda self: True)
    def test_process_artifact_breaking__broken(self):
        for artifact in list(self.hero.equipment.values()):
            artifact.power = power.Power(100, 100)

        old_power = self.hero.power.total()
        self.action_battle.process_artifact_breaking()
        self.assertTrue(old_power > self.hero.power.total())

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.objects.Artifact.can_be_broken', lambda self: False)
    def test_process_artifact_breaking__not_broken(self):
        for artifact in list(self.hero.equipment.values()):
            artifact.power = power.Power(100, 100)

        old_power = self.hero.power.total()
        self.action_battle.process_artifact_breaking()
        self.assertEqual(old_power, self.hero.power.total())

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_BREAKS_PER_BATTLE', 1.0)
    @mock.patch('the_tale.game.artifacts.objects.Artifact.can_be_broken', lambda self: False)
    def test_process_artifact_breaking__break_only_mostly_damaged(self):
        for artifact in list(self.hero.equipment.values()):
            artifact.power = power.Power(100, 100)
            artifact.integrity = 0

        artifact.integrity = artifact.max_integrity

        for i in range(100):
            self.action_battle.process_artifact_breaking()

        self.assertEqual(artifact.power, power.Power(100, 100))

    def test_process_artifact_breaking__integrity_damage(self):
        for artifact in list(self.hero.equipment.values()):
            artifact.integrity = artifact.max_integrity

        self.action_battle.process_artifact_breaking()

        for artifact in list(self.hero.equipment.values()):
            self.assertTrue(artifact.integrity < artifact.max_integrity)
