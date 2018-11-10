
import smart_imports

smart_imports.all()


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='chronicle')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

########################################
# filters
########################################


class IndexFilter(utils_list_filter.ListFilter):
    ELEMENTS = [utils_list_filter.reset_element(),
                utils_list_filter.choice_element('город:',
                                                 attribute='place',
                                                 choices=lambda x: [(None, 'все')] + places_storage.places.get_choices()),
                utils_list_filter.choice_element('мастер:',
                                                 attribute='person',
                                                 choices=lambda x: [(None, 'все')] + persons_objects.Person.form_choices())]

########################################
# views
########################################


@utils_views.PageNumberProcessor(default_value=(2 << 31))
@places_views.PlaceProcessor(error_message='Город не найден', get_name='place', context_name='place', default_value=None)
@persons_views.PersonProcessor(error_message='Мастер не найден', get_name='person', context_name='person', default_value=None)
@resource('')
def index(context):

    tags = [object.meta_object().tag
            for object in (context.place, context.person)
            if object is not None]

    page, total_records, events = tt_services.chronicle.cmd_get_events(page=context.page+1,
                                                                       tags=tags,
                                                                       records_on_page=conf.settings.RECORDS_ON_PAGE)

    page -= 1

    url_builder = dext_urls.UrlBuilder(dext_urls.url('game:chronicle:'),
                                       arguments={'page': context.page,
                                                  'place': context.place.id if context.place else None,
                                                  'person': context.person.id if context.person else None})

    if page != context.page and 'page' in context.django_request.GET:
        return dext_views.Redirect(url_builder(page=page + 1))

    filter = IndexFilter(url_builder=url_builder,
                         values={'place': context.place.id if context.place else None,
                                 'person': context.person.id if context.person else None})

    paginator = utils_pagination.Paginator(page,
                                           total_records,
                                           conf.settings.RECORDS_ON_PAGE,
                                           url_builder,
                                           inverse=True)

    tt_api_events_log.fill_events_wtih_meta_objects(events)

    return dext_views.Page('chronicle/index.html',
                           content={'events': events,
                                    'place': context.place,
                                    'person': context.person,
                                    'paginator': paginator,
                                    'index_filter': filter,
                                    'url_builder': url_builder,
                                    'resource': context.resource})
