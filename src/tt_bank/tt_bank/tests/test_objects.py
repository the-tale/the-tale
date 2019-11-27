

from .. import objects

from . import helpers


class RestrictionsTests(helpers.BaseTests):

    def test_serialization(self):
        restrictions = objects.Restrictions(hard_minimum=0,
                                            hard_maximum=1,
                                            soft_minimum=2,
                                            soft_maximum=3)

        self.assertEqual(restrictions, objects.Restrictions.deserialize(restrictions.serialize()))
