
import smart_imports

smart_imports.all()


effects = companions_abilities_effects


class ContainerTests(utils_testcase.TestCase):

    def setUp(self):
        super(ContainerTests, self).setUp()

        self.container_1 = companions_abilities_container.Container(common=(effects.ABILITIES.PEACEFUL, effects.ABILITIES.SNEAKY),
                                                                    start=frozenset(),
                                                                    coherence=effects.ABILITIES.MANAGING,
                                                                    honor=None,
                                                                    peacefulness=effects.ABILITIES.AGGRESSIVE)

        self.container_2 = companions_abilities_container.Container(common=(effects.ABILITIES.PEACEFUL, effects.ABILITIES.HONEST, effects.ABILITIES.CANNY),
                                                                    start=frozenset((effects.ABILITIES.BONA_FIDE, effects.ABILITIES.PEACEFUL)),
                                                                    coherence=None,
                                                                    honor=effects.ABILITIES.SNEAKY,
                                                                    peacefulness=effects.ABILITIES.AGGRESSIVE)

    def test_initialization(self):
        self.assertEqual(self.container_1.common, (effects.ABILITIES.PEACEFUL, effects.ABILITIES.SNEAKY))
        self.assertEqual(self.container_1.start, frozenset())
        self.assertEqual(self.container_1.coherence, effects.ABILITIES.MANAGING)
        self.assertEqual(self.container_1.honor, None)
        self.assertEqual(self.container_1.peacefulness, effects.ABILITIES.AGGRESSIVE)

        self.assertEqual(self.container_2.common, (effects.ABILITIES.PEACEFUL, effects.ABILITIES.HONEST, effects.ABILITIES.CANNY))
        self.assertEqual(self.container_2.start, frozenset((effects.ABILITIES.BONA_FIDE, effects.ABILITIES.PEACEFUL)))
        self.assertEqual(self.container_2.coherence, None)
        self.assertEqual(self.container_2.honor, effects.ABILITIES.SNEAKY)
        self.assertEqual(self.container_2.peacefulness, effects.ABILITIES.AGGRESSIVE)

    def test_serialization(self):
        self.assertEqual(self.container_1.serialize(), companions_abilities_container.Container.deserialize(self.container_1.serialize()).serialize())
        self.assertEqual(self.container_2.serialize(), companions_abilities_container.Container.deserialize(self.container_2.serialize()).serialize())

    def test_has_duplicates(self):
        self.assertFalse(self.container_1.has_duplicates())
        self.assertTrue(self.container_2.has_duplicates())

    def test_has_same_effects(self):
        self.assertTrue(self.container_1.has_same_effects())
        self.assertTrue(self.container_2.has_same_effects())

        container_3 = companions_abilities_container.Container(common=(effects.ABILITIES.OBSTINATE, effects.ABILITIES.PEACEFUL),
                                                               start=frozenset((effects.ABILITIES.CANNY,)),
                                                               coherence=None,
                                                               honor=None,
                                                               peacefulness=None)

        self.assertFalse(container_3.has_same_effects())

    def test_not_ordered(self):
        self.assertRaises(companions_abilities_exceptions.NotOrderedUIDSError, companions_abilities_container.Container,
                          common=set((effects.ABILITIES.PEACEFUL, effects.ABILITIES.HONEST, effects.ABILITIES.CANNY)))

    def test_start_abilities(self):
        self.assertEqual(set(ability for ability in self.container_1.start_abilities),
                         set((effects.ABILITIES.MANAGING, effects.ABILITIES.AGGRESSIVE)))
        self.assertEqual(set(ability for ability in self.container_2.start_abilities),
                         set((effects.ABILITIES.BONA_FIDE, effects.ABILITIES.PEACEFUL, effects.ABILITIES.SNEAKY, effects.ABILITIES.AGGRESSIVE)))

    def test_coherence_abilities(self):
        self.assertEqual([(coherence, ability) for coherence, ability in self.container_1.coherence_abilities],
                         [(33, effects.ABILITIES.PEACEFUL), (66, effects.ABILITIES.SNEAKY)])

        self.assertEqual([(coherence, ability) for coherence, ability in self.container_2.coherence_abilities],
                         [(25, effects.ABILITIES.PEACEFUL), (50, effects.ABILITIES.HONEST), (75, effects.ABILITIES.CANNY)])

    def test_all_abilities(self):
        self.assertEqual(set((coherence, ability) for coherence, ability in self.container_1.all_abilities),
                         set(((33, effects.ABILITIES.PEACEFUL), (66, effects.ABILITIES.SNEAKY), (0, effects.ABILITIES.MANAGING), (0, effects.ABILITIES.AGGRESSIVE))))
        self.assertEqual(set((coherence, ability) for coherence, ability in self.container_2.all_abilities),
                         set(((25, effects.ABILITIES.PEACEFUL), (50, effects.ABILITIES.HONEST), (75, effects.ABILITIES.CANNY),
                              (0, effects.ABILITIES.BONA_FIDE), (0, effects.ABILITIES.PEACEFUL), (0, effects.ABILITIES.SNEAKY), (0, effects.ABILITIES.AGGRESSIVE))))

    def check_abilities_for_coherence(self, container, coherence, uids):
        self.assertEqual(set(ability.value for ability in container.abilities_for_coherence(coherence)),
                         set(uids))

    def test_abilities_for_coherence(self):
        self.check_abilities_for_coherence(self.container_1, 100, [5, 9, 3, 4])
        self.check_abilities_for_coherence(self.container_1, 66, [5, 9, 3, 4])
        self.check_abilities_for_coherence(self.container_1, 50, [5, 3, 4])
        self.check_abilities_for_coherence(self.container_1, 33, [5, 3, 4])
        self.check_abilities_for_coherence(self.container_1, 32, [3, 4])
        self.check_abilities_for_coherence(self.container_1, 9, [3, 4])
        self.check_abilities_for_coherence(self.container_1, 0, [3, 4])

        self.check_abilities_for_coherence(self.container_2, 100, [5, 8, 7, 2, 5, 9, 4])
        self.check_abilities_for_coherence(self.container_2, 75, [5, 8, 7, 2, 5, 9, 4])
        self.check_abilities_for_coherence(self.container_2, 50, [5, 8, 2, 5, 9, 4])
        self.check_abilities_for_coherence(self.container_2, 25, [5, 2, 5, 9, 4])
        self.check_abilities_for_coherence(self.container_2, 24, [2, 5, 9, 4])
        self.check_abilities_for_coherence(self.container_2, 0, [2, 5, 9, 4])

    def test_modify_attribute(self):
        with mock.patch('the_tale.game.companions.abilities.effects.Base.modify_attribute', lambda self, abilities_levels, modifier, value: value * 2):
            self.assertEqual(self.container_1.modify_attribute(100, {}, None, 1, is_dead=False), 16)
            self.assertEqual(self.container_1.modify_attribute(66, {}, None, 1, is_dead=False), 16)
            self.assertEqual(self.container_1.modify_attribute(50, {}, None, 1, is_dead=False), 8)
            self.assertEqual(self.container_1.modify_attribute(33, {}, None, 1, is_dead=False), 8)
            self.assertEqual(self.container_1.modify_attribute(32, {}, None, 1, is_dead=False), 4)
            self.assertEqual(self.container_1.modify_attribute(9, {}, None, 1, is_dead=False), 4)

            self.assertEqual(self.container_2.modify_attribute(100, {}, None, 1, is_dead=False), 128)
            self.assertEqual(self.container_2.modify_attribute(75, {}, None, 1, is_dead=False), 128)
            self.assertEqual(self.container_2.modify_attribute(50, {}, None, 1, is_dead=False), 64)
            self.assertEqual(self.container_2.modify_attribute(25, {}, None, 1, is_dead=False), 32)
            self.assertEqual(self.container_2.modify_attribute(24, {}, None, 1, is_dead=False), 16)
            self.assertEqual(self.container_2.modify_attribute(0, {}, None, 1, is_dead=False), 16)

            self.assertEqual(self.container_1.modify_attribute(100, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_1.modify_attribute(66, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_1.modify_attribute(50, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_1.modify_attribute(33, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_1.modify_attribute(32, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_1.modify_attribute(9, {}, None, 1, is_dead=True), 1)

            self.assertEqual(self.container_2.modify_attribute(100, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_2.modify_attribute(75, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_2.modify_attribute(50, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_2.modify_attribute(25, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_2.modify_attribute(24, {}, None, 1, is_dead=True), 1)
            self.assertEqual(self.container_2.modify_attribute(0, {}, None, 1, is_dead=True), 1)

    def test_check_attribute(self):
        with mock.patch('the_tale.game.companions.abilities.effects.Base.check_attribute', lambda self, modifier: True):
            self.assertEqual(self.container_1.check_attribute(100, None, is_dead=False), True)
            self.assertEqual(self.container_1.check_attribute(66, None, is_dead=False), True)
            self.assertEqual(self.container_1.check_attribute(50, None, is_dead=False), True)
            self.assertEqual(self.container_1.check_attribute(33, None, is_dead=False), True)
            self.assertEqual(self.container_1.check_attribute(32, None, is_dead=False), True)
            self.assertEqual(self.container_1.check_attribute(9, None, is_dead=False), True)

            self.assertEqual(self.container_2.check_attribute(100, None, is_dead=False), True)
            self.assertEqual(self.container_2.check_attribute(75, None, is_dead=False), True)
            self.assertEqual(self.container_2.check_attribute(50, None, is_dead=False), True)
            self.assertEqual(self.container_2.check_attribute(25, None, is_dead=False), True)
            self.assertEqual(self.container_2.check_attribute(24, None, is_dead=False), True)
            self.assertEqual(self.container_2.check_attribute(0, None, is_dead=False), True)

            self.assertEqual(self.container_1.check_attribute(100, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(66, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(50, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(33, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(32, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(9, None, is_dead=True), False)

            self.assertEqual(self.container_2.check_attribute(100, None, is_dead=True), False)
            self.assertEqual(self.container_2.check_attribute(75, None, is_dead=True), False)
            self.assertEqual(self.container_2.check_attribute(50, None, is_dead=True), False)
            self.assertEqual(self.container_2.check_attribute(25, None, is_dead=True), False)
            self.assertEqual(self.container_2.check_attribute(24, None, is_dead=True), False)
            self.assertEqual(self.container_2.check_attribute(0, None, is_dead=True), False)

        with mock.patch('the_tale.game.companions.abilities.effects.Base.check_attribute', lambda self, modifier: False):
            self.assertEqual(self.container_1.check_attribute(100, None, is_dead=False), False)
            self.assertEqual(self.container_1.check_attribute(66, None, is_dead=False), False)
            self.assertEqual(self.container_1.check_attribute(50, None, is_dead=False), False)
            self.assertEqual(self.container_1.check_attribute(33, None, is_dead=False), False)
            self.assertEqual(self.container_1.check_attribute(32, None, is_dead=False), False)
            self.assertEqual(self.container_1.check_attribute(9, None, is_dead=False), False)

            self.assertEqual(self.container_2.check_attribute(100, None, is_dead=False), False)
            self.assertEqual(self.container_2.check_attribute(75, None, is_dead=False), False)
            self.assertEqual(self.container_2.check_attribute(50, None, is_dead=False), False)
            self.assertEqual(self.container_2.check_attribute(25, None, is_dead=False), False)
            self.assertEqual(self.container_2.check_attribute(24, None, is_dead=False), False)
            self.assertEqual(self.container_2.check_attribute(0, None, is_dead=False), False)

    def test_modify_attribute__allow_for_dead(self):
        self.container_1.start = frozenset(self.container_1.start | set((effects.ABILITIES.TEMPORARY,)))

        with mock.patch('the_tale.game.companions.abilities.effects.Base.modify_attribute', lambda self, abilities_levels, modifier, value: value * 2):
            self.assertEqual(self.container_1.modify_attribute(100, {}, None, 1, is_dead=True), 2)
            self.assertEqual(self.container_1.modify_attribute(66, {}, None, 1, is_dead=True), 2)
            self.assertEqual(self.container_1.modify_attribute(50, {}, None, 1, is_dead=True), 2)
            self.assertEqual(self.container_1.modify_attribute(33, {}, None, 1, is_dead=True), 2)
            self.assertEqual(self.container_1.modify_attribute(32, {}, None, 1, is_dead=True), 2)
            self.assertEqual(self.container_1.modify_attribute(9, {}, None, 1, is_dead=True), 2)

    def test_check_attribute__allow_for_dead(self):
        self.container_1.start = frozenset(self.container_1.start | set((effects.ABILITIES.TEMPORARY,)))
        with mock.patch('the_tale.game.companions.abilities.effects.Base.check_attribute', lambda self, modifier: True):
            self.assertEqual(self.container_1.check_attribute(100, None, is_dead=True), True)
            self.assertEqual(self.container_1.check_attribute(66, None, is_dead=True), True)
            self.assertEqual(self.container_1.check_attribute(50, None, is_dead=True), True)
            self.assertEqual(self.container_1.check_attribute(33, None, is_dead=True), True)
            self.assertEqual(self.container_1.check_attribute(32, None, is_dead=True), True)
            self.assertEqual(self.container_1.check_attribute(9, None, is_dead=True), True)

        with mock.patch('the_tale.game.companions.abilities.effects.Base.check_attribute', lambda self, modifier: False):
            self.assertEqual(self.container_1.check_attribute(100, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(66, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(50, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(33, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(32, None, is_dead=True), False)
            self.assertEqual(self.container_1.check_attribute(9, None, is_dead=True), False)

    def test_can_be_freezed(self):
        self.assertTrue(self.container_1.can_be_freezed())
        self.assertTrue(self.container_2.can_be_freezed())

    def test_can_be_freezed_2(self):
        self.container_1.start = frozenset(self.container_1.start | set((effects.ABILITIES.TEMPORARY,)))

        self.assertFalse(self.container_1.can_be_freezed())
