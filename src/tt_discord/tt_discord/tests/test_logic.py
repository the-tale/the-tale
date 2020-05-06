

import unittest

from .. import logic


class NormalizeNicknameTests(unittest.TestCase):

    def test(self):
        self.assertEqual(logic.normalize_nickname(''), 'unknown player')

        self.assertEqual(logic.normalize_nickname('   my nick\tis   Tiendil\r'), 'my nick is Tiendil')

        self.assertEqual(logic.normalize_nickname('discordtag'), 'unknown player')
        self.assertEqual(logic.normalize_nickname('everyone'), 'unknown player')
        self.assertEqual(logic.normalize_nickname('here'), 'unknown player')

        self.assertEqual(logic.normalize_nickname('xxx@xxx#xxx:xxx``xxx```xxx'), 'xxx?xxx?xxx?xxx``xxx???xxx')
        self.assertEqual(logic.normalize_nickname('veryveryveryveryveryveryveryveryveryveryveryverylongnickname'),
                         'veryveryveryveryveryveryveryvery')
