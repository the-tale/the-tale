
import uuid
import datetime

from .. import objects

from . import helpers


class BindCodeTests(helpers.BaseTests):

    def test_data(self):
        created_at = datetime.datetime.now()
        expire_at = datetime.datetime.now()
        code = uuid.uuid4()

        bind_code = objects.BindCode(code=code,
                                     created_at=created_at,
                                     expire_at=expire_at)

        self.assertEqual(bind_code.data(),
                         {'created_at': created_at.isoformat(),
                          'expire_at': expire_at.isoformat(),
                          'code': code.hex})
