
import unittest
import datetime

from .. import checkers
from .. import constants


class IsPlayerParticipateInGame(unittest.TestCase):

    def test(self):
        now = datetime.datetime.utcnow()
        past = now - datetime.timedelta(seconds=constants.INACTIVE_PREMIUM_LIVETIME)
        future = now + datetime.timedelta(seconds=constants.INACTIVE_PREMIUM_LIVETIME)

        data = [[{'is_banned': True, 'is_premium': True, 'active_end_at': past}, False],
                [{'is_banned': True, 'is_premium': True, 'active_end_at': now}, False],
                [{'is_banned': True, 'is_premium': True, 'active_end_at': future}, False],

                [{'is_banned': True, 'is_premium': False, 'active_end_at': past}, False],
                [{'is_banned': True, 'is_premium': False, 'active_end_at': now}, False],
                [{'is_banned': True, 'is_premium': False, 'active_end_at': future}, False],

                [{'is_banned': False, 'is_premium': True, 'active_end_at': past}, False],
                [{'is_banned': False, 'is_premium': True, 'active_end_at': now}, True],
                [{'is_banned': False, 'is_premium': True, 'active_end_at': future}, True],

                [{'is_banned': False, 'is_premium': False, 'active_end_at': past}, False],
                [{'is_banned': False, 'is_premium': False, 'active_end_at': now}, False],
                [{'is_banned': False, 'is_premium': False, 'active_end_at': future}, True]]

        for input, output in data:
            self.assertEqual(checkers.is_player_participate_in_game(**input), output)
