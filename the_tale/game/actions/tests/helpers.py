# coding: utf-8

import mock

from the_tale.game.actions import contexts
from the_tale.game.actions.prototypes import ActionBase
from the_tale.game.actions import relations


class TestAction(ActionBase):
    TYPE = relations.ACTION_TYPE.TEST
    CONTEXT_MANAGER = contexts.BattleContext
    SINGLE = False
    TEXTGEN_TYPE = 'action_idleness'

    @classmethod
    def _create(cls, hero=None, bundle_id=None, data=0, single=False):
        obj = cls( hero=hero,
                   bundle_id=bundle_id,
                   data=data,
                   state=cls.STATE.UNINITIALIZED)
        obj.SINGLE = single
        return obj


class ActionEventsTestsMixin(object):

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set())
    def test_habit_events__no_events(self):

        with self.check_not_changed(self.hero.diary.messages_number):
            self.action_event.do_events()


    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.NOTHING)
    def test_habit_events__nothing(self):

        with self.check_delta(self.hero.diary.messages_number, 1):
            self.action_event.do_events()


    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.MONEY)
    def test_habit_events__money(self):

        old_money = self.hero.money

        with self.check_delta(self.hero.diary.messages_number, 1):
            self.action_event.do_events()

        self.assertTrue(old_money < self.hero.money)


    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.ARTIFACT)
    def test_habit_events__artifact(self):

        self.assertEqual(self.hero.bag.occupation, 0)

        with self.check_delta(self.hero.diary.messages_number, 1):
            self.action_event.do_events()

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertFalse(self.hero.bag.values()[0].type.is_USELESS)



    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.EXPERIENCE)
    def test_habit_events__experience(self):

        old_experience = self.hero.experience
        old_level = self.hero.level

        with self.check_delta(self.hero.diary.messages_number, 1):
            self.action_event.do_events()

        self.assertTrue(old_experience < self.hero.experience or old_level < self.hero.level)


    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    def test_habit_events__all_hero_events(self):

        with self.check_changed(self.hero.diary.messages_number):
            self.action_event.do_events()
