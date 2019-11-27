
from .. import logic
from .. import objects

from . import helpers


class ValidateRestrictionsTests(helpers.BaseTests):

    def test_hard_minimum(self):
        restrictions = objects.Restrictions(hard_minimum=-100)

        self.assertEqual(logic.validate_restrictions(restrictions, -1000),
                         (False, None))

        self.assertEqual(logic.validate_restrictions(restrictions, -100),
                         (True, -100))

        self.assertEqual(logic.validate_restrictions(restrictions, 1000),
                         (True, 1000))

    def test_soft_minimum(self):
        restrictions = objects.Restrictions(hard_minimum=None, soft_minimum=-666)

        self.assertEqual(logic.validate_restrictions(restrictions, -1000),
                         (True, -666))

        self.assertEqual(logic.validate_restrictions(restrictions, -100),
                         (True, -100))

        self.assertEqual(logic.validate_restrictions(restrictions, 1000),
                         (True, 1000))

    def test_hard_maximum(self):
        restrictions = objects.Restrictions(hard_maximum=100)

        self.assertEqual(logic.validate_restrictions(restrictions, 1000),
                         (False, None))

        self.assertEqual(logic.validate_restrictions(restrictions, 100),
                         (True, 100))

    def test_soft_maximum(self):
        restrictions = objects.Restrictions(soft_maximum=666)

        self.assertEqual(logic.validate_restrictions(restrictions, 1000),
                         (True, 666))

        self.assertEqual(logic.validate_restrictions(restrictions, 100),
                         (True, 100))
