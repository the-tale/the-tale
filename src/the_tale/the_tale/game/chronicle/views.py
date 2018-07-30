
import smart_imports

smart_imports.all()


class IndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.choice_element('город:', attribute='place', choices=lambda x: [(None, 'все')] + places_storage.places.get_choices()),
                utils_list_filter.choice_element('мастер:', attribute='person', choices=lambda x: [(None, 'все')] + persons_objects.Person.form_choices())]


class ChronicleResource(utils_resources.Resource):

    def initialize(self, *args, **kwargs):
        super(ChronicleResource, self).initialize(*args, **kwargs)

    @dext_old_views.validate_argument('page', int, 'chronicle', 'неверная страница')
    @dext_old_views.validate_argument('place', lambda value: places_storage.places[int(value)], 'chronicle', 'неверный идентификатор города')
    @dext_old_views.validate_argument('person', lambda value: persons_storage.persons[int(value)], 'chronicle', 'неверный идентификатор Мастера')
    @dext_old_views.handler('', method='get')
    def index(self, page=None, place=None, person=None):

        records_query = models.Record.objects.all()

        if place is not None:
            records_query = records_query.filter(actors__place_id=place.id)

        if person is not None:
            records_query = records_query.filter(actors__person_id=person.id)

        url_builder = dext_urls.UrlBuilder(django_reverse('game:chronicle:'), arguments={'place': place.id if place else None,
                                                                                         'person': person.id if person else None})

        index_filter = IndexFilter(url_builder=url_builder, values={'place': place.id if place else None,
                                                                    'person': person.id if person else None})

        records_count = records_query.count()

        if page is None:
            page = utils_pagination.Paginator.get_page_numbers(records_count, conf.settings.RECORDS_ON_PAGE)
            if page == 0:
                page = 1

        page = int(page) - 1

        paginator = utils_pagination.Paginator(page, records_count, conf.settings.RECORDS_ON_PAGE, url_builder, inverse=True)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        record_from, record_to = paginator.page_borders(page)

        records = [prototypes.RecordPrototype(record) for record in records_query.select_related().order_by('created_at', 'created_at_turn')[record_from:record_to]]

        records = list(reversed(records))

        return self.template('chronicle/index.html',
                             {'records': records,
                              'place': place,
                              'paginator': paginator,
                              'index_filter': index_filter,
                              'url_builder': url_builder})
