
import smart_imports

smart_imports.all()


class ArenaPvP1x1Test(pvp_helpers.PvPTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super(ArenaPvP1x1Test, self).setUp()

        game_logic.create_test_map()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

        self.battle_info = self.create_pvp_battle()

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.hero_1.id,))

        self.assertEqual(len(battles), 1)
        self.assertEqual(set(battles[0].participants_ids), {self.battle_info.hero_1.id, self.battle_info.hero_2.id})

    def test_serialization(self):
        self.assertEqual(self.battle_info.meta_action.serialize(),
                         meta_actions.ArenaPvP1x1.deserialize(self.battle_info.meta_action.serialize()).serialize())

    def test_initialization(self):
        self.assertTrue(self.battle_info.meta_action.storage)

        heroes_ids = (self.battle_info.hero_1.id, self.battle_info.hero_2.id)

        self.assertTrue(self.battle_info.meta_action.hero_1.id in heroes_ids)
        self.assertTrue(self.battle_info.meta_action.hero_2.id in heroes_ids)

        self.assertEqual(self.battle_info.meta_action.uid,
                         '%s#%d#%d' % (self.battle_info.meta_action.TYPE.value,
                                       min(self.battle_info.hero_1.id, self.battle_info.hero_2.id),
                                       max(self.battle_info.hero_1.id, self.battle_info.hero_2.id)))

        self.assertEqual(self.battle_info.meta_action.hero_1.health, self.battle_info.hero_1.max_health)

        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.advantage, 0)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.energy, 0)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.energy_speed, 1)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.turn_advantage, 0)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.turn_effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.turn_energy, 0)
        self.assertEqual(self.battle_info.meta_action.hero_1_pvp.turn_energy_speed, 1)
        self.assertTrue(self.battle_info.meta_action.hero_1_context.pvp_advantage_strike_damage.total > 0)

        self.assertEqual(self.battle_info.meta_action.hero_2.health, self.battle_info.hero_2.max_health)

        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.advantage, 0)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.energy, 0)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.energy_speed, 1)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.turn_advantage, 0)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.turn_effectiveness, c.PVP_EFFECTIVENESS_INITIAL)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.turn_energy, 0)
        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.turn_energy_speed, 1)
        self.assertTrue(self.battle_info.meta_action.hero_2_context.pvp_advantage_strike_damage.total > 0)

    def test_is_valid(self):
        self.assertTrue(self.battle_info.meta_action.is_valid())

        heroes_ids = (self.battle_info.hero_1.id, self.battle_info.hero_2.id)
        self.battle_info.meta_action.storage.release_account_data(random.choice(heroes_ids))

        self.assertFalse(self.battle_info.meta_action.is_valid())

    def test_no_help_choices(self):
        self.assertEqual(self.battle_info.hero_1.actions.current_action.HELP_CHOICES, ())
        self.assertEqual(self.battle_info.hero_2.actions.current_action.HELP_CHOICES, ())

    def test_restore_health_restore(self):
        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account()

        hero_1 = heroes_logic.load_hero(account_id=account_1.id)
        hero_1.health = hero_1.max_health / 2

        heroes_logic.save_hero(hero_1)

        supervisor_task = game_prototypes.SupervisorTaskPrototype.create_arena_pvp_1x1(account_1, account_2)

        supervisor_task.capture_member(account_1.id)
        supervisor_task.capture_member(account_2.id)

        supervisor_task.process(bundle_id=100500)

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]

        self.assertEqual(hero_1.health, hero_1.max_health)

        hero_1.actions.current_action.meta_action.process_battle_ending()

        self.assertEqual(hero_1.health, hero_1.max_health / 2)

    def test_one_hero_killed(self):
        self.battle_info.meta_action.hero_1.health = 0
        self.battle_info.meta_action.process()
        self.assertEqual(self.battle_info.meta_action.state, meta_actions.ArenaPvP1x1.STATE.BATTLE_ENDING)
        game_turn.increment()
        self.battle_info.meta_action.process()

        self.assertEqual(self.battle_info.meta_action.state, meta_actions.ArenaPvP1x1.STATE.PROCESSED)
        self.assertTrue(self.battle_info.meta_action.hero_1.is_alive and self.battle_info.meta_action.hero_2.is_alive)
        self.assertEqual(self.battle_info.meta_action.hero_1.health, self.battle_info.meta_action.hero_1.max_health)
        self.assertEqual(self.battle_info.meta_action.hero_2.health, self.battle_info.meta_action.hero_2.max_health)

    def check_hero_pvp_statistics(self, hero, battles, victories, draws, defeats):
        self.assertEqual(hero.statistics.pvp_battles_1x1_number, battles)
        self.assertEqual(hero.statistics.pvp_battles_1x1_victories, victories)
        self.assertEqual(hero.statistics.pvp_battles_1x1_draws, draws)
        self.assertEqual(hero.statistics.pvp_battles_1x1_defeats, defeats)

    def _end_battle(self, hero_1_health, hero_2_health):
        self.battle_info.meta_action.hero_1.health = hero_1_health
        self.battle_info.meta_action.hero_2.health = hero_2_health

        self.battle_info.meta_action.process()
        game_turn.increment()
        self.battle_info.meta_action.process()

    def test_hero_1_win(self):
        self._end_battle(hero_1_health=self.battle_info.meta_action.hero_1.max_health, hero_2_health=0)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.meta_action.hero_1.id,))
        self.assertFalse(battles)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 1, 1, 0, 0)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 1, 0, 0, 1)

    def test_hero_2_win(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.battle_info.meta_action.hero_2.max_health)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.meta_action.hero_1.id,))
        self.assertFalse(battles)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 1, 0, 0, 1)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 1, 1, 0, 0)

    def test_draw(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.meta_action.hero_1.id,))
        self.assertFalse(battles)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 1, 0, 1, 0)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 1, 0, 1, 0)

    @mock.patch('the_tale.game.pvp.logic.calculate_rating_required', lambda *argv, **kwargs: False)
    def test_hero_1_win_no_stats(self):
        self._end_battle(hero_1_health=self.battle_info.meta_action.hero_1.max_health, hero_2_health=0)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 0, 0, 0, 0)

    @mock.patch('the_tale.game.pvp.logic.calculate_rating_required', lambda *argv, **kwargs: False)
    def test_hero_2_win_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=self.battle_info.meta_action.hero_1.max_health)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 0, 0, 0, 0)

    @mock.patch('the_tale.game.pvp.logic.calculate_rating_required', lambda *argv, **kwargs: False)
    def test_draw_no_stats(self):
        self._end_battle(hero_1_health=0, hero_2_health=0)

        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_1, 0, 0, 0, 0)
        self.check_hero_pvp_statistics(self.battle_info.meta_action.hero_2, 0, 0, 0, 0)

    def test_second_process_call_in_one_turn(self):

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1._process') as meta_action_process_counter:
            self.battle_info.meta_action.process()
            self.battle_info.meta_action.process()

        self.assertEqual(meta_action_process_counter.call_count, 1)

    def test_update_hero_pvp_info(self):
        self.battle_info.meta_action.hero_2_pvp.set_effectiveness(50)

        self.battle_info.meta_action.update_hero_pvp_info(self.battle_info.meta_action.hero_2_pvp)
        self.assertTrue(self.battle_info.meta_action.hero_2_pvp.energy > self.battle_info.meta_action.hero_1_pvp.energy)

        self.assertTrue(0 < self.battle_info.meta_action.hero_2_pvp.effectiveness < 50)

    def test_advantage_after_turn(self):
        self.battle_info.meta_action.hero_1_pvp.set_effectiveness(50)
        self.battle_info.meta_action.hero_2_pvp.set_effectiveness(25)

        self.battle_info.meta_action.process()

        self.assertTrue(self.battle_info.meta_action.hero_1_pvp.advantage > 0)
        self.assertTrue(self.battle_info.meta_action.hero_2_pvp.advantage < 0)

    def test_full_battle(self):
        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.meta_action.hero_1.id,))

        self.assertEqual(len(battles), 1)
        self.assertEqual(set(battles[0].participants_ids), {self.battle_info.meta_action.hero_1.id, self.battle_info.meta_action.hero_2.id})

        while self.battle_info.meta_action.state != meta_actions.ArenaPvP1x1.STATE.PROCESSED:
            self.battle_info.meta_action.process()
            game_turn.increment()

        self.assertEqual(self.battle_info.meta_action.state, meta_actions.ArenaPvP1x1.STATE.PROCESSED)
        self.assertTrue(self.battle_info.meta_action.hero_1.is_alive and self.battle_info.meta_action.hero_2.is_alive)
        self.assertEqual(self.battle_info.meta_action.hero_1.health, self.battle_info.meta_action.hero_1.max_health)
        self.assertEqual(self.battle_info.meta_action.hero_2.health, self.battle_info.meta_action.hero_2.max_health)

        battles = pvp_tt_services.matchmaker.cmd_get_battles_by_participants(participants_ids=(self.battle_info.meta_action.hero_1.id,))

        self.assertEqual(len(battles), 0)

        self.assertEqual(pvp_models.Battle1x1Result.objects.all().count(), 1)

        battle_result = pvp_models.Battle1x1Result.objects.all()[0]

        self.assertNotEqual(battle_result.participant_1_id, battle_result.participant_2_id)

    def test_get_bot_pvp_properties(self):
        properties = self.battle_info.meta_action.bot_pvp_properties

        self.assertEqual(set(properties.keys()), set(('ability_chance', 'priorities')))
        self.assertTrue(0 < properties['ability_chance'] <= 1)
        self.assertEqual(set(properties['priorities']), set(pvp_abilities.ABILITIES.keys()))

        for ability_priority in properties['priorities'].values():
            self.assertTrue(ability_priority > 0)

    def test_process_bot_called__hero_1(self):
        self.battle_info.meta_action.hero_1.is_bot = True

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1.process_bot') as process_bot:
            self.battle_info.meta_action.process()

        self.assertEqual(process_bot.call_count, 1)
        self.assertEqual(process_bot.call_args[1]['bot'].id, self.battle_info.meta_action.hero_1.id)
        self.assertEqual(process_bot.call_args[1]['enemy'].id, self.battle_info.meta_action.hero_2.id)

    def test_process_bot_called__hero_2(self):
        self.battle_info.meta_action.hero_2.is_bot = True

        with mock.patch('the_tale.game.actions.meta_actions.ArenaPvP1x1.process_bot') as process_bot:
            self.battle_info.meta_action.process()

        self.assertEqual(process_bot.call_count, 1)
        self.assertEqual(process_bot.call_args[1]['bot'].id, self.battle_info.meta_action.hero_2.id)
        self.assertEqual(process_bot.call_args[1]['enemy'].id, self.battle_info.meta_action.hero_1.id)

    def test_process_bot_called__use_ability(self):
        self.battle_info.meta_action.hero_1.is_bot = True
        self.battle_info.meta_action.hero_1_pvp.set_energy(10)

        properties = self.battle_info.meta_action.bot_pvp_properties
        properties['ability_chance'] = 1.0

        self.battle_info.meta_action.hero_2_pvp.set_energy_speed(2)  # flame abilitie will not be used, if enemy energy speed is 1

        self.battle_info.meta_action.process()

        self.assertTrue(self.battle_info.meta_action.hero_1_pvp.energy in (1, 2))

    def test_initialize_bots__bot_is_second(self):
        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account(is_bot=True)

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_1.level = 50
        self.assertEqual(hero_2.level, 1)

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_2.level, 50)
        self.assertTrue(len(hero_2.abilities.all) > 1)
        self.assertEqual(hero_2.health, hero_2.max_health)

    def test_initialize_bots__bot_is_first(self):
        account_1 = self.accounts_factory.create_account(is_bot=True)
        account_2 = self.accounts_factory.create_account()

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_2.level = 50
        self.assertEqual(hero_1.level, 1)

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_1.level, 50)
        self.assertTrue(len(hero_1.abilities.all) > 1)
        self.assertEqual(hero_1.health, hero_1.max_health)

    def test_initialize_bots__second_create(self):
        account_1 = self.accounts_factory.create_account()
        account_2 = self.accounts_factory.create_account(is_bot=True)

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        hero_1.level = 50
        self.assertEqual(hero_2.level, 1)

        meta_action = meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)
        meta_action.process_battle_ending()

        meta_actions.ArenaPvP1x1.create(storage, hero_1, hero_2)

        self.assertEqual(hero_2.level, 50)
        self.assertTrue(len(hero_2.abilities.all) > 1)
        self.assertEqual(hero_2.health, hero_2.max_health)

    def test_process_bot__flame_ability_not_used(self):
        account_1 = self.accounts_factory.create_account(is_bot=True)
        account_2 = self.accounts_factory.create_account()

        storage = game_logic_storage.LogicStorage()
        storage.load_account_data(account_1)
        storage.load_account_data(account_2)

        hero_1 = storage.accounts_to_heroes[account_1.id]
        hero_2 = storage.accounts_to_heroes[account_2.id]

        self.battle_info.meta_action.bot_pvp_properties = {'priorities': {pvp_abilities.Flame.TYPE: 1}, 'ability_chance': 1}

        self.assertEqual(self.battle_info.meta_action.hero_2_pvp.energy_speed, 1)

        with mock.patch('the_tale.game.pvp.abilities.Flame.use') as use:
            for i in range(100):
                self.battle_info.meta_action.process_bot(hero_1, hero_2, self.battle_info.meta_action.hero_2_pvp)

        self.assertEqual(use.call_count, 0)
