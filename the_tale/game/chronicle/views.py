# coding: utf-8

from django.core.urlresolvers import reverse
from django.db import models

from dext.views import handler, validator, validate_argument
from dext.utils.decorators import nested_commit_on_success
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.enum import create_enum
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype

from game.map.places.prototypes import PlacePrototype

from game.chronicle.models import Record
from game.chronicle.conf import chronicle_settings
from game.chronicle.prototypes import RecordPrototype

class ChronicleResource(Resource):

    def initialize(self, *args, **kwargs):
        super(ChronicleResource, self).initialize(*args, **kwargs)

    @validate_argument('page', int, 'chronicle', u'неверная страница')
    @validate_argument('place', PlacePrototype.get_by_id, 'chronicle', u'неверный идентификатор города')
    @handler('', method='get')
    def index(self, page=1, place=None):

        records_query = Record.objects.all()

        is_filtering = False

        if place is not None:
            is_filtering = True
            pass

        url_builder = UrlBuilder(reverse('game:chronicle:'), arguments={'place': place.id if place else None})

        records_count = records_query.count()

        page = int(page) - 1

        paginator = Paginator(page, records_count, chronicle_settings.RECORDS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        record_from, record_to = paginator.page_borders(page)

        records = [ RecordPrototype(record) for record in records_query.select_related().order_by('created_at', 'created_at_turn')[record_from:record_to]]

        return self.template('chronicle/index.html',
                             {'records': records,
                              'is_filtering': is_filtering,
                              'current_page_number': page,
                              'place': place,
                              'paginator': paginator,
                              'url_builder': url_builder} )
