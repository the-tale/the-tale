# coding: utf-8


class Paginator(object):

    def __init__(self, records_number, records_on_page):
        self.records_number = records_number
        self.records_on_page = records_on_page

        self._calculate_pages_count()

    def _calculate_pages_count(self):
        self.pages_count = (self.records_number + 1) / self.records_on_page
        if (self.records_number + 1) % self.records_on_page:
            self.pages_count += 1

    def page_borders(self, page):
        '''
        page numbers must start with 0
        '''

        if page > self.pages_count:
            return None, None

        record_from = page * self.records_on_page
        record_to = record_from + self.records_on_page

        return record_from, record_to
