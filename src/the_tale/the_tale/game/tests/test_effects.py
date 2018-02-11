

from the_tale.common.utils import testcase

from the_tale.game.places import relations as places_relations

from .. import effects


TEST_CONTAINER_CLASS = effects.create_container(places_relations.ATTRIBUTE)


class EffectsContainerTests(testcase.TestCase):

    def setUp(self):
        super(EffectsContainerTests, self).setUp()

        self.container = TEST_CONTAINER_CLASS()

        self.effect_1 = effects.Effect(name='x.1',
                                       attribute=places_relations.ATTRIBUTE.STABILITY,
                                       value=1,
                                       delta=0.1)
        self.effect_2 = effects.Effect(name='x.2',
                                       attribute=places_relations.ATTRIBUTE.SAFETY,
                                       value=2,
                                       delta=2)
        self.effect_3 = effects.Effect(name='x.3',
                                       attribute=places_relations.ATTRIBUTE.TRANSPORT,
                                       value=3,
                                       delta=1)

    def test_initialization(self):
        self.assertEqual(self.container.effects, [])

    def test_serialization(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        self.assertEqual(self.container, TEST_CONTAINER_CLASS.deserialize(self.container.serialize()))

    def test_add(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        self.assertEqual(self.container.effects, [self.effect_1, self.effect_2, self.effect_3])

    def test_update_step(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        self.container.update_step()

        self.assertEqual(self.effect_1.value, 0.9)
        self.assertEqual(self.effect_2.value, 0)
        self.assertEqual(self.effect_3.value, 2)

        self.assertEqual(self.container.effects, [self.effect_1, self.effect_3])

    def test_update_step__deltas(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        self.container.update_step({places_relations.ATTRIBUTE.TRANSPORT: 0.4,
                                    places_relations.ATTRIBUTE.SAFETY: 1})

        self.assertEqual(self.effect_1.value, 0.9)
        self.assertEqual(self.effect_2.value, 1)
        self.assertEqual(self.effect_3.value, 2.6)

    def test_clear(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        self.container.clear()

        self.assertEqual(self.container.effects, [])

    def test_effects_sequence_not_changed(self):
        self.container.add(self.effect_1)
        self.container.add(self.effect_2)
        self.container.add(self.effect_3)

        container = TEST_CONTAINER_CLASS.deserialize(self.container.serialize())

        self.assertEqual(container.effects, [self.effect_1, self.effect_2, self.effect_3])

        container.update_step()

        self.assertEqual([effect.name for effect in container.effects], ['x.1', 'x.3'])
