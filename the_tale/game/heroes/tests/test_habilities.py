# coding: utf-8
import random
import datetime

import mock

from dext.common.utils import s11n

from django.test import client
from django.core.urlresolvers import reverse

from the_tale.common.utils.testcase import TestCase
from the_tale.common.postponed_tasks import PostponedTaskPrototype, FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.logic import register_user, login_page_url
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic_storage import LogicStorage
from the_tale.game.logic import create_test_map
from the_tale.game.balance import constants as c

from the_tale.game.actions.fake import FakeActor
from the_tale.game.actions.contexts.battle import Damage

from the_tale.game.heroes.fake import FakeMessenger

from the_tale.game.heroes.habilities import battle as battle_abilities
from the_tale.game.heroes.habilities import modifiers as modifiers_abilities
from the_tale.game.heroes.habilities import ABILITIES, ABILITY_AVAILABILITY
from the_tale.game.heroes.postponed_tasks import ChooseHeroAbilityTask, CHOOSE_HERO_ABILITY_STATE
from the_tale.game.heroes.conf import heroes_settings

from .. import logic


E = 0.0001

class HabilitiesContainerTest(TestCase):

    def setUp(self):
        super(HabilitiesContainerTest, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))

        self.hero = self.storage.accounts_to_heroes[account_id]

        self.abilities = self.hero.abilities

    def test_simple_level_up(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(self.abilities.randomized_mob_level_up(1), 1)

        self.assertEqual(reset_accessors_cache.call_count, 0)
        self.assertEqual(self.abilities.get(battle_abilities.HIT.get_id()).level, 1)

    def test_simple_level_up_with_level_up(self):
        self.abilities.add(battle_abilities.REGENERATION.get_id())

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(self.abilities.randomized_mob_level_up(1), 0)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.abilities.get(battle_abilities.REGENERATION.get_id()).level, 2)

    def test_large_level_up(self):
        self.assertEqual(self.abilities.randomized_mob_level_up(battle_abilities.HIT.MAX_LEVEL+1), 2)
        self.assertEqual(self.abilities.get(battle_abilities.HIT.get_id()).level, battle_abilities.HIT.MAX_LEVEL)

    def test_multiply_level_up(self):
        self.abilities.add(battle_abilities.REGENERATION.get_id())
        self.abilities.add(battle_abilities.STRONG_HIT.get_id())
        levels = max([battle_abilities.HIT.MAX_LEVEL, battle_abilities.REGENERATION.MAX_LEVEL, battle_abilities.STRONG_HIT.MAX_LEVEL])
        self.assertEqual(self.abilities.randomized_mob_level_up(levels), 0)
        self.assertTrue(self.abilities.get(battle_abilities.HIT.get_id()).level, 1)
        self.assertTrue(self.abilities.get(battle_abilities.REGENERATION.get_id()).level > 1)
        self.assertTrue(self.abilities.get(battle_abilities.STRONG_HIT.get_id()).level > 1)

    def test_multiply_simple_level_up(self):
        self.abilities.add(battle_abilities.REGENERATION.get_id())
        self.assertEqual(self.abilities.randomized_mob_level_up(1), 0)
        self.assertTrue(self.abilities.get(battle_abilities.HIT.get_id()).level in [1, 2])
        self.assertTrue(self.abilities.get(battle_abilities.REGENERATION.get_id()).level in [1, 2])
        self.assertEqual(self.abilities.get(battle_abilities.HIT.get_id()).level + self.abilities.get(battle_abilities.REGENERATION.get_id()).level, 3)

    def test_reset_abilities(self):
        self.assertFalse(self.abilities.can_reset) # new hero created with reset timeout
        self.abilities.set_reseted_at(datetime.datetime.now() - heroes_settings.ABILITIES_RESET_TIMEOUT)
        self.assertTrue(self.abilities.can_reset)

        self.abilities.add(battle_abilities.STRONG_HIT.get_id())
        self.assertTrue(len(self.abilities.all) > 1)

        old_destiny_points = self.abilities.destiny_points_spend

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.abilities.reset()

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(len(self.abilities.all), 2)
        self.assertEqual(old_destiny_points + 1, self.abilities.destiny_points_spend)
        self.assertFalse(self.abilities.can_reset)

    def test_rechooce_choices(self):
        for i in xrange(1000):
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

        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.can_choose_new_ability', True):
            self.assertTrue(self.abilities.can_rechoose_abilities_choices())


    def test_rechooce_choices__can_not_rechoose(self):
        while self.abilities._can_rechoose_abilities_choices():
            self.hero.randomized_level_up(increment_level=True)

        # here we should have only c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM unchosen abilities

        self.assertEqual(len(self.abilities._get_candidates()), c.ABILITIES_OLD_ABILITIES_FOR_CHOOSE_MAXIMUM)

        for i in xrange(1000):
            old_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())
            self.assertFalse(self.abilities.rechooce_choices())
            new_choices = set(ability.get_id() for ability in self.abilities.get_for_choose())
            self.assertEqual(old_choices, new_choices)

    def test_add(self):
        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.abilities.add(battle_abilities.REGENERATION.get_id())

        self.assertEqual(reset_accessors_cache.call_count, 1)


    def test_increment_level(self):
        self.abilities.add(battle_abilities.REGENERATION.get_id())

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.abilities.increment_level(battle_abilities.REGENERATION.get_id())

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.abilities.get(battle_abilities.REGENERATION.get_id()).level, 2)




class HabilitiesTest(TestCase):

    def setUp(self):
        super(HabilitiesTest, self).setUp()
        self.messenger = FakeMessenger()
        self.attacker = FakeActor(name='attacker')
        self.defender = FakeActor(name='defender')

    def tearDown(self):
        pass

    def test_serrialization(self):
        for ability_class in ABILITIES.values():
            ability = ability_class(level=random.randint(1, ability_class.MAX_LEVEL))
            self.assertEqual(ability, ability_class.deserialize(ability.serialize()))

    def test_on_miss_method_exists(self):
        for ability_class in ABILITIES.values():
            if ability_class.LOGIC_TYPE is not None and ability_class.LOGIC_TYPE.is_WITH_CONTACT:
                self.assertTrue('on_miss' in ability_class.__dict__)

    def test_hit(self):
        battle_abilities.HIT().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_hit'])

    def test_magic_mushroom(self):
        battle_abilities.MAGIC_MUSHROOM().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ability_magic_mushroom)
        self.assertFalse(self.defender.context.ability_magic_mushroom)
        self.assertEqual(self.messenger.messages, ['hero_ability_magicmushroom'])

    def test_sidestep(self):
        battle_abilities.SIDESTEP().use(self.messenger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.ability_sidestep)
        self.assertTrue(self.defender.context.ability_sidestep)
        self.assertEqual(self.messenger.messages, ['hero_ability_sidestep'])

    def test_run_up_push(self):
        battle_abilities.RUN_UP_PUSH().use(self.messenger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.stun_length)
        self.assertTrue(self.defender.context.stun_length)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messenger.messages, ['hero_ability_runuppush'])

    def test_regeneration(self):
        self.assertFalse(battle_abilities.REGENERATION().can_be_used(self.attacker))
        self.attacker.health = 1
        self.assertTrue(battle_abilities.REGENERATION().can_be_used(self.attacker))

        battle_abilities.REGENERATION().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messenger.messages, ['hero_ability_regeneration'])

    def test_critical_chance(self):
        self.assertFalse(self.attacker.context.crit_chance > 0)
        battle_abilities.CRITICAL_HIT().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.crit_chance > 0)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_berserk(self):
        old_damage = self.attacker.context.modify_outcoming_damage(Damage(100, 50))
        battle_abilities.BERSERK().update_context(self.attacker, self.defender)
        self.assertEqual(old_damage, self.attacker.context.modify_outcoming_damage(Damage(100, 50)))
        self.attacker.health = 1
        battle_abilities.BERSERK().update_context(self.attacker, self.defender)
        new_damage = self.attacker.context.modify_outcoming_damage(Damage(100, 50))
        self.assertTrue(old_damage.physic < new_damage.physic)
        self.assertTrue(old_damage.magic < new_damage.magic)

    def test_ninja(self):
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja == 0)
        battle_abilities.NINJA().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja > 0)

    def test_fireball(self):
        battle_abilities.FIREBALL().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertFalse(self.attacker.context.damage_queue_fire)
        self.assertTrue(self.defender.context.damage_queue_fire)
        self.assertEqual(self.messenger.messages, ['hero_ability_fireball'])

    def test_poison_cloud(self):
        battle_abilities.POISON_CLOUD().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.attacker.context.damage_queue_poison)
        self.assertTrue(self.defender.context.damage_queue_poison)
        self.assertEqual(self.messenger.messages, ['hero_ability_poison_cloud'])

    def test_vimpire_strike(self):
        self.attacker.health = 1
        battle_abilities.VAMPIRE_STRIKE().use(self.messenger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messenger.messages, ['hero_ability_vampire_strike'])

    def test_freezing(self):
        battle_abilities.FREEZING().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.attacker.context.initiative_queue)
        self.assertTrue(1 - E < self.attacker.context.initiative < 1 + E)
        self.assertTrue(self.defender.context.initiative_queue)

        self.defender.context.on_enemy_turn()
        self.assertTrue(self.defender.context.initiative < 1)

        self.assertEqual(self.messenger.messages, ['hero_ability_freezing'])

    def test_speedup(self):
        battle_abilities.SPEEDUP().use(self.messenger, self.attacker, self.defender)
        self.assertEqual(self.defender.health, self.defender.max_health)
        self.assertFalse(self.defender.context.initiative_queue)
        self.assertTrue(1 - E < self.defender.context.initiative < 1 + E)

        self.assertTrue(self.attacker.context.initiative_queue)
        self.attacker.context.on_own_turn()
        self.assertTrue(self.attacker.context.initiative > 1)

        self.assertEqual(self.messenger.messages, ['hero_ability_speedup'])

    def test_last_chance(self):
        battle_abilities.LAST_CHANCE().update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.last_chance_probability > 0)

    def test_insane_strike(self):
        self.assertEqual(self.attacker.health, self.defender.health)

        with self.check_decreased(lambda: self.attacker.health):
            with self.check_decreased(lambda: self.defender.health):
                battle_abilities.INSANE_STRIKE().use(self.messenger, self.attacker, self.defender)

        self.assertTrue(self.attacker.health > self.defender.health)

        self.assertEqual(self.messenger.messages, ['hero_ability_insane_strike'])

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_mage(self):
        modifiers_abilities.MAGE().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic > 100)

        damage = self.attacker.context.modify_incoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic < 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_warrior(self):
        modifiers_abilities.WARRIOR().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic < 100)

        damage = self.attacker.context.modify_incoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic > 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_gargoyle(self):
        modifiers_abilities.GARGOYLE().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic == 100 and damage.magic == 100)

        damage = self.attacker.context.modify_incoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic < 100 and damage.magic < 100)

    @mock.patch('the_tale.game.balance.constants.DAMAGE_DELTA', 0)
    def test_killer(self):
        modifiers_abilities.KILLER().update_context(self.attacker, self.defender)
        damage = self.attacker.context.modify_outcoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic > 100)

        damage = self.attacker.context.modify_incoming_damage(Damage(100, 100))
        self.assertTrue(damage.physic > 100 and damage.magic > 100)



class ChooseAbilityTaskTest(TestCase):

    def setUp(self):
        super(ChooseAbilityTaskTest, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]


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
        for ability_key, ability in ABILITIES.items():
            if (not ability().availability.value & ABILITY_AVAILABILITY.FOR_PLAYERS.value):
                return ability_key

    def test_create(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.hero_id, self.hero.id)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.UNPROCESSED)

    def test_serialization(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.serialize(), ChooseHeroAbilityTask.deserialize(task.serialize()).serialize())

    def test_process_wrong_id(self):
        task = ChooseHeroAbilityTask(self.hero.id, 'ssadasda')
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.WRONG_ID)

    def test_process_id_not_in_choices(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_unchoosed_ability_id())
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.NOT_IN_CHOICE_LIST)

    def test_process_not_for_heroes(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_only_for_mobs_ability_id())

        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.get_for_choose', lambda x: [ABILITIES[task.ability_id]]):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.NOT_FOR_PLAYERS)

    def test_process_already_max_level(self):
        task = ChooseHeroAbilityTask(self.hero.id, battle_abilities.HIT.get_id())

        self.hero.abilities.abilities[battle_abilities.HIT.get_id()].level = battle_abilities.HIT.MAX_LEVEL
        self.hero.abilities.updated = True
        logic.save_hero(self.hero)

        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.get_for_choose', lambda x: [ABILITIES[task.ability_id]]):
            with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.can_choose_new_ability', True):
                self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.ALREADY_MAX_LEVEL)

    def test_process_success(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.PROCESSED)

    def test_process_no_freee_ability_points(self):

        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())

        with mock.patch('the_tale.game.heroes.habilities.AbilitiesPrototype.can_choose_new_ability', False):
            self.assertEqual(task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)

        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.MAXIMUM_ABILITY_POINTS_NUMBER)


class HabilitiesViewsTest(TestCase):

    def setUp(self):
        super(HabilitiesViewsTest, self).setUp()
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')

        self.storage = LogicStorage()
        self.storage.load_account_data(AccountPrototype.get_by_id(account_id))
        self.hero = self.storage.accounts_to_heroes[account_id]

        register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.client = client.Client()

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.abilities.get_for_choose()[0].get_id()

    def tearDown(self):
        pass

    def test_choose_ability_dialog(self):
        self.request_login('test_user@test.com')
        response = self.request_html(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id]))
        self.assertEqual(response.status_code, 200) #here is real page

    def test_choose_ability_dialog_anonymous(self):
        request_url = reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])
        self.check_redirect(request_url, login_page_url(request_url))

    def test_choose_ability_dialog_wrong_user(self):
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.request_html(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])), texts=(('heroes.not_owner', 1),))

    def test_choose_ability_request_anonymous(self):
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_request_hero_not_exist(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-ability', args=[666]) + '?ability_id=' + self.get_new_ability_id())
        self.check_ajax_error(response, 'heroes.hero.not_found')

    def test_choose_ability_request_wrong_user(self):
        self.request_login('test_user_2@test.com')
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.check_ajax_error(response, 'heroes.not_owner')

    def test_choose_ability_request_wrong_ability(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id+1]) + '?ability_id=xxxyyy')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_request_ok(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
