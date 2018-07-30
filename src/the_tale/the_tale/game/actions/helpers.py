
import smart_imports

smart_imports.all()


class TestAction(prototypes.ActionBase):
    TYPE = relations.ACTION_TYPE.TEST
    CONTEXT_MANAGER = contexts.BattleContext
    SINGLE = False
    TEXTGEN_TYPE = 'action_idleness'

    @classmethod
    def _create(cls, hero=None, bundle_id=None, data=0, single=False):
        obj = cls(hero=hero,
                  bundle_id=bundle_id,
                  data=data,
                  state=cls.STATE.UNINITIALIZED)
        obj.SINGLE = single
        return obj


class ActionEventsTestsMixin(object):

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set())
    def test_habit_events__no_events(self):

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 0):
            self.action_event.do_events()

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.NOTHING)
    def test_habit_events__nothing(self):

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 1):
            self.action_event.do_events()

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.MONEY)
    def test_habit_events__money(self):

        old_money = self.hero.money

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 1):
            self.action_event.do_events()

        self.assertTrue(old_money < self.hero.money)

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.ARTIFACT)
    def test_habit_events__artifact(self):

        self.assertEqual(self.hero.bag.occupation, 0)

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 1):
            self.action_event.do_events()

        self.assertEqual(self.hero.bag.occupation, 1)
        self.assertFalse(list(self.hero.bag.values())[0].type.is_USELESS)

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    @mock.patch('the_tale.game.actions.prototypes.ActionBase.choose_event_reward', lambda hero: relations.ACTION_EVENT_REWARD.EXPERIENCE)
    def test_habit_events__experience(self):

        old_experience = self.hero.experience
        old_level = self.hero.level

        with self.check_calls_count('the_tale.game.heroes.tt_services.diary.cmd_push_message', 1):
            self.action_event.do_events()

        self.assertTrue(old_experience < self.hero.experience or old_level < self.hero.level)

    @mock.patch('the_tale.game.balance.constants.HABIT_EVENTS_IN_TURN', 1.01)
    @mock.patch('the_tale.game.heroes.objects.Hero.habit_events', lambda hero: set(relations.ACTION_EVENT.records))
    def test_habit_events__all_hero_events(self):

        with self.check_calls_exists('the_tale.game.heroes.tt_services.diary.cmd_push_message'):
            self.action_event.do_events()
