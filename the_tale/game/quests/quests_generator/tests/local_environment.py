# coding: utf-8

from common.utils import testcase

from game.quests.quests_generator.environment import LocalEnvironment


class LocalEnvironmentTest(testcase.TestCase):

    def setUp(self):
        super(LocalEnvironmentTest, self).setUp()
        self.env = LocalEnvironment()

    def test_after_constuction(self):
        self.assertEqual(self.env._storage, {})

    def test_register(self):
        self.env.register('name', 'value')
        self.assertEqual(self.env._storage, {'name': 'value'})
        self.assertEqual(self.env.name, 'value')
        getattr(self.env, 'name')

    def test_wrong_argument(self):
        self.assertRaises(AttributeError, getattr, self.env, 'name')

    def test_serialize(self):
        self.env.register('name', 'value')

        data = self.env.serialize()

        env = LocalEnvironment()
        env.deserialize(data)

        self.assertEqual(self.env, env)
