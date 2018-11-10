
import smart_imports

smart_imports.all()


class GiveStabilityMixin(helpers.CardsTestMixin):
    CARD = None

    def setUp(self):
        super(GiveStabilityMixin, self).setUp()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.highlevel = amqp_environment.environment.workers.highlevel
        self.highlevel.process_initialize(0, 'highlevel')

    def test_use(self):

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, value=self.place_1.id))

        self.assertEqual((result, step), (game_postponed_tasks.ComplexChangeTask.RESULT.CONTINUE, game_postponed_tasks.ComplexChangeTask.STEP.HIGHLEVEL))
        self.assertEqual(len(postsave_actions), 1)

        with mock.patch('the_tale.game.workers.highlevel.Worker.cmd_logic_task') as highlevel_logic_task_counter:
            postsave_actions[0]()

        self.assertEqual(highlevel_logic_task_counter.call_count, 1)

        self.assertEqual(len(self.place_1.effects), 0)

        with self.check_delta(lambda: len(self.place_1.effects), 1):
            result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero,
                                                                                        step=step,
                                                                                        highlevel=self.highlevel,
                                                                                        value=self.place_1.id))

        self.assertEqual(self.place_1.effects.effects[0].name, 'Хранитель {}'.format(self.account_1.nick))
        self.assertTrue(self.place_1.effects.effects[0].attribute.is_STABILITY)
        self.assertTrue(self.place_1.effects.effects[0].value, self.CARD.effect.modificator)

        self.assertEqual((result, step, postsave_actions), (game_postponed_tasks.ComplexChangeTask.RESULT.SUCCESSED, game_postponed_tasks.ComplexChangeTask.STEP.SUCCESS, ()))

    def test_use_for_wrong_place_id(self):
        with self.check_not_changed(lambda: len(self.place_1.effects)):
            self.assertEqual(self.CARD.effect.use(**self.use_attributes(hero=self.hero, value=666, storage=self.storage)),
                             (game_postponed_tasks.ComplexChangeTask.RESULT.FAILED, game_postponed_tasks.ComplexChangeTask.STEP.ERROR, ()))


class GiveStabilityUncommonTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_UNCOMMON


class GiveStabilityRareTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_RARE


class GiveStabilityEpicTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_EPIC


class GiveStabilityLegendaryTests(GiveStabilityMixin, utils_testcase.TestCase):
    CARD = types.CARD.GIVE_STABILITY_LEGENDARY
