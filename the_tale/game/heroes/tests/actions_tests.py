# coding: utf-8

import mock

from common.utils import testcase

from game.heroes.actions import ActionBase, ActionsContainer


# class ActionTests(testcase.TestCase):

#     def setUp(self):
#         super(ActionTests, self).setUp()
#         self.action = ActionBase(percents=0.6, description=u'bla-bla', info_link=u'/info')

#     def test_create(self):
#         self.assertEqual(self.action._container, None)
#         self.assertEqual(self.action.percents, 0.6)
#         self.assertEqual(self.action.description, u'bla-bla')
#         self.assertEqual(self.action.info_link, u'/info')

#     def test_serialization(self):
#         self.assertEqual(self.action.serialize(), ActionBase.deserialize(self.action.serialize()).serialize())

#     def test_percents_change(self):
#         with mock.patch.object(self.action, '_container') as container:
#             self.action.percents = 0.7
#         self.assertEqual(self.action.percents, 0.7)
#         self.assertTrue(container.updated)


# class ActionsContainerTests(testcase.TestCase):

#     def setUp(self):
#         super(ActionsContainerTests, self).setUp()
#         self.action_1 = ActionBase(percents=0.1, description=u'bla-1', info_link=u'/info-1')
#         self.action_2 = ActionBase(percents=0.2, description=u'bla-2', info_link=u'/info-2')
#         self.action_3 = ActionBase(percents=0.3, description=u'bla-3', info_link=u'/info-3')

#         self.container = ActionsContainer()

#         self.container.push_action(self.action_1)
#         self.container.push_action(self.action_2)
#         self.container.push_action(self.action_3)

#     def test_create(self):
#         container = ActionsContainer()
#         self.assertFalse(container.updated)
#         self.assertEqual(container._actions, [])

#     def test_serialization(self):
#         self.assertEqual(self.container.serialize(), ActionsContainer.deserialize(self.container.serialize()).serialize())

#         container = ActionsContainer.deserialize(self.container.serialize())
#         for action in container._actions:
#             self.assertEqual(id(action._container), id(container))

#     def test_push_action(self):
#         self.assertEqual([a.percents for a in self.container._actions], [0.1, 0.2, 0.3])

#         action_4 = ActionBase(percents=0.4, description=u'bla-4', info_link=u'/info-4')

#         self.container.updated = False
#         self.container.push_action(action_4)
#         self.assertTrue(self.container.updated)
#         self.assertEqual([a.percents for a in self.container._actions], [0.1, 0.2, 0.3, 0.4])


#     def test_pop_action(self):
#         self.assertEqual([a.percents for a in self.container._actions], [0.1, 0.2, 0.3])
#         self.container.updated = False

#         action = self.container.pop_action()
#         self.assertEqual(action.percents, 0.3)
#         self.assertTrue(self.container.updated)
#         self.assertEqual([a.percents for a in self.container._actions], [0.1, 0.2])

#     def test_current_action(self):
#         self.assertEqual(self.container.current_action.percents, self.action_3.percents)
