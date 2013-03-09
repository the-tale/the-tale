# coding: utf-8

from django.core.urlresolvers import reverse

from dext.views import handler, validate_argument
from dext.utils.urls import UrlBuilder

from common.utils import list_filter
from common.utils.resources import Resource
from common.utils.pagination import Paginator

from game.map.places.prototypes import PlacePrototype
from game.map.places.storage import places_storage

from game.chronicle.models import Record
from game.chronicle.conf import chronicle_settings
from game.chronicle.prototypes import RecordPrototype


class IndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.choice_element(u'город:', attribute='place', choices=lambda x: [(None, u'все')] + places_storage.get_choices()) ]


class ChronicleResource(Resource):

    def initialize(self, *args, **kwargs):
        super(ChronicleResource, self).initialize(*args, **kwargs)

    @validate_argument('page', int, 'chronicle', u'неверная страница')
    @validate_argument('place', PlacePrototype.get_by_id, 'chronicle', u'неверный идентификатор города')
    @handler('', method='get')
    def index(self, page=None, place=None):

        records_query = Record.objects.all()

        if place is not None:
            records_query = records_query.filter(actors__place_id=place.id)

        url_builder = UrlBuilder(reverse('game:chronicle:'), arguments={'place': place.id if place else None})

        index_filter = IndexFilter(url_builder=url_builder, values={'place': place.id if place else None})

        records_count = records_query.count()

        if page is None:
            page = Paginator.get_page_numbers(records_count, chronicle_settings.RECORDS_ON_PAGE)
            if page == 0: page = 1
        page = int(page) - 1

        paginator = Paginator(page, records_count, chronicle_settings.RECORDS_ON_PAGE, url_builder, inverse=True)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        record_from, record_to = paginator.page_borders(page)

        records = [ RecordPrototype(record) for record in records_query.select_related().order_by('created_at', 'created_at_turn')[record_from:record_to]]

        records = list(reversed(records))

        return self.template('chronicle/index.html',
                             {'records': records,
                              'place': place,
                              'paginator': paginator,
                              'index_filter': index_filter,
                              'url_builder': url_builder} )
