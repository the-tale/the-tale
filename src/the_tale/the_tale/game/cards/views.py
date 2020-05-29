
import smart_imports

smart_imports.all()


########################################
# processors definition
########################################

class AccountCardsLoader(utils_views.BaseViewProcessor):
    def preprocess(self, context):
        context.account_cards = tt_services.storage.cmd_get_items(context.account.id)


class AccountCardProcessor(utils_views.ArgumentProcessor):
    ERROR_MESSAGE = 'У Вас нет такой карты'
    GET_NAME = 'card'
    CONTEXT_NAME = 'account_card'

    def parse(self, context, raw_value):
        try:
            card_uid = uuid.UUID(raw_value)
        except ValueError:
            self.raise_wrong_format()

        if card_uid not in context.account_cards:
            self.raise_wrong_value()

        return context.account_cards[card_uid]


class AccountCardsProcessor(utils_views.ArgumentProcessor):
    ERROR_MESSAGE = 'У вас нет как минимум одной из указанных карт'
    POST_NAME = 'card'
    CONTEXT_NAME = 'cards'
    IN_LIST = True

    def parse(self, context, raw_value):
        try:
            cards_uids = [uuid.UUID(card_id.strip()) for card_id in raw_value]
        except ValueError:
            self.raise_wrong_format()

        for card_uid in cards_uids:
            if card_uid not in context.account_cards:
                self.raise_wrong_value()

        return [context.account_cards[card_uid] for card_uid in cards_uids]


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='cards')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(heroes_views.CurrentHeroProcessor())

guide_resource = utils_views.Resource(name='cards')
guide_resource.add_processor(accounts_views.CurrentAccountProcessor())
guide_resource.add_processor(utils_views.FakeResourceProcessor())

technical_resource = utils_views.Resource(name='cards')

########################################
# filters
########################################


class INDEX_ORDER(rels_django.DjangoEnum):
    records = (('RARITY', 0, 'по редкости'),
               ('NAME', 1, 'по имени'))


CARDS_FILTER = [utils_list_filter.reset_element(),
                utils_list_filter.choice_element('редкость:', attribute='rarity', choices=[(None, 'все')] + list(relations.RARITY.select('value', 'text'))),
                utils_list_filter.choice_element('доступность:', attribute='availability', choices=[(None, 'все')] + list(relations.AVAILABILITY.select('value', 'text'))),
                utils_list_filter.choice_element('сортировка:',
                                                 attribute='order_by',
                                                 choices=list(INDEX_ORDER.select('value', 'text')),
                                                 default_value=INDEX_ORDER.RARITY.value)]


class CardsFilter(utils_list_filter.ListFilter):
    ELEMENTS = CARDS_FILTER

########################################
# views
########################################


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@AccountCardProcessor()
@resource('use-dialog')
def use_dialog(context):

    favorite_items = {slot: context.account_hero.equipment.get(slot)
                      for slot in heroes_relations.EQUIPMENT_SLOT.records
                      if context.account_hero.equipment.get(slot) is not None}

    return utils_views.Page('cards/use_dialog.html',
                            content={'hero': context.account_hero,
                                     'card': context.account_card,
                                     'form': context.account_card.get_form(hero=context.account_hero),
                                     'dialog_info': context.account_card.get_dialog_info(hero=context.account_hero),
                                     'resource': context.resource,
                                     'EQUIPMENT_SLOT': heroes_relations.EQUIPMENT_SLOT,
                                     'RISK_LEVEL': heroes_relations.RISK_LEVEL,
                                     'COMPANION_DEDICATION': heroes_relations.COMPANION_DEDICATION,
                                     'COMPANION_EMPATHY': heroes_relations.COMPANION_EMPATHY,
                                     'ENERGY_REGENERATION': heroes_relations.ENERGY_REGENERATION,
                                     'ARCHETYPE': game_relations.ARCHETYPE,
                                     'favorite_items': favorite_items})


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@AccountCardProcessor()
@utils_api.Processor(versions=(conf.settings.USE_API_VERSION, ))
@resource('api', 'use', name='api-use', method='POST')
def api_use(context):
    form = context.account_card.get_form(data=context.django_request.POST, hero=context.account_hero)

    if not form.is_valid():
        raise utils_views.ViewError(code='form_errors', message=form.errors)

    task = context.account_card.activate(context.account_hero, data=form.get_card_data())

    return utils_views.AjaxProcessing(task.status_url)


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@utils_api.Processor(versions=(conf.settings.RECEIVE_API_VERSION,))
@resource('api', 'receive', name='api-receive-cards', method='post')
def api_receive(context):
    new_cards = [card for card in context.account_cards.values() if card.storage.is_NEW]

    logic.change_storage(owner_id=context.account.id,
                         operation_type='activate-new-cards',
                         cards=new_cards,
                         old_storage=relations.STORAGE.NEW,
                         new_storage=relations.STORAGE.FAST)

    return utils_views.AjaxOk(content={'cards': [card.ui_info() for card in new_cards]})


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@AccountCardsProcessor()
@utils_api.Processor(versions=(conf.settings.COMBINE_API_VERSION, '2.0'))
@resource('api', 'combine', name='api-combine', method='post')
def api_combine(context):
    new_cards, result = logic.get_combined_cards(allow_premium_cards=context.account.cards_receive_mode().is_ALL,
                                                 combined_cards=context.cards)

    if not result.is_SUCCESS:
        raise utils_views.ViewError(code='wrong_cards', message=result.text)

    try:
        logic.change_cards(owner_id=context.account.id,
                           operation_type='combine-cards',
                           to_add=new_cards,
                           to_remove=context.cards)
    except tt_api_exceptions.TTAPIUnexpectedAPIStatus:
        # return error, in most cases it is duplicate request
        raise utils_views.ViewError(code='can_not_combine_cards',
                                    message='Не удалось объединить карты. Попробуйте обновить страницу и повторить попытку.')

    ##################################
    # change combined cards statistics
    logic_task = heroes_postponed_tasks.InvokeHeroMethodTask(hero_id=context.account.id,
                                                             method_name='new_cards_combined',
                                                             method_kwargs={'number': 1})
    task = PostponedTaskPrototype.create(logic_task)
    amqp_environment.environment.workers.supervisor.cmd_logic_task(account_id=context.account.id, task_id=task.id)
    ##################################

    MESSAGE = '''
<p>Вы получаете новые карты:

<ul>{cards_list}</ul>
'''

    card_template = '<li><span class="{rarity}-card-label">{name}</span><br/><br/><blockquote>{description}</blockquote></p></li>'

    cards_list = [card_template.format(rarity=card.type.rarity.name.lower(),
                                       name=card.name[0].upper() + card.name[1:],
                                       description=card.effect.DESCRIPTION)
                  for card in new_cards]

    message = MESSAGE.format(cards_list=''.join(cards_list))

    if context.api_version == '2.0':
        return utils_views.AjaxOk(content={'message': message,
                                           'card': new_cards[0].ui_info()})

    return utils_views.AjaxOk(content={'message': message,
                                       'cards': [card.ui_info() for card in new_cards]})


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@utils_api.Processor(versions=(conf.settings.GET_CARDS_API_VERSION, ))
@resource('api', 'get-cards', name='api-get-cards', method='get')
def api_get_cards(context):

    timers = accounts_tt_services.players_timers.cmd_get_owner_timers(context.account.id)

    if not timers and (django_settings.RUNSERVER_RUNNING or django_settings.TESTS_RUNNING):
        accounts_logic.create_cards_timer(account_id=context.account.id)
        timers = accounts_tt_services.players_timers.cmd_get_owner_timers(context.account.id)

    for timer in timers:
        if timer.type.is_CARDS_MINER:
            new_card_timer = timer
            break

    return utils_views.AjaxOk(content={'cards': [card.ui_info()
                                                 for card in context.account_cards.values()
                                                 if not card.storage.is_NEW],
                                       'new_cards': sum(1 for card in context.account_cards.values() if card.storage.is_NEW),
                                       'new_card_timer': new_card_timer.ui_info()})


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@AccountCardsProcessor()
@utils_api.Processor(versions=(conf.settings.MOVE_TO_STORAGE_API_VERSION, ))
@resource('api', 'move-to-storage', name='api-move-to-storage', method='post')
def api_move_to_storage(context):
    logic.change_storage(owner_id=context.account.id,
                         operation_type='move-to-storage',
                         cards=context.cards,
                         old_storage=relations.STORAGE.FAST,
                         new_storage=relations.STORAGE.ARCHIVE)

    return utils_views.AjaxOk()


@accounts_views.LoginRequiredProcessor()
@AccountCardsLoader()
@AccountCardsProcessor()
@utils_api.Processor(versions=(conf.settings.MOVE_TO_HAND_API_VERSION, ))
@resource('api', 'move-to-hand', name='api-move-to-hand', method='post')
def api_move_to_hand(context):
    logic.change_storage(owner_id=context.account.id,
                         operation_type='move-to-storage',
                         cards=context.cards,
                         old_storage=relations.STORAGE.ARCHIVE,
                         new_storage=relations.STORAGE.FAST)

    return utils_views.AjaxOk()


@utils_views.RelationArgumentProcessor(relation=relations.RARITY, default_value=None,
                                       error_message='неверный тип редкости карты',
                                       context_name='cards_rarity', get_name='rarity')
@utils_views.RelationArgumentProcessor(relation=relations.AVAILABILITY, default_value=None,
                                       error_message='неверный тип доступности карты',
                                       context_name='cards_availability', get_name='availability')
@utils_views.RelationArgumentProcessor(relation=INDEX_ORDER, default_value=INDEX_ORDER.RARITY,
                                       error_message='неверный тип сортировки карт',
                                       context_name='cards_order_by', get_name='order_by')
@guide_resource('')
def index(context):
    all_cards = types.CARD.records

    if context.cards_availability:
        all_cards = [card for card in all_cards if card.availability == context.cards_availability]

    if context.cards_rarity:
        all_cards = [card for card in all_cards if card.rarity == context.cards_rarity]

    if context.cards_order_by.is_RARITY:
        all_cards = sorted(all_cards, key=lambda c: (c.rarity.value, c.text))
    elif context.cards_order_by.is_NAME:
        all_cards = sorted(all_cards, key=lambda c: (c.text, c.rarity.value))

    url_builder = utils_urls.UrlBuilder(utils_urls.url('guide:cards:'), arguments={'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                                                   'availability': context.cards_availability.value if context.cards_availability else None,
                                                                                   'order_by': context.cards_order_by.value})

    index_filter = CardsFilter(url_builder=url_builder, values={'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                                'availability': context.cards_availability.value if context.cards_availability else None,
                                                                'order_by': context.cards_order_by.value if context.cards_order_by else None})
    return utils_views.Page('cards/index.html',
                            content={'section': 'cards',
                                     'CARDS': all_cards,
                                     'index_filter': index_filter,
                                     'CARD_RARITY': relations.RARITY,
                                     'resource': context.resource})


@tt_api_views.RequestProcessor(request_class=tt_protocol_timers_pb2.CallbackBody)
@tt_api_views.SecretProcessor(secret=django_settings.TT_SECRET)
@technical_resource('tt', 'take-card-callback', name='tt-take-card-callback', method='post')
@django_decorators.csrf.csrf_exempt
def take_card_callback(context):

    account = accounts_prototypes.AccountPrototype.get_by_id(context.tt_request.timer.owner_id)

    if account is None or account.is_removed():
        postprocess_type = tt_protocol_timers_pb2.CallbackAnswer.PostprocessType.Value('REMOVE')
        return tt_api_views.ProtobufOk(content=tt_protocol_timers_pb2.CallbackAnswer(postprocess_type=postprocess_type))

    if tt_logic_checkers.is_player_participate_in_game(is_banned=account.is_ban_game,
                                                       active_end_at=account.active_end_at,
                                                       is_premium=account.is_premium):

        logic.give_new_cards(account_id=account.id,
                             operation_type='give-card',
                             allow_premium_cards=account.cards_receive_mode().is_ALL,
                             available_for_auction=account.is_premium)

    if accounts_logic.cards_timer_speed(account) != context.tt_request.timer.speed:
        accounts_logic.update_cards_timer(account=account)

    postprocess_type = tt_protocol_timers_pb2.CallbackAnswer.PostprocessType.Value('RESTART')
    return tt_api_views.ProtobufOk(content=tt_protocol_timers_pb2.CallbackAnswer(postprocess_type=postprocess_type))


@accounts_views.LoginRequiredProcessor()
@accounts_views.PremiumAccountProcessor(error_message='Изменить тип получаемых карт могут только подписчики.')
@utils_views.RelationArgumentProcessor(relation=relations.RECEIVE_MODE,
                                       error_message='неверный тип получения карт',
                                       context_name='receive_mode',
                                       get_name='mode')
@utils_api.Processor(versions=(conf.settings.CHANGE_RECEIVE_MODE_API_VERSION, ))
@resource('api', 'change-receive-mode', name='api-change-receive-mode', method='POST')
def api_change_receive_mode(context):
    context.account.set_cards_receive_mode(context.receive_mode)
    context.account.save()
    return utils_views.AjaxOk()
