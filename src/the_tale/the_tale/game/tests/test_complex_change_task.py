
import smart_imports

smart_imports.all()


class ComplexChangeTasksTests(utils_testcase.TestCase):

    def setUp(self):
        super(ComplexChangeTasksTests, self).setUp()

        logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.storage = logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        card_type = cards_types.CARD.ADD_GOLD_COMMON

        self.card = card_type.effect.create_card(card_type, available_for_auction=True)

        cards_logic.change_cards(owner_id=self.hero.id,
                                 operation_type='test',
                                 to_add=[self.card])

        self.task = cards_postponed_tasks.UseCardTask(processor_id=self.card.type.value,
                                                      hero_id=self.hero.id,
                                                      data={'hero_id': self.hero.id,
                                                            'card': {'id': self.card.uid.hex,
                                                                     'data': self.card.serialize()}})

    def test_create(self):
        self.assertTrue(issubclass(cards_postponed_tasks.UseCardTask, postponed_tasks.ComplexChangeTask))
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.UNPROCESSED)

    def test_serialization(self):
        self.assertEqual(self.task.serialize(), cards_postponed_tasks.UseCardTask.deserialize(self.task.serialize()).serialize())

    def test_response_data(self):
        self.assertEqual(self.task.processed_data, {})

    def test_banned(self):
        self.hero.ban_state_end_at = datetime.datetime.now() + datetime.timedelta(days=1)
        heroes_logic.save_hero(self.hero)
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.BANNED)

    @mock.patch('the_tale.game.cards.effects.BaseEffect.check_hero_conditions', lambda *argv, **kwargs: False)
    def test_check_hero_conditions__failed(self):
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.ERROR)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.HERO_CONDITIONS_NOT_PASSED)

    def test_process_can_not_process(self):

        with mock.patch('the_tale.game.cards.effects.AddGold.use',
                        lambda self, task, storage: (postponed_tasks.ComplexChangeTask.RESULT.FAILED, None, ())):
            self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage),
                             POSTPONED_TASK_LOGIC_RESULT.ERROR)
            self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.CAN_NOT_PROCESS)

    def test_process_success(self):
        self.assertEqual(self.task.process(postponed_tasks_helpers.FakePostpondTaskPrototype(), self.storage),
                         POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, postponed_tasks.ComplexChangeTask.STATE.PROCESSED)
