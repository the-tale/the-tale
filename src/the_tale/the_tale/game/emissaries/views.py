
import smart_imports

smart_imports.all()


########################################
# processors
########################################

class EmissaryProcessor(dext_views.ArgumentProcessor):
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


class EmissaryInGameProcessor(dext_views.BaseViewProcessor):
    ARG_EMISSARY_ATTRIBUTE = dext_views.ProcessorArgument(default='current_emissary')

    def preprocess(self, context):
        if getattr(context, self.emissary_attribute).state.is_IN_GAME:
            return

        raise dext_views.ViewError(code='emissary.emissary_is_not_in_game',
                                   message='Эмиссар уже не участвует в игре (убит или уволен)')


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='emissaries')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(clans_views.AccountClanProcessor(account_attribute='account', clan_attribute='clan'))
resource.add_processor(clans_views.ClanRightsProcessor(clan_attribute='clan'))
resource.add_processor(EmissaryProcessor(url_name='emissary'))


@resource('#emissary', name='show')
def show(context):

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

    return dext_views.Page('emissaries/show.html',
                           content={'resource': context.resource,
                                    'emissary': context.current_emissary,
                                    'clan_events': clan_events,
                                    'game_events': game_events,
                                    'clan': clans_logic.load_clan(clan_id=context.current_emissary.clan_id),
                                    'clan_rights': context.clan_rights,
                                    'emissary_power': emissary_power})


@accounts_views.LoginRequiredProcessor()
@clans_views.ClanStaticOperationAccessProcessor(permissions_attribute='clan_rights', permission='can_emissaries_relocation')
@resource('create-dialog')
def create_dialog(context):
    return dext_views.Page('emissaries/create_dialog.html',
                           content={'clan': context.clan,
                                    'form': forms.EmissaryForm(),
                                    'resource': context.resource})


@accounts_views.LoginRequiredProcessor()
@clans_views.ClanStaticOperationAccessProcessor(permissions_attribute='clan_rights', permission='can_emissaries_relocation')
@dext_views.FormProcessor(form_class=forms.EmissaryForm)
@resource('create', method='POST')
def create(context):

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

    return dext_views.AjaxOk(content={'next_url': dext_urls.url('game:emissaries:show', emissary.id)})
