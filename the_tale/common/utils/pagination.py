# coding: utf-8


class Paginator(object):

    def __init__(self, current_page_number, records_number, records_on_page, url_builder, inverse=False):
        self.current_page_number = current_page_number
        self.records_number = records_number
        self.records_on_page = records_on_page
        self.url_builder = url_builder
        self.inverse = inverse

        self._calculate_pages_count()

    @classmethod
    def get_page_numbers(cls, records_number, records_on_page):
        return (records_number - 1) / records_on_page + 1

    def _calculate_pages_count(self):
        if self.records_number == 0:
            self.pages_count = 0
            self.pages_numbers = []
            return

        self.pages_count = self.get_page_numbers(self.records_number, self.records_on_page)
        self.pages_numbers = range(self.pages_count)

        if self.inverse:
            self.pages_numbers = reversed(self.pages_numbers)

    @property
    def wrong_page_number(self): return self.current_page_number and self.current_page_number >= self.pages_count # zero page always exists

    @property
    def last_page_url(self): return self.url_builder(page=max(self.pages_count, 1))

    @property
    def first_page_url(self): return self.url_builder(page=1)

    def page_borders(self, page):
        '''
        page numbers must start with 0
        '''

        if page > self.pages_count:
            return None, None

        record_from = page * self.records_on_page
        record_to = record_from + self.records_on_page

        return record_from, record_to
