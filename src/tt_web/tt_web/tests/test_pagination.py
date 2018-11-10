
from ..common import pagination

from . import helpers


class PaginationTests(helpers.BaseTests):

    def test_pagination(self):
        self.assertEqual(pagination.normalize_page(page=0, records_number=0, records_on_page=100), 1)
        self.assertEqual(pagination.normalize_page(page=0, records_number=104, records_on_page=100), 1)
        self.assertEqual(pagination.normalize_page(page=1, records_number=104, records_on_page=100), 1)
        self.assertEqual(pagination.normalize_page(page=2, records_number=104, records_on_page=100), 2)
        self.assertEqual(pagination.normalize_page(page=3, records_number=104, records_on_page=100), 2)
