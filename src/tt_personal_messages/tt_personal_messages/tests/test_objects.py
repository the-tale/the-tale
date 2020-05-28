
import datetime

from .. import objects

from . import helpers


class MessageTests(helpers.BaseTests):

    def test_data_of(self):
        created_at = datetime.datetime.now()

        message = objects.Message(id=5,
                                  sender=7,
                                  recipients=[8, 9, 10],
                                  created_at=created_at,
                                  body='xx yy',
                                  visible=True)

        self.assertEqual(message.data_of(7),
                         {'created_at': created_at.isoformat(),
                          'id': 5,
                          'recipients': [8, 9, 10],
                          'removed': False,
                          'sender': 7,
                          'text': 'xx yy'})

        self.assertEqual(message.data_of(9),
                         {'created_at': created_at.isoformat(),
                          'id': 5,
                          'recipients': [9],
                          'removed': False,
                          'sender': 7,
                          'text': 'xx yy'})

        message.visible = False

        self.assertEqual(message.data_of(7),
                         {'created_at': created_at.isoformat(),
                          'id': 5,
                          'recipients': [8, 9, 10],
                          'removed': True,
                          'sender': 7,
                          'text': 'xx yy'})
