
import smart_imports

smart_imports.all()


class POWER_TYPE_FILTER(rels_django.DjangoEnum):
    records = (('ALL', 0, 'всё'),
               ('PERSONAL', 1, 'ближний круг'),
               ('CROWD', 2, 'народное'))


HISTORY_FILTERS = [utils_list_filter.reset_element(),
                   utils_list_filter.static_element('игрок:', attribute='account'),
                   utils_list_filter.choice_element('тип влияния:',
                                                    attribute='power_type',
                                                    choices=POWER_TYPE_FILTER.select('value', 'text'),
                                                    default_value=POWER_TYPE_FILTER.ALL.value),
                   utils_list_filter.choice_element('город:',
                                                    attribute='place',
                                                    choices=lambda x: [(None, 'все')] + places_storage.places.get_choices()),
                   utils_list_filter.choice_element('мастер:',
                                                    attribute='person',
                                                    choices=lambda x: [(None, 'все')] + persons_objects.Person.form_choices())]


class HistoryFilter(utils_list_filter.ListFilter):
    ELEMENTS = HISTORY_FILTERS


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='politic-power')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())


########################################
# views
########################################

@dext_views.RelationArgumentProcessor(relation=POWER_TYPE_FILTER, error_message='неверный тип влияния',
                                      default_value=POWER_TYPE_FILTER.ALL,
                                      get_name='power_type', context_name='power_type')
@accounts_views.AccountProcessor(error_message='Игрок не найден', get_name='account', context_name='account_filter', default_value=None)
@places_views.PlaceProcessor(error_message='Город не найден', get_name='place', context_name='place', default_value=None)
@persons_views.PersonProcessor(error_message='Мастер не найден', get_name='person', context_name='person', default_value=None)
@resource('history', name='history')
def history(context):

    url = django_reverse('game:politic-power:history')

    url_builder = dext_urls.UrlBuilder(url, arguments={'account': context.account_filter.id if context.account_filter else None,
                                                       'power_type': context.power_type.value if context.power_type else POWER_TYPE_FILTER.ALL.value,
                                                       'place': context.place.id if context.place else None,
                                                       'person': context.person.id if context.person else None})

    filter = HistoryFilter(url_builder=url_builder, values={'account': context.account_filter.nick if context.account_filter else None,
                                                            'power_type': context.power_type.value if context.power_type else None,
                                                            'place': context.place.id if context.place else None,
                                                            'person': context.person.id if context.person else None})

    if context.place and context.person:
        return dext_views.Page('politic_power/history.html',
                               content={'resource': context.resource,
                                        'error': 'Нельзя одновременно фильтровать по городу и Мастеру. Пожалуйста, выберите что-то одно.',
                                        'error_code': 'pgf-cannot-filter-by-place-and-master',
                                        'impacts': [],
                                        'limit': conf.settings.MAX_HISTORY_LENGTH,
                                        'filter': filter})
    target_type = None
    target_id = None

    actors = []

    if context.account_filter:
        actors.extend(((tt_api_impacts.OBJECT_TYPE.HERO, context.account_filter.id),
                       (tt_api_impacts.OBJECT_TYPE.ACCOUNT, context.account_filter.id)))
    else:
        actors.append((None, None))

    if context.place:
        target_type = tt_api_impacts.OBJECT_TYPE.PLACE
        target_id = context.place.id

    if context.person:
        target_type = tt_api_impacts.OBJECT_TYPE.PERSON
        target_id = context.person.id

    storages = []

    if context.power_type.is_ALL or context.power_type.is_PERSONAL:
        storages.append(game_tt_services.personal_impacts)

    if context.power_type.is_ALL or context.power_type.is_CROWD:
        storages.append(game_tt_services.crowd_impacts)

    impacts = logic.get_last_power_impacts(storages=storages,
                                           actors=actors,
                                           target_type=target_type,
                                           target_id=target_id,
                                           limit=conf.settings.MAX_HISTORY_LENGTH)

    accounts_ids = set()
    bills_ids = set()

    for impact in impacts:
        if impact.actor_type.is_ACCOUNT:
            accounts_ids.add(impact.actor_id)
        elif impact.actor_type.is_HERO:
            accounts_ids.add(impact.actor_id)
        elif impact.actor_type.is_BILL:
            bills_ids.add(impact.actor_id)

    accounts = {account.id: account
                for account in accounts_prototypes.AccountPrototype.from_query(
                    accounts_prototypes.AccountPrototype._db_filter(id__in=accounts_ids))}
    heroes = {hero.id: hero for hero in heroes_logic.load_heroes_by_account_ids(accounts_ids)}
    bills = {bill.id: bill
             for bill in bills_prototypes.BillPrototype.from_query(bills_prototypes.BillPrototype._db_filter(id__in=bills_ids))}

    return dext_views.Page('politic_power/history.html',
                           content={'resource': context.resource,
                                    'error': None,
                                    'impacts': impacts,
                                    'limit': conf.settings.MAX_HISTORY_LENGTH,
                                    'filter': filter,
                                    'accounts': accounts,
                                    'heroes': heroes,
                                    'bills': bills,
                                    'places_storage': places_storage.places,
                                    'persons_storage': persons_storage.persons})
