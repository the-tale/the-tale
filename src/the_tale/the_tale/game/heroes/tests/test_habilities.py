
import smart_imports

smart_imports.all()


E = 0.0001


class HabilitiesContainerTest(utils_testcase.TestCase):

    def setUp(self):
        super(HabilitiesContainerTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account.id)

        self.hero = self.storage.accounts_to_heroes[account.id]

        self.abilities = self.hero.abilities

    def test_simple_level_up(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(self.abilities.randomized_mob_level_up(1), 1)

        self.assertEqual(reset_accessors_cache.call_count, 0)
        self.assertEqual(self.abilities.get(heroes_abilities_battle.HIT.get_id()).level, 1)

    def test_simple_level_up_with_level_up(self):
        self.abilities.add(heroes_abilities_battle.REGENERATION.get_id())

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(self.abilities.randomized_mob_level_up(1), 0)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.abilities.get(heroes_abilities_battle.REGENERATION.get_id()).level, 2)

    def test_large_level_up(self):
        self.assertEqual(self.abilities.randomized_mob_level_up(heroes_abilities_battle.HIT.MAX_LEVEL + 1), 2)
        self.assertEqual(self.abilities.get(heroes_abilities_battle.HIT.get_id()).level, heroes_abilities_battle.HIT.MAX_LEVEL)

    def test_multiply_level_up(self):
        self.abilities.add(heroes_abilities_battle.REGENERATION.get_id())
        self.abilities.add(heroes_abilities_battle.STRONG_HIT.get_id())
        levels = max([heroes_abilities_battle.HIT.MAX_LEVEL, heroes_abilities_battle.REGENERATION.MAX_LEVEL, heroes_abilities_battle.STRONG_HIT.MAX_LEVEL])
        self.assertEqual(self.abilities.randomized_mob_level_up(levels), 0)
        self.assertTrue(self.abilities.get(heroes_abilities_battle.HIT.get_id()).level, 1)
        self.assertTrue(self.abilities.get(heroes_abilities_battle.REGENERATION.get_id()).level > 1)
        self.assertTrue(self.abilities.get(heroes_abilities_battle.STRONG_HIT.get_id()).level > 1)

    def test_multiply_simple_level_up(self):
        self.abilities.add(heroes_abilities_battle.REGENERATION.get_id())
        self.assertEqual(self.abilities.randomized_mob_level_up(1), 0)
        self.assertTrue(self.abilities.get(heroes_abilities_battle.HIT.get_id()).level in [1, 2])
        self.assertTrue(self.abilities.get(heroes_abilities_battle.REGENERATION.get_id()).level in [1, 2])
        self.assertEqual(self.abilities.get(heroes_abilities_battle.HIT.get_id()).level + self.abilities.get(heroes_abilities_battle.REGENERATION.get_id()).level, 3)

    def test_rechooce_choices(self):
        for i in range(1000):
            old_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())

            with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
                self.assertTrue(self.abilities.rechooce_choices())

            self.assertEqual(reset_accessors_cache.call_count, 1)

            new_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())
            self.assertNotEqual(old_choices, new_choices)

    def test_can_rechoose_abilities_choices__when_no_points(self):
        self.hero.randomized_level_up()

        self.assertFalse(self.abilities.can_choose_new_ability)
        self.assertFalse(self.abilities.can_rechoose_abilities_choices())

        with mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.can_choose_new_ability', True):
            self.assertTrue(self.abilities.can_rechoose_abilities_choices())

    def test_rechooce_choices__can_not_rechoose(self):
        while self.abilities._can_rechoose_abilities_choices():
            self.hero.randomized_level_up(increment_level=True)

        # here we should have only c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM unchosen abilities

        self.assertEqual(len(self.abilities._get_candidates()), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)

        for i in range(1000):
            old_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())
            self.assertFalse(self.abilities.rechooce_choices())
            new_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())
            self.assertEqual(old_choices, new_choices)

    def test_add(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.abilities.add(heroes_abilities_battle.REGENERATION.get_id())

        self.assertEqual(reset_accessors_cache.call_count, 1)

    def test_increment_level(self):
        self.abilities.add(heroes_abilities_battle.REGENERATION.get_id())

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.abilities.increment_level(heroes_abilities_battle.REGENERATION.get_id())

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.abilities.get(heroes_abilities_battle.REGENERATION.get_id()).level, 2)


class HabilitiesTest(utils_testcase.TestCase):

    def setUp(self):
        super(HabilitiesTest, self).setUp()
        self.messenger = heroes_fake.FakeMessenger()
        self.attacker = actions_fake.FakeActor(name='attacker')
        self.defender = actions_fake.FakeActor(name='defender')

        game_logic.create_test_map()

    def test_serrialization(self):
        for ability_class in list(heroes_abilities.ABILITIES.values()):
            ability = ability_class(level=random.randint(1, ability_class.MAX_LEVEL))
            self.assertEqual(ability, ability_class.deserialize(ability.serialize()))

    def test_on_miss_method_exists(self):
        for ability_class in list(heroes_abilities.ABILITIES.values()):
            if ability_class.LOGIC_TYPE is not None and ability_class.LOGIC_TYPE.is_WITH_CONTACT:
                self.assertTrue('on_miss' in ability_class.__dict__)

    def test_hit(self):
        heroes_abilities_battle.HIT().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_hit'])

    def test_charge_enemy_without_bag(self):
        heroes_abilities_battle.CHARGE().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_charge_hit_only'])

    def test_charge_enemy_with_empty_bag(self):
        self.defender.bag = bag.Bag()
        heroes_abilities_battle.CHARGE().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_charge_hit_only'])

    @mock.patch('the_tale.game.heroes.abilities.battle.CHARGE.STAFF_DESTROY_CHANCE', 1)
    def test_charge_enemy_with_not_empty_bag__equipment(self):
        self.defender.bag = bag.Bag()
        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.artifacts,
                                                                           1,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)

        self.defender.bag.put_artifact(artifact)
        charge = heroes_abilities_battle.CHARGE()
        charge.use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.messenger.messages, ['hero_ability_charge_hit_only'])
        self.assertFalse(self.defender.bag.is_empty)

    @mock.patch('the_tale.game.heroes.abilities.battle.CHARGE.STAFF_DESTROY_CHANCE', 1)
    def test_charge_enemy_with_not_empty_bag__loot(self):
        self.defender.bag = bag.Bag()
        artifact = artifacts_storage.artifacts.generate_artifact_from_list(artifacts_storage.artifacts.loot,
                                                                           1,
                                                                           rarity=artifacts_relations.RARITY.NORMAL)

        self.defender.bag.put_artifact(artifact)
        charge = heroes_abilities_battle.CHARGE()
        charge.use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.messenger.messages, ['hero_ability_charge_hit_and_destroy'])
        self.assertTrue(self.defender.bag.is_empty)

    def test_magic_mushroom(self):
        heroes_abilities_battle.MAGIC_MUSHROOM().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ability_magic_mushroom)
        self.assertFalse(self.defender.context.ability_magic_mushroom)
        self.assertEqual(self.messenger.messages, ['hero_ability_magicmushroom'])

    def test_sidestep(self):
        heroes_abilities_battle.SIDESTEP().use(self.messenger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.ability_sidestep)
        self.assertTrue(self.defender.context.ability_sidestep)
        self.assertEqual(self.messenger.messages, ['hero_ability_sidestep'])

    def test_run_up_push(self):
        heroes_abilities_battle.RUN_UP_PUSH().use(self.messenger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.stun_length)
        self.assertTrue(self.defender.context.stun_length)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_runuppush'])

    def test_regeneration(self):
        self.assertFalse(heroes_abilities_battle.REGENERATION().can_be_used(self.attacker))
        self.attacker.health = 1
        self.assertTrue(heroes_abilities_battle.REGENERATION().can_be_used(self.attacker))

        heroes_abilities_battle.REGENERATION().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messenger.messages, ['hero_ability_regeneration'])

    def test_critical_chance(self):
        self.assertFalse(self.attacker.context.crit_chance > 0)
        heroes_abilities_battle.CRITICAL_HIT().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.crit_chance > 0)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_berserk(self):
        old_damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 50))
        heroes_abilities_battle.BERSERK().update_context(self.attacker, self.defender)
        self.assertEqual(old_damage, self.attacker.context.modify_outcoming_damage(power.Damage(100, 50)))
        self.attacker.health = 1
        heroes_abilities_battle.BERSERK().update_context(self.attacker, self.defender)
        new_damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 50))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_ninja(self):
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja == 0)
        heroes_abilities_battle.NINJA().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja > 0)

    def test_fireball(self):
        heroes_abilities_battle.FIREBALL().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertFalse(self.attacker.context.damage_queue_fire)
        self.assertTrue(self.defender.context.damage_queue_fire)
        self.assertEqual(self.messenger.messages, ['hero_ability_fireball'])

    def test_poison_cloud(self):
        heroes_abilities_battle.POISON_CLOUD().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.attacker.context.damage_queue_poison)
        self.assertTrue(self.defender.context.damage_queue_poison)
        self.assertEqual(self.messenger.messages, ['hero_ability_poison_cloud'])

    def test_vimpire_strike(self):
        self.attacker.health = 1
        heroes_abilities_battle.VAMPIRE_STRIKE().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messenger.messages, ['hero_ability_vampire_strike'])

    def test_freezing(self):
        heroes_abilities_battle.FREEZING().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.attacker.context.initiative_queue)
        self.assertTrue(1 - E < self.attacker.context.initiative < 1 + E)
        self.assertTrue(self.defender.context.initiative_queue)

        self.defender.context.on_enemy_turn()
        self.assertTrue(self.defender.context.initiative < 1)

        self.assertEqual(self.messenger.messages, ['hero_ability_freezing'])

    def test_speedup(self):
        heroes_abilities_battle.SPEEDUP().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.defender.context.initiative_queue)
        self.assertTrue(1 - E < self.defender.context.initiative < 1 + E)

        self.assertTrue(self.attacker.context.initiative_queue)
        self.attacker.context.on_own_turn()
        self.assertTrue(self.attacker.context.initiative > 1)

        self.assertEqual(self.messenger.messages, ['hero_ability_speedup'])

    def test_last_chance(self):
        heroes_abilities_battle.LAST_CHANCE().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.last_chance_probability > 0)

    def test_insane_strike(self):
        self.assertEqual(self.attacker.health, self.defender.health)

        with self.check_decreased(lambda: self.attacker.health):
            with self.check_decreased(lambda: self.defender.health):
                heroes_abilities_battle.INSANE_STRIKE().use(self.messenger, self.attacker, self.defender)

        self.assertTrue(self.attacker.health > self.defender.health)

        self.assertEqual(self.messenger.messages, ['hero_ability_insane_strike'])

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_mage(self):
        heroes_abilities_modifiers.MAGE().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic > 100)

        damage = self.attacker.context.modify_incoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic < 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_warrior(self):
        heroes_abilities_modifiers.WARRIOR().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic < 100)

        damage = self.attacker.context.modify_incoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic > 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_gargoyle(self):
        heroes_abilities_modifiers.GARGOYLE().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic == 100 and damage.magic == 100)

        damage = self.attacker.context.modify_incoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic < 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_killer(self):
        heroes_abilities_modifiers.KILLER().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic > 100)

        damage = self.attacker.context.modify_incoming_damage(power.Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic > 100)


class ChooseAbilityTaskTest(utils_testcase.TestCase):

    def setUp(self):
        super(ChooseAbilityTaskTest, self).setUp()

        game_logic.create_test_map()

        account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(account.id)
        self.hero = self.storage.accounts_to_heroes[account.id]

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.abilities.get_for_choose()[0].get_id()

    def get_unchoosed_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        choices = hero.abilities.get_for_choose()

        all_ = hero.abilities._get_candidates()

        for ability in all_:
            if ability not in choices:
                return ability.get_id()

    def get_only_for_mobs_ability_id(self):
        for ability_key, ability in list(heroes_abilities.ABILITIES.items()):
            if (not ability().availability.value & heroes_abilities_relations.ABILITY_AVAILABILITY.FOR_PLAYERS.value):
                return ability_key

    def test_create(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.hero_id, self.hero.id)
        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.UNPROCESSED)

    def test_serialization(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.serialize(), postponed_tasks.ChooseHeroAbilityTask.deserialize(task.serialize()).serialize())

    def test_process_wrong_id(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, 'ssadasda')
        self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.WRONG_ID)

    def test_process_id_not_in_choices(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_unchoosed_ability_id())
        self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.NOT_IN_CHOICE_LIST)

    def test_process_not_for_heroes(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_only_for_mobs_ability_id())

        with mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.get_for_choose', lambda x: [heroes_abilities.ABILITIES[task.ability_id]]):
            self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.NOT_FOR_PLAYERS)

    def test_process_already_max_level(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, heroes_abilities_battle.HIT.get_id())

        self.hero.abilities.abilities[heroes_abilities_battle.HIT.get_id()].level = heroes_abilities_battle.HIT.MAX_LEVEL
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.get_for_choose', lambda x: [heroes_abilities.ABILITIES[task.ability_id]]):
            with mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.can_choose_new_ability', True):
                self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.ALREADY_MAX_LEVEL)

    def test_process_success(self):
        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.PROCESSED)

    def test_process_no_freee_ability_points(self):

        task = postponed_tasks.ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())

        with mock.patch('the_tale.game.heroes.abilities.AbilitiesPrototype.can_choose_new_ability', False):
            self.assertEqual(task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, postponed_tasks.CHOOSE_HERO_ABILITY_STATE.MAXIMUM_ABILITY_POINTS_NUMBER)


class HabilitiesViewsTest(utils_testcase.TestCase):

    def setUp(self):
        super(HabilitiesViewsTest, self).setUp()

        game_logic.create_test_map()

        self.account1 = self.accounts_factory.create_account()
        self.account2 = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account1.id)
        self.hero = self.storage.accounts_to_heroes[self.account1.id]

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.abilities.get_for_choose()[0].get_id()

    def tearDown(self):
        pass

    def test_choose_ability_dialog(self):
        self.request_login(self.account1.email)
        response = self.request_html(django_reverse('game:heroes:choose-ability-dialog', args=[self.hero.id]))
        self.assertEqual(response.status_code, 200)  # here is real page

    def test_choose_ability_dialog_anonymous(self):
        request_url = django_reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])
        self.check_redirect(request_url, accounts_logic.login_page_url(request_url))

    def test_choose_ability_dialog_wrong_user(self):
        self.request_login(self.account2.email)
        self.check_html_ok(self.request_html(django_reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])), texts=(('heroes.not_owner', 1),))

    def test_choose_ability_request_anonymous(self):
        response = self.client.post(django_reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content.decode('utf-8'))['status'], 'error')

    def test_choose_ability_request_hero_not_exist(self):
        self.request_login(self.account1.email)
        response = self.client.post(django_reverse('game:heroes:choose-ability', args=[666]) + '?ability_id=' + self.get_new_ability_id())
        self.check_ajax_error(response, 'heroes.hero.not_found')

    def test_choose_ability_request_wrong_user(self):
        self.request_login(self.account2.email)
        response = self.client.post(django_reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.check_ajax_error(response, 'heroes.not_owner')

    def test_choose_ability_request_wrong_ability(self):
        self.request_login(self.account1.email)
        response = self.client.post(django_reverse('game:heroes:choose-ability', args=[self.hero.id + 1]) + '?ability_id=xxxyyy')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content.decode('utf-8'))['status'], 'error')

    def test_choose_ability_request_ok(self):
        self.request_login(self.account1.email)
        response = self.client.post(django_reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
