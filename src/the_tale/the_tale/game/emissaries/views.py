
import smart_imports

smart_imports.all()


########################################
# processors
########################################

class EmissaryProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'current_emissary'
    DEFAULT_VALUE = None
    ERROR_MESSAGE = 'Неверный идентификатор эмиссара'

    def parse(self, context, raw_value):
        try:
            emissary_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        emissary = logic.load_emissary(emissary_id=emissary_id)

        if emissary is None:
            self.raise_wrong_value()

        return emissary


class EmissaryClanRightsProcessor(utils_views.BaseViewProcessor):
    ARG_EMISSARY_ATTRIBUTE = utils_views.ProcessorArgument(default='current_emissary')
    ARG_EMISSARY_CLAN_RIGHTS_ATTRIBUTE = utils_views.ProcessorArgument(default='emissary_clan_rights')

    def preprocess(self, context):
        emissary = getattr(context, self.emissary_attribute, None)

        if emissary is None:
            setattr(context, '', None)
            return

        clan = clans_logic.load_clan(emissary.clan_id)

        setattr(context,
                self.emissary_clan_rights_attribute,
                clans_logic.operations_rights(initiator=context.account,
                                              clan=clan,
                                              is_moderator=False))


class EmissaryInGameProcessor(utils_views.BaseViewProcessor):
    ARG_EMISSARY_ATTRIBUTE = utils_views.ProcessorArgument(default='current_emissary')

    def preprocess(self, context):
        if getattr(context, self.emissary_attribute).state.is_IN_GAME:
            return

        raise utils_views.ViewError(code='emissary.emissary_is_not_in_game',
                                    message='Эмиссар уже не участвует в игре (убит или уволен)')


class EventTypeProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'event_type'
    DEFAULT_VALUE = NotImplemented
    ERROR_MESSAGE = 'Неверный идентификатор мероприятия'

    def parse(self, context, raw_value):
        try:
            event_value = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        return relations.EVENT_TYPE(event_value)


class EventIdProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'current_event_id'
    DEFAULT_VALUE = NotImplemented
    ERROR_MESSAGE = 'Неверный идентификатор события'

    def parse(self, context, raw_value):
        try:
            event_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        return event_id


class EventPermissionProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'emissaries.no_rights'
    ERROR_MESSAGE = 'Вы не можете проводить эту операцию'

    ARG_PERMISSIONS_ATTRIBUTE = utils_views.ProcessorArgument(default='emissary_clan_rights')

    def check(self, context):
        rights = getattr(context, self.permissions_attribute)

        if rights is None:
            return False

        if hasattr(context, 'event_type'):
            event_type = context.event_type
        else:
            event_type = storage.events.get_or_load(context.current_event_id).concrete_event.TYPE

        if event_type is None:
            return False

        return getattr(rights, event_type.clan_permission)()


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='emissaries')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(clans_views.AccountClanProcessor(account_attribute='account', clan_attribute='clan'))
resource.add_processor(clans_views.ClanRightsProcessor(clan_attribute='clan'))
resource.add_processor(EmissaryProcessor(url_name='emissary'))
resource.add_processor(EmissaryClanRightsProcessor())


@resource('#emissary', name='show')
def show(context):

    if context.current_emissary is None:
        raise utils_views.ViewError(code='emissaries.not_found',
                                    message='Эмиссар не найден.')

    clan_events = None

    if context.clan:
        number = conf.settings.CLAN_CHRONICLE_RECORDS_ON_EMISSARY_PAGE
        total_events, clan_events = clans_tt_services.chronicle.cmd_get_last_events(clan=context.clan,
                                                                                    tags=(context.current_emissary.meta_object().tag,),
                                                                                    number=number)

        tt_api_events_log.fill_events_wtih_meta_objects(clan_events)

    total_events, game_events = chronicle_tt_services.chronicle.cmd_get_last_events(tags=(context.current_emissary.meta_object().tag,),
                                                                            number=conf.settings.GAME_CHRONICLE_RECORDS_ON_EMISSARY_PAGE)

    tt_api_events_log.fill_events_wtih_meta_objects(game_events)

    emissary_power = politic_power_logic.get_emissaries_power([context.current_emissary.id])[context.current_emissary.id]

    active_emissary_events_types = [event.concrete_event.TYPE for event in context.current_emissary.active_events()]

    all_emissary_events = [events.TYPES[event] for event in sorted(relations.EVENT_TYPE.records, key=lambda e: e.text)]

    return utils_views.Page('emissaries/show.html',
                            content={'resource': context.resource,
                                     'emissary': context.current_emissary,
                                     'clan_events': clan_events,
                                     'game_events': game_events,
                                     'clan': clans_logic.load_clan(clan_id=context.current_emissary.clan_id),
                                     'emissary_clan_rights': context.emissary_clan_rights,
                                     'emissary_power': emissary_power,
                                     'active_emissary_events_types': active_emissary_events_types,
                                     'all_emissary_events': all_emissary_events})


def check_clan_restrictions(clan_id):
    clan_attributes = clans_logic.load_attributes(clan_id)

    if clan_attributes.fighters_maximum < clans_logic.get_combat_personnel(clan_id):
        raise utils_views.ViewError(code='emissaries.maximum_fighters',
                                    message='Боевой состав вашей гильдии превышает максимально допустимый.')

    if not logic.has_clan_space_for_emissary(clan_id, clan_attributes):
        raise utils_views.ViewError(code='emissaries.maximum_emissaries',
                                    message='Ваша гильдия уже наняла максимально возможное количество эмиссаров.')


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanGameProcessor()
@clans_views.ClanStaticOperationAccessProcessor(permissions_attribute='clan_rights', permission='can_emissaries_relocation')
@resource('create-dialog')
def create_dialog(context):

    check_clan_restrictions(context.clan.id)

    return utils_views.Page('emissaries/create_dialog.html',
                            content={'clan': context.clan,
                                     'form': forms.EmissaryForm(),
                                     'tt_clans_constants': tt_clans_constants,
                                     'resource': context.resource})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanGameProcessor()
@clans_views.ClanStaticOperationAccessProcessor(permissions_attribute='clan_rights', permission='can_emissaries_relocation')
@utils_views.FormProcessor(form_class=forms.EmissaryForm)
@resource('create', method='POST')
def create(context):

    with django_transaction.atomic():
        clans_logic.lock_clan_for_update(context.clan.id)

        check_clan_restrictions(context.clan.id)

        with clans_views.points_banker(account_id=context.clan.id,
                                       type='create_emissary',
                                       amount=-tt_clans_constants.PRICE_CREATE_EMISSARY):
            emissary = logic.create_emissary(initiator=context.account,
                                             clan=context.clan,
                                             place_id=context.form.c.place,
                                             gender=context.form.c.gender,
                                             race=context.form.c.race,
                                             utg_name=game_names.generator().get_name(context.form.c.race,
                                                                                      context.form.c.gender))

        return utils_views.AjaxOk(content={'next_url': utils_urls.url('game:emissaries:show', emissary.id)})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanGameProcessor()
@EventTypeProcessor(get_name='event_type')
@EventPermissionProcessor()
@resource('#emissary', 'start-event-dialog')
def start_event_dialog(context):

    if context.event_type is None:
        raise utils_views.ViewError(code='common.argument_required', message='Не указан тип мероприятия')

    event_class = events.TYPES[context.event_type]

    max_power_to_spend = event_class.power_cost(context.current_emissary, days=event_class.max_event_length())

    current_power = politic_power_logic.get_emissaries_power(emissaries_ids=[context.current_emissary.id])[context.current_emissary.id]

    show_power_warning = (current_power <= max_power_to_spend + conf.settings.SHOW_START_EVENT_WARNING_BARRIER)

    return utils_views.Page('emissaries/start_event_dialog.html',
                            content={'emissary': context.current_emissary,
                                     'form': event_class.form(emissary=context.current_emissary),
                                     'event_class': event_class,
                                     'resource': context.resource,
                                     'current_power': current_power,
                                     'show_power_warning': show_power_warning})


def _check_emissaries_events(emissary, event_class):

    if emissary.attrs.maximum_simultaneously_events <= len(emissary.active_events()):
        raise utils_views.ViewError(code='emissaies.maximum_simultaneously_events',
                                    message='У эмиссара слишком много активных мероприятий. Дождитесь их завершения или отмените одно.')

    if event_class.TYPE in {event.concrete_event.TYPE for event in emissary.active_events()}:
        raise utils_views.ViewError(code='emissaies.dublicate_event',
                                    message='Нельзя запустить два мероприятия одного типа.')

    if not event_class.is_available(emissary=emissary, active_events={event.concrete_event.TYPE for event in emissary.active_events()}):
        raise utils_views.ViewError(code='emissaries.event_not_available', message='Нельзя начать это мероприятие.')


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanGameProcessor()
@EventTypeProcessor(get_name='event_type')
@EventPermissionProcessor()
@resource('#emissary', 'start-event', method='POST')
def start_event(context):

    emissary = context.current_emissary

    event_class = events.TYPES[context.event_type]

    form = event_class.form(emissary=emissary,
                            post=context.django_request.POST)

    if not form.is_valid():
        raise utils_views.ViewError(code='form_errors', message=form.errors)

    with django_transaction.atomic():

        if not logic.lock_emissary_for_update(emissary.id):
            raise utils_views.ViewError(code='emissaies.no_emissary_found', message='Активный эмиссар не найден')

        _check_emissaries_events(emissary, event_class)

        with clans_views.points_banker(account_id=context.clan.id,
                                       type='start_event',
                                       amount=-event_class.action_points_cost(emissary)):

            current_power = politic_power_logic.get_emissaries_power(emissaries_ids=[emissary.id])[emissary.id]

            days = form.c.period

            required_power = event_class.power_cost(emissary, days)

            if current_power < required_power:
                raise utils_views.ViewError(code='emissaies.no_enough_power', message='У эмиссара недостаточно влияния')

            concrete_event = event_class.construct_by_form(emissary, form)

            try:
                with concrete_event.on_create(context.current_emissary):
                    event = logic.create_event(initiator=context.account,
                                               emissary=context.current_emissary,
                                               concrete_event=concrete_event,
                                               days=days)

                concrete_event.after_create(event)

                logic.save_event(event)

            except exceptions.OnEventCreateError:
                raise utils_views.ViewError(code='emissaries.on_create_error',
                                            message='Не выполнено одно из специфичных для мероприятия условий')

            # влияние отнимаем после успешног осоздания мероприятия
            # так как при его создании могут возникунть ошибки, которые не должны влиять на списание влияния
            # поскольку списание влияния не транзакционное и при ошибке оно не вернётся.
            impact = game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                  actor_type=tt_api_impacts.OBJECT_TYPE.ACCOUNT,
                                                  actor_id=context.account.id,
                                                  target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                  target_id=emissary.id,
                                                  amount=-required_power)

            politic_power_logic.add_power_impacts([impact])

    return utils_views.AjaxOk(content={'next_url': utils_urls.url('game:emissaries:show', emissary.id)})


@accounts_views.LoginRequiredProcessor()
@accounts_views.BanGameProcessor()
@EventIdProcessor(get_name='event')
@EventPermissionProcessor()
@resource('#emissary', 'stop-event', method='POST')
def stop_event(context):

    event = storage.events.get_or_load(context.current_event_id)

    emissary = context.current_emissary

    if event.state.is_STOPPED:
        return utils_views.AjaxOk(content={'next_url': utils_urls.url('game:emissaries:show', emissary.id)})

    if event.emissary_id != emissary.id:
        raise utils_views.ViewError(code='emissaries.wrong_emissary', message='Эмиссар не проводит это мероприятие')

    logic.cancel_event(initiator=context.account, event=event)

    return utils_views.AjaxOk(content={'next_url': utils_urls.url('game:emissaries:show', emissary.id)})
