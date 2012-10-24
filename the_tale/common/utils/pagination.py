# coding: utf-8


class Paginator(object):

    def __init__(self, current_page_number, records_number, records_on_page, url_builder):
        self.current_page_number = current_page_number
        self.records_number = records_number
        self.records_on_page = records_on_page
        self.url_builder = url_builder

        self._calculate_pages_count()

    def _calculate_pages_count(self):
        if self.records_number == 0:
            self.pages_count = 0
            self.pages_numbers = []
            return

        self.pages_count = (self.records_number - 1) / self.records_on_page + 1
        self.pages_numbers = range(self.pages_count)

    @property
    def wrong_page_number(self): return self.current_page_number and self.current_page_number >= self.pages_count # zero page always exists

    @property
    def last_page_url(self): return self.url_builder(page=max(self.pages_count, 1))

    def page_borders(self, page):
        '''
        page numbers must start with 0
        '''

        if page > self.pages_count:
            return None, None

        record_from = page * self.records_on_page
        record_to = record_from + self.records_on_page

        return record_from, record_to
