# coding: utf-8

import random

import mock

from the_tale.common.utils import testcase

from the_tale.common.postponed_tasks.prototypes import PostponedTaskPrototype

from the_tale.game.logic import create_test_map

from the_tale.game.jobs import job
from the_tale.game.jobs import effects

from the_tale.game.heroes import logic as heroes_logic


class FakeJob(job.Job):
    ACTOR = random.choice(('person', 'place'))


class BaseEffectsTests(testcase.TestCase):

    def setUp(self):
        super(BaseEffectsTests, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.hero_1 = heroes_logic.load_hero(account_id=self.account_1.id)

        self.account_2 = self.accounts_factory.create_account()
        self.hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.account_3 = self.accounts_factory.create_account()
        self.hero_3 = heroes_logic.load_hero(account_id=self.account_3.id)

        self.effect = effects.EFFECT.PLACE_SAFETY


    def test_apply_to_heroes(self):
        with mock.patch('the_tale.game.jobs.effects.BaseEffect.invoke_hero_method') as invoke_hero_method:
            self.effect.logic.apply_to_heroes(actor_type='person',
                                              effect=self.effect,
                                              method_names=('pos', 'neg'),
                                              method_kwargs={'a': 'b'},
                                              positive_heroes=set([self.hero_1.id, self.hero_3.id]),
                                              negative_heroes=set([self.hero_2.id]),
                                              direction='positive')

            self.effect.logic.apply_to_heroes(actor_type='place',
                                              effect=self.effect,
                                              method_names=('pos2', 'neg2'),
                                              method_kwargs={'x': 'y'},
                                              positive_heroes=set([self.hero_3.id]),
                                              negative_heroes=set([self.hero_1.id, self.hero_2.id]),
                                              direction='negative')

        self.assertEqual(invoke_hero_method.call_args_list,
                         [mock.call(method_name='pos', account_id=self.account_1.id,
                                    method_kwargs={'a': 'b', 'message_type': 'job_diary_person_place_safety_positive_friends'}, hero_id=self.hero_1.id),
                          mock.call(method_name='pos', account_id=self.account_3.id,
                                    method_kwargs={'a': 'b', 'message_type': 'job_diary_person_place_safety_positive_friends'}, hero_id=self.hero_3.id),
                          mock.call(method_name='neg', account_id=self.account_2.id,
                                    method_kwargs={'a': 'b', 'message_type': 'job_diary_person_place_safety_positive_enemies'}, hero_id=self.hero_2.id),
                          mock.call(method_name='pos2', account_id=self.account_3.id,
                                    method_kwargs={'x': 'y', 'message_type': 'job_diary_place_place_safety_negative_friends'}, hero_id=self.hero_3.id),
                          mock.call(method_name='neg2', account_id=self.account_1.id,
                                    method_kwargs={'x': 'y', 'message_type': 'job_diary_place_place_safety_negative_enemies'}, hero_id=self.hero_1.id),
                          mock.call(method_name='neg2', account_id=self.account_2.id,
                                    method_kwargs={'x': 'y', 'message_type': 'job_diary_place_place_safety_negative_enemies'}, hero_id=self.hero_2.id)])


    def test_invoke_hero_method(self):

        with self.check_delta(PostponedTaskPrototype._db_count, 1):
            operation = self.effect.logic.invoke_hero_method(self.account_1.id, self.hero_1.id, 'method_x', {'x': 'y'})

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_logic_task') as cmd_logic_task:
            operation()

        task = PostponedTaskPrototype._db_latest()

        self.assertEqual(cmd_logic_task.call_args_list,
                         [mock.call(account_id=self.account_1.id, task_id=task.id)])

        self.assertEqual(task.internal_logic.hero_id, self.hero_1.id)
        self.assertEqual(task.internal_logic.method_name, 'method_x')
        self.assertEqual(task.internal_logic.method_kwargs, {'x': 'y'})


    def test_message_type(self):
        self.assertEqual(self.effect.logic.message_type(actor='x', effect=self.effect, direction='a', group='z'),
                         'job_diary_x_place_safety_a_z')



class EffectsTestsBase(testcase.TestCase):

    def setUp(self):
        super(EffectsTestsBase, self).setUp()

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.hero_1 = heroes_logic.load_hero(account_id=self.account_1.id)

        self.account_2 = self.accounts_factory.create_account()
        self.hero_2 = heroes_logic.load_hero(account_id=self.account_2.id)

        self.account_3 = self.accounts_factory.create_account()
        self.hero_3 = heroes_logic.load_hero(account_id=self.account_3.id)

        self.place = self.place_1
        self.person = self.place.persons[0]

        self.actor_name = 'actor name'
        self.job_power = 666


class PlaceEffectTests(EffectsTestsBase):

    def check_apply_positive(self, effect):
        with mock.patch('the_tale.game.jobs.effects.BaseEffect.invoke_hero_method') as invoke_hero_method:
            effect.logic.apply_positive(actor_type='x',
                                        actor_name=self.actor_name,
                                        place=self.place,
                                        person=None,
                                        positive_heroes=set([self.hero_1.id, self.hero_3.id]),
                                        negative_heroes=set([self.hero_2.id]),
                                        job_power=self.job_power)

        self.assertEqual(invoke_hero_method.call_args_list,
                         [mock.call(method_name='job_message', account_id=self.account_1.id, hero_id=self.hero_1.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name='job_message', account_id=self.account_3.id, hero_id=self.hero_3.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name='job_message', account_id=self.account_2.id, hero_id=self.hero_2.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power})])

        applied_effect = self.place.effects.effects[0]

        self.assertEqual(applied_effect.name, self.actor_name)
        self.assertEqual(applied_effect.attribute, effect.logic.attribute)
        self.assertEqual(applied_effect.value, effect.logic.base_value*self.job_power)


    def check_apply_negative(self, effect):
        with mock.patch('the_tale.game.jobs.effects.BaseEffect.invoke_hero_method') as invoke_hero_method:
            effect.logic.apply_negative(actor_type='y',
                                        actor_name=self.actor_name,
                                        place=self.place,
                                        person=self.person,
                                        positive_heroes=set([self.hero_1.id]),
                                        negative_heroes=set([self.hero_3.id, self.hero_2.id]),
                                        job_power=self.job_power)

        self.assertEqual(invoke_hero_method.call_args_list,
                         [mock.call(method_name='job_message', account_id=self.account_1.id, hero_id=self.hero_1.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name='job_message', account_id=self.account_2.id, hero_id=self.hero_2.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name='job_message', account_id=self.account_3.id, hero_id=self.hero_3.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power})])

        applied_effect = self.place.effects.effects[0]

        self.assertEqual(applied_effect.name, self.actor_name)
        self.assertEqual(applied_effect.attribute, effect.logic.attribute)

        self.assertEqual(applied_effect.value, -effect.logic.base_value*self.job_power)


    def test_production__positive(self):
        self.check_apply_positive(effects.EFFECT.PLACE_PRODUCTION)

    def test_production__negative(self):
        self.check_apply_negative(effects.EFFECT.PLACE_PRODUCTION)

    def test_safety__positive(self):
        self.check_apply_positive(effects.EFFECT.PLACE_SAFETY)

    def test_safety__negative(self):
        self.check_apply_negative(effects.EFFECT.PLACE_SAFETY)


    def test_transport__positive(self):
        self.check_apply_positive(effects.EFFECT.PLACE_TRANSPORT)

    def test_transport__negative(self):
        self.check_apply_negative(effects.EFFECT.PLACE_TRANSPORT)


    def test_freedom__positive(self):
        self.check_apply_positive(effects.EFFECT.PLACE_FREEDOM)

    def test_freedom__negative(self):
        self.check_apply_negative(effects.EFFECT.PLACE_FREEDOM)


    def test_stability__positive(self):
        self.check_apply_positive(effects.EFFECT.PLACE_STABILITY)

    def test_stability__negative(self):
        self.check_apply_negative(effects.EFFECT.PLACE_STABILITY)



class HeroEffectTests(EffectsTestsBase):

    def check_apply_positive(self, effect):
        with mock.patch('the_tale.game.jobs.effects.BaseEffect.invoke_hero_method') as invoke_hero_method:
            effect.logic.apply_positive(actor_type='x',
                                        actor_name=self.actor_name,
                                        place=self.place,
                                        person=None,
                                        positive_heroes=set([self.hero_1.id, self.hero_3.id]),
                                        negative_heroes=set([self.hero_2.id]),
                                        job_power=self.job_power)

        self.assertEqual(invoke_hero_method.call_args_list,
                         [mock.call(method_name=effect.logic.method_name, account_id=self.account_1.id, hero_id=self.hero_1.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name=effect.logic.method_name, account_id=self.account_3.id, hero_id=self.hero_3.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name='job_message', account_id=self.account_2.id, hero_id=self.hero_2.id,
                                    method_kwargs={'person_id': None,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_x_%s_positive_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power})])

    def check_apply_negative(self, effect):
        with mock.patch('the_tale.game.jobs.effects.BaseEffect.invoke_hero_method') as invoke_hero_method:
            effect.logic.apply_negative(actor_type='y',
                                        actor_name=self.actor_name,
                                        place=self.place,
                                        person=self.person,
                                        positive_heroes=set([self.hero_1.id]),
                                        negative_heroes=set([self.hero_3.id, self.hero_2.id]),
                                        job_power=self.job_power)

        self.assertEqual(invoke_hero_method.call_args_list,
                         [mock.call(method_name='job_message', account_id=self.account_1.id, hero_id=self.hero_1.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_friends' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name=effect.logic.method_name, account_id=self.account_2.id, hero_id=self.hero_2.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power}),
                          mock.call(method_name=effect.logic.method_name, account_id=self.account_3.id, hero_id=self.hero_3.id,
                                    method_kwargs={'person_id': self.person.id,
                                                   'place_id': self.place.id,
                                                   'message_type': 'job_diary_y_%s_negative_enemies' % effect.name.lower(),
                                                   'job_power': self.job_power})])


    def test_money__positive(self):
        self.check_apply_positive(effects.EFFECT.HERO_MONEY)

    def test_money__negative(self):
        self.check_apply_negative(effects.EFFECT.HERO_MONEY)


    def test_artifact__positive(self):
        self.check_apply_positive(effects.EFFECT.HERO_ARTIFACT)

    def test_artifact__negative(self):
        self.check_apply_negative(effects.EFFECT.HERO_ARTIFACT)


    def test_experience__positive(self):
        self.check_apply_positive(effects.EFFECT.HERO_EXPERIENCE)

    def test_experience__negative(self):
        self.check_apply_negative(effects.EFFECT.HERO_EXPERIENCE)


    def test_energy__positive(self):
        self.check_apply_positive(effects.EFFECT.HERO_ENERGY)

    def test_energy__negative(self):
        self.check_apply_negative(effects.EFFECT.HERO_ENERGY)
