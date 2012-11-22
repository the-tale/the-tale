# coding: utf-8
import mock

from dext.utils import s11n

from django.test import client
from django.core.urlresolvers import reverse

from common.utils.testcase import TestCase
from common.postponed_tasks import PostponedTask, PostponedTaskPrototype, FakePostpondTaskPrototype

from accounts.logic import register_user, login_url

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.actions.fake import FakeActor

from game.heroes.fake import FakeMessanger

from game.heroes.prototypes import HeroPrototype, ChooseHeroAbilityTask, CHOOSE_HERO_ABILITY_STATE
from game.heroes.habilities import prototypes as common_abilities
from game.heroes.habilities import ABILITIES
from game.heroes.habilities.prototypes import ABILITIES_LOGIC_TYPE




class HabilitiesTest(TestCase):

    def setUp(self):
        self.messanger = FakeMessanger()
        self.attacker = FakeActor(name='attacker')
        self.defender = FakeActor(name='defender')

    def tearDown(self):
        pass

    def test_on_miss_method_exists(self):
        for ability_class in ABILITIES.values():
            if ability_class.LOGIC_TYPE == ABILITIES_LOGIC_TYPE.WITH_CONTACT:
                self.assertTrue('on_miss' in ability_class.__dict__)

    def test_hit(self):
        common_abilities.HIT.use(self.messanger, self.attacker, self.defender)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_hit'])

    def test_magic_mushroom(self):
        common_abilities.MAGIC_MUSHROOM.use(self.messanger, self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ability_magic_mushroom)
        self.assertFalse(self.defender.context.ability_magic_mushroom)
        self.assertEqual(self.messanger.messages, ['hero_ability_magicmushroom'])

    def test_sidestep(self):
        common_abilities.SIDESTEP.use(self.messanger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.ability_sidestep)
        self.assertTrue(self.defender.context.ability_sidestep)
        self.assertEqual(self.messanger.messages, ['hero_ability_sidestep'])

    def test_run_up_push(self):
        common_abilities.RUN_UP_PUSH.use(self.messanger, self.attacker, self.defender)
        self.assertFalse(self.attacker.context.stun_length)
        self.assertTrue(self.defender.context.stun_length)
        self.assertTrue(self.defender.health < self.defender.max_health)
        self.assertEqual(self.messanger.messages, ['hero_ability_runuppush'])

    def test_regeneration(self):
        self.attacker.health = 1
        common_abilities.REGENERATION.use(self.messanger, self.attacker, self.defender)
        self.assertTrue(self.attacker.health > 1)
        self.assertEqual(self.messanger.messages, ['hero_ability_regeneration'])

    def test_critical_chance(self):
        self.assertFalse(self.attacker.context.crit_chance > 0)
        common_abilities.CRITICAL_HIT.update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.crit_chance > 0)

    @mock.patch('game.balance.constants.DAMAGE_DELTA', 0)
    def test_berserk(self):
        old_damage = self.attacker.context.modify_initial_damage(100)
        common_abilities.BERSERK.update_context(self.attacker, self.defender)
        self.assertEqual(old_damage, self.attacker.context.modify_initial_damage(100))
        self.attacker.health = 1
        common_abilities.BERSERK.update_context(self.attacker, self.defender)
        self.assertTrue(old_damage < self.attacker.context.modify_initial_damage(100))

    def test_ninja(self):
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja == 0)
        common_abilities.NINJA.update_context(self.attacker, self.defender)
        self.assertTrue(self.attacker.context.ninja == 0)
        self.assertTrue(self.defender.context.ninja > 0)


class ChooseAbilityTaskTest(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.get_abilities_for_choose()[0].get_id()

    def get_unchoosed_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        choices = hero.get_abilities_for_choose()
        all_ = hero.abilities.get_for_choose(hero, all_=True)
        for ability in all_:
            if ability not in choices:
                return ability.get_id()

    def get_only_for_mobs_ability_id(self):
        for ability_key, ability in ABILITIES.items():
            if not ability.AVAILABLE_TO_PLAYERS:
                return ability_key

    def test_create(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task.hero_id, self.hero.id)
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.UNPROCESSED)

    def test_serialization(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertEqual(task, ChooseHeroAbilityTask.deserialize(task.serialize()))

    def test_process_wrong_id(self):
        task = ChooseHeroAbilityTask(self.hero.id, 'ssadasda')
        self.assertFalse(task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.WRONG_ID)

    def test_process_id_not_in_choices(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_unchoosed_ability_id())
        self.assertFalse(task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.NOT_IN_CHOICE_LIST)

    def test_process_not_for_heroes(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_only_for_mobs_ability_id())

        with mock.patch('game.heroes.prototypes.HeroPrototype.get_abilities_for_choose', lambda x: [ABILITIES[task.ability_id]]):
            self.assertFalse(task.process(FakePostpondTaskPrototype(), self.storage))

        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.NOT_FOR_PLAYERS)

    def test_process_already_choosen(self):
        task = ChooseHeroAbilityTask(self.hero.id, common_abilities.HIT.get_id())

        with mock.patch('game.heroes.prototypes.HeroPrototype.get_abilities_for_choose', lambda x: [ABILITIES[task.ability_id]]):
            self.assertFalse(task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.ALREADY_CHOOSEN)

    def test_process_success(self):
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertTrue(task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.PROCESSED)

    def test_process_no_destiny_points(self):
        self.hero.destiny_points = 0
        task = ChooseHeroAbilityTask(self.hero.id, self.get_new_ability_id())
        self.assertFalse(task.process(FakePostpondTaskPrototype(), self.storage))
        self.assertEqual(task.state, CHOOSE_HERO_ABILITY_STATE.NO_DESTINY_POINTS)


class HabilitiesViewsTest(TestCase):

    def setUp(self):
        create_test_map()
        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.hero = HeroPrototype.get_by_account_id(account_id)
        self.storage = LogicStorage()
        self.storage.add_hero(self.hero)


        register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.client = client.Client()

    def get_new_ability_id(self, hero=None):
        if hero is None:
            hero = self.hero
        return hero.get_abilities_for_choose()[0].get_id()

    @property
    def task(self):
        if not hasattr(self, '_task'):
            self._task = ChooseAbilityTaskPrototype(ChooseAbilityTask.objects.all()[0])
        return self._task

    def tearDown(self):
        pass

    def test_choose_ability_dialog(self):
        self.request_login('test_user@test.com')
        response = self.client.get(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id]))
        self.assertEqual(response.status_code, 200) #here is real page

    def test_choose_ability_dialog_anonymous(self):
        request_url = reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])
        response = self.client.get(request_url)
        self.assertRedirects(response, login_url(request_url), status_code=302, target_status_code=200)

    def test_choose_ability_dialog_wrong_user(self):
        self.request_login('test_user_2@test.com')
        self.check_html_ok(self.client.get(reverse('game:heroes:choose-ability-dialog', args=[self.hero.id])), texts=(('heroes.not_owner', 1),))

    def test_choose_ability_request_anonymous(self):
        response = self.client.post(reverse('game:heroes:choose-ability', args=[self.hero.id]) + '?ability_id=' + self.get_new_ability_id())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(s11n.from_json(response.content)['status'], 'error')

    def test_choose_ability_request_hero_not_exist(self):
        self.request_login('test_user@test.com')
        response = self.client.post(reverse('game:heroes:choose-ability', args=[666]) + '?ability_id=' + self.get_new_ability_id())
        self.check_ajax_error(response, 'heroes.hero_not_exists')

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
        task = PostponedTaskPrototype(PostponedTask.objects.all()[0])
        self.check_ajax_processing(response, task.status_url)
