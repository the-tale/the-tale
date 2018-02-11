
import unittest

from ..common import unique_priority_queue


class QueueTests(unittest.TestCase):

    def setUp(self):
        self.queue = unique_priority_queue.Queue()

    def test_initialize(self):
        self.assertEqual(self.queue._heap, [])
        self.assertEqual(self.queue._set, {})

    def test_empty__empty(self):
        self.assertTrue(self.queue.empty())

    def test_empty__not_empty(self):
        self.queue.push(1, 1)
        self.assertFalse(self.queue.empty())

    def test_push(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(30, 2)

        self.assertEqual(self.queue._set, {10: 3, 20: 1, 30: 2})
        self.assertEqual([(20, 1), (30, 2), (10, 3)], [item for item in self.queue.items()])

    def test_duplicate(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(10, 2)

        self.assertEqual(self.queue._set, {10: 2, 20: 1})
        self.assertEqual([(20, 1), (10, 2)], [item for item in self.queue.items()])

    def test_pop(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(30, 2)

        self.assertEqual(self.queue.pop(), (20, 1))
        self.assertEqual(self.queue.pop(), (30, 2))
        self.assertEqual(self.queue.pop(), (10, 3))

        self.assertTrue(self.queue.empty())

    def test_pop__empty(self):
        self.assertEqual(self.queue.pop(), (None, None))

    def test_pop__duplicate(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(10, 2)

        self.assertEqual(self.queue.pop(), (20, 1))
        self.assertEqual(self.queue.pop(), (10, 2))

        self.assertTrue(self.queue.empty())

    def test_first(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(30, 2)

        self.assertEqual(self.queue.first(), (20, 1))

    def test_first__empty(self):
        self.assertEqual(self.queue.first(), (None, None))

    def test_first__duplicate(self):
        self.queue.push(10, 3)
        self.queue.push(20, 3)
        self.queue.push(5, 1)
        self.queue.push(10, 2)

        self.assertEqual(self.queue.first(), (5, 1))

    def test_clean(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(30, 2)

        self.queue.clean()

        self.assertEqual(self.queue._heap, [])
        self.assertEqual(self.queue._set, {})

        self.assertTrue(self.queue.empty())

    def test_items__empty(self):
        self.assertEqual([], [item for item in self.queue.items()])

    def test_items__has_items(self):
        self.queue.push(10, 3)
        self.queue.push(20, 1)
        self.queue.push(30, 2)

        self.assertEqual([(20, 1), (30, 2), (10, 3)], [item for item in self.queue.items()])
