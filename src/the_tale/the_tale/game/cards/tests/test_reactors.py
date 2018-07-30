
import smart_imports

smart_imports.all()


class Simple3Tests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.ADD_BONUS_ENERGY_RARE
        self.next_card_type = types.CARD.ADD_BONUS_ENERGY_EPIC

        self.reactor = self.own_card_type.combiners[0]

        self.assertEqual(self.reactor.__class__, reactors.Simple3)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)
        self.assertEqual(self.reactor.next_card_type, self.next_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '3 x «магический вихрь» => «энергетический шторм»')

    def test_combine__not_3(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card.type, self.next_card_type)


class Special3Tests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.SHORT_TELEPORT
        self.next_card_type = types.CARD.LONG_TELEPORT

        self.reactor = self.own_card_type.combiners[0]

        self.assertEqual(self.reactor.__class__, reactors.Special3)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)
        self.assertEqual(self.reactor.next_card_type_name, 'LONG_TELEPORT')
        self.assertEqual(self.reactor.next_card_type, self.next_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '3 x «телепорт» => «ТАРДИС»')

    def test_combine__not_3(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card.type, self.next_card_type)


class SameHabbits3Test(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.CHANGE_HABIT_UNCOMMON
        self.next_card_type = types.CARD.CHANGE_HABIT_RARE

        self.habit = game_relations.HABIT_TYPE.random()
        self.direction = random.choice((-1, 1))

        self.reactor = self.own_card_type.combiners[1]

        self.assertEqual(self.reactor.__class__, reactors.SameHabbits3)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)
        self.assertEqual(self.reactor.next_card_type, self.next_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '3 x одинаковых «прозрение» => «откровение» с тем же эффектом')

    def test_combine__not_3(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__data_not_equal(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=-self.direction),))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, habit=self.habit, direction=self.direction),))
        self.assertEqual(new_card.type, self.next_card_type)


class Same2Tests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.CHANGE_PREFERENCE

        self.reactor = self.own_card_type.combiners[0]

        self.assertEqual(self.reactor.__class__, reactors.Same2)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '2 x «свежий взгляд» => «свежий взгляд» с другим эффектом')

    def test_combine__not_2(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        for i in range(100):
            preference_1 = heroes_relations.PREFERENCE_TYPE.random()
            preference_2 = heroes_relations.PREFERENCE_TYPE.random()

            new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, preference=preference_1),
                                             self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, preference=preference_2)))

            self.assertNotEqual(new_card.data['preference_id'], preference_1.value)
            self.assertNotEqual(new_card.data['preference_id'], preference_2.value)
            self.assertEqual(new_card.type, self.own_card_type)


class SamePower3Tests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.ADD_PERSON_POWER_RARE
        self.next_card_type = types.CARD.ADD_PERSON_POWER_EPIC

        self.direction = random.choice((-1, 1))

        self.reactor = self.own_card_type.combiners[-1]

        self.assertEqual(self.reactor.__class__, reactors.SamePower3)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)
        self.assertEqual(self.reactor.next_card_type, self.next_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '3 x одинаковых «неожиданное обстоятельство» => «афера» с тем же эффектом')

    def test_combine__not_2(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__data_not_equal(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=-self.direction),))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=self.direction),))
        self.assertEqual(new_card.type, self.next_card_type)


class SameEqual2Tests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.own_card_type = types.CARD.ADD_PERSON_POWER_COMMON

        self.reactor = self.own_card_type.combiners[0]

        self.assertEqual(self.reactor.__class__, reactors.SameEqual2)

    def test_initialized(self):
        self.assertEqual(self.reactor.own_card_type, self.own_card_type)

    def test_description(self):
        self.assertEqual(self.reactor.descrption(), '2 x одинаковых «случай» => «случай» с другим эффектом')

    def test_combine__not_2(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__unexpected_types(self):
        wrong_card_type = types.CARD.random(exclude=(self.own_card_type,))
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=wrong_card_type)))
        self.assertEqual(new_card, None)

    def test_combine__not_equal(self):
        new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=1),
                                         self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=-1)))
        self.assertEqual(new_card, None)

    def test_combine__success(self):
        for i in range(100):
            preference_1 = heroes_relations.PREFERENCE_TYPE.random()
            preference_2 = heroes_relations.PREFERENCE_TYPE.random()

            old_direction, new_direction = random.sample([-1, 1], 2)

            new_card = self.reactor.combine((self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=old_direction),
                                             self.own_card_type.effect.create_card(available_for_auction=True, type=self.own_card_type, direction=old_direction)))

            self.assertEqual(new_card.data['direction'], new_direction)
            self.assertEqual(new_card.type, self.own_card_type)
