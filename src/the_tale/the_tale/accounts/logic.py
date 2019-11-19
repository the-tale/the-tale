
import smart_imports

smart_imports.all()


def login_url(target_url='/'):
    return dext_urls.url('accounts:auth:api-login', api_version='1.0', api_client=django_settings.API_CLIENT, next_url=target_url.encode('utf-8'))


def login_page_url(target_url='/'):
    return dext_urls.url('accounts:auth:page-login', next_url=target_url.encode('utf-8'))


def logout_url():
    return dext_urls.url('accounts:auth:api-logout', api_version='1.0', api_client=django_settings.API_CLIENT)


def register_url():
    return dext_urls.url('accounts:registration:api-register', api_version='1.0', api_client=django_settings.API_CLIENT)


def get_system_user_id():
    if not django_settings.TESTS_RUNNING and hasattr(get_system_user_id, '_id'):
        return get_system_user_id._id

    account = get_system_user()

    get_system_user_id._id = account.id

    return get_system_user_id._id


def get_system_user():
    account = prototypes.AccountPrototype.get_by_nick(conf.settings.SYSTEM_USER_NICK)

    if account:
        return account

    password = utils_password.generate_password(len_=conf.settings.RESET_PASSWORD_LENGTH)

    register_result, account_id, bundle_id = register_user(conf.settings.SYSTEM_USER_NICK,
                                                           email=django_settings.EMAIL_NOREPLY,
                                                           password=password)

    account = prototypes.AccountPrototype.get_by_id(account_id)
    account._model.active_end_at = datetime.datetime.fromtimestamp(0)
    account.save()

    return account


def cards_for_new_account(account):
    to_add = [cards_types.CARD.CHANGE_HERO_SPENDINGS.effect.create_card(available_for_auction=False,
                                                                        type=cards_types.CARD.CHANGE_HERO_SPENDINGS,
                                                                        item=heroes_relations.ITEMS_OF_EXPENDITURE.BUYING_ARTIFACT),
              cards_types.CARD.HEAL_COMPANION_COMMON.effect.create_card(available_for_auction=False,
                                                                        type=cards_types.CARD.HEAL_COMPANION_COMMON),
              cards_types.CARD.ADD_EXPERIENCE_COMMON.effect.create_card(available_for_auction=False,
                                                                        type=cards_types.CARD.ADD_EXPERIENCE_COMMON),
              cards_types.CARD.CHANGE_ABILITIES_CHOICES.effect.create_card(available_for_auction=False,
                                                                           type=cards_types.CARD.CHANGE_ABILITIES_CHOICES),
              cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                    type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                    preference=heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
              cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                    type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                    preference=heroes_relations.PREFERENCE_TYPE.ENERGY_REGENERATION_TYPE),
              cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                    type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                    preference=heroes_relations.PREFERENCE_TYPE.PLACE),
              cards_types.CARD.CHANGE_PREFERENCE.effect.create_card(available_for_auction=False,
                                                                    type=cards_types.CARD.CHANGE_PREFERENCE,
                                                                    preference=heroes_relations.PREFERENCE_TYPE.FRIEND),
              cards_types.CARD.ADD_BONUS_ENERGY_RARE.effect.create_card(available_for_auction=False,
                                                                        type=cards_types.CARD.ADD_BONUS_ENERGY_RARE)]

    for _ in range(5):
        to_add.append(cards_types.CARD.STOP_IDLENESS.effect.create_card(available_for_auction=False,
                                                                        type=cards_types.CARD.STOP_IDLENESS))

    cards_logic.change_cards(owner_id=account.id,
                             operation_type='new-hero-gift',
                             to_add=to_add)


def register_user(nick,
                  email=None,
                  password=None,
                  referer=None,
                  referral_of_id=None,
                  action_id=None,
                  is_bot=False,
                  gender=game_relations.GENDER.MALE,
                  full_create=True,
                  hero_attributes={}):
    if models.Account.objects.filter(nick=nick).exists():
        return relations.REGISTER_USER_RESULT.DUPLICATE_USERNAME, None, None

    if email and models.Account.objects.filter(email=email).exists():
        return relations.REGISTER_USER_RESULT.DUPLICATE_EMAIL, None, None

    try:
        referral_of = prototypes.AccountPrototype.get_by_id(referral_of_id)
    except ValueError:
        referral_of = None

    if (email and not password) or (not email and password):
        raise exceptions.EmailAndPasswordError()

    is_fast = not (email and password)

    if is_fast and is_bot:
        raise exceptions.BotIsFastError()

    if password is None:
        password = conf.settings.FAST_REGISTRATION_USER_PASSWORD

    account = prototypes.AccountPrototype.create(nick=nick,
                                                 email=email,
                                                 is_fast=is_fast,
                                                 is_bot=is_bot,
                                                 password=password,
                                                 referer=referer,
                                                 referral_of=referral_of,
                                                 action_id=action_id,
                                                 gender=gender)

    achievements_prototypes.AccountAchievementsPrototype.create(account)
    collections_prototypes.AccountItemsPrototype.create(account)

    hero_attributes['is_fast'] = account.is_fast
    hero_attributes['is_bot'] = account.is_bot
    hero_attributes['might'] = account.might
    hero_attributes['active_state_end_at'] = account.active_end_at
    hero_attributes['premium_state_end_at'] = account.premium_end_at
    hero_attributes['ban_state_end_at'] = account.ban_game_end_at

    hero = heroes_logic.create_hero(account_id=account.id, attributes=hero_attributes)

    if full_create:
        game_tt_services.energy.cmd_change_balance(account_id=account.id,
                                                   type='initial_contribution',
                                                   amount=c.INITIAL_ENERGY_AMOUNT,
                                                   async=False,
                                                   autocommit=True)

        create_cards_timer(account.id)

        cards_for_new_account(hero)

    return relations.REGISTER_USER_RESULT.OK, account.id, hero.actions.current_action.bundle_id


def create_cards_timer(account_id):
    tt_services.players_timers.cmd_create_timer(owner_id=account_id,
                                                type=relations.PLAYER_TIMERS_TYPES.CARDS_MINER,
                                                speed=tt_cards_constants.NORMAL_PLAYER_SPEED,
                                                border=tt_cards_constants.RECEIVE_TIME)


def cards_timer_speed(account):
    if account.is_premium:
        return tt_cards_constants.PREMIUM_PLAYER_SPEED

    return tt_cards_constants.NORMAL_PLAYER_SPEED


def update_cards_timer(account):
    tt_services.players_timers.cmd_change_timer_speed(owner_id=account.id,
                                                      speed=cards_timer_speed(account),
                                                      type=relations.PLAYER_TIMERS_TYPES.CARDS_MINER)


def login_user(request, nick=None, password=None, remember=False):
    user = django_auth.authenticate(nick=nick, password=password)

    if request.user.id != user.id:
        request.session.flush()

    django_auth.login(request, user)

    if remember:
        request.session.set_expiry(conf.settings.SESSION_REMEMBER_TIME)


def force_login_user(request, user):

    if request.user.id != user.id:
        request.session.flush()

    user.backend = django_settings.AUTHENTICATION_BACKENDS[0]

    django_auth.login(request, user)


def logout_user(request):
    signals.on_before_logout.send(None, request=request)

    django_auth.logout(request)
    request.session.flush()

    request.session[conf.settings.SESSION_FIRST_TIME_VISIT_VISITED_KEY] = True


def remove_account(account, force=False):
    if force or account.can_be_removed():
        with django_transaction.atomic():
            game_logic.remove_game_data(account)
            account.remove()


def block_expired_accounts(logger):

    expired_before = datetime.datetime.now() - datetime.timedelta(seconds=conf.settings.FAST_ACCOUNT_EXPIRED_TIME)

    accounts_query = models.Account.objects.filter(is_fast=True, created_at__lt=expired_before)

    removed_accounts_number = accounts_query.count()

    logger.info('found %s accounts to remove', removed_accounts_number)

    for i, account_model in enumerate(accounts_query):
        logger.info('process account %s/%s', i, removed_accounts_number)

        if account_model.clan_id is not None:
            logger.error('found fast account with clan, account id: %s', account_model.id)
            continue

        remove_account(prototypes.AccountPrototype(account_model))


def thin_out_accounts(number, prolong_active_to, logger):
    restricted_accounts = set()
    restricted_accounts |= set(models.RandomPremiumRequest.objects.values_list('initiator', flat=True))
    restricted_accounts |= set(models.RandomPremiumRequest.objects.values_list('receiver', flat=True))
    restricted_accounts |= set(models.Account.objects.exclude(clan_id=None).values_list('id', flat=True))
    restricted_accounts |= set(bills_models.Bill.objects.values_list('owner_id', flat=True))
    restricted_accounts |= set(blogs_models.Post.objects.values_list('author_id', flat=True))
    restricted_accounts |= set(blogs_models.Post.objects.values_list('moderator_id', flat=True))
    restricted_accounts |= set(forum_models.Post.objects.values_list('author_id', flat=True))
    restricted_accounts |= set(forum_models.Thread.objects.values_list('author_id', flat=True))

    all_accounts_ids = set(models.Account.objects.values_list('id', flat=True))
    all_accounts_ids -= restricted_accounts

    accounts_to_delete = sorted(all_accounts_ids)[number:]

    logger.info('accounts to delete: %s', len(accounts_to_delete))

    for i, account_model in enumerate(models.Account.objects.filter(id__in=accounts_to_delete)):
        logger.info('process account %s/%s', i, len(accounts_to_delete))
        remove_account(prototypes.AccountPrototype(account_model), force=True)

    models.Account.objects.all().update(active_end_at=datetime.datetime.now() + datetime.timedelta(seconds=prolong_active_to))


# for bank
def get_account_id_by_email(email):
    account = prototypes.AccountPrototype.get_by_email(dext_logic.normalize_email(email))
    return account.id if account else None


def get_session_expire_at_timestamp(request):
    return time.mktime(request.session.get_expiry_date().timetuple())


def is_first_time_visit(request):
    return not request.user.is_authenticated and request.session.get(conf.settings.SESSION_FIRST_TIME_VISIT_KEY)


def get_account_info(account, hero):
    ratings = {}

    rating_places = ratings_prototypes.RatingPlacesPrototype.get_by_account_id(account.id)

    rating_values = ratings_prototypes.RatingValuesPrototype.get_by_account_id(account.id)

    if rating_values and rating_places:
        for rating in ratings_relations.RATING_TYPE.records:
            ratings[rating.value] = {'name': rating.text,
                                     'place': getattr(rating_places, '%s_place' % rating.field, None),
                                     'value': getattr(rating_values, rating.field, None)}

    popularity = places_logic.get_hero_popularity(hero.id)

    places_history = [{'place': {'id': place_id,
                                 'name': places_storage.places[place_id].name},
                       'count': help_count} for place_id, help_count in popularity.places_rating()]

    clan_info = None

    if account.clan_id:
        clan = account.clan
        clan_info = {'id': clan.id,
                     'abbr': clan.abbr,
                     'name': clan.name}

    return {'id': account.id,
            'registered': not account.is_fast,
            'name': account.nick_verbose,
            'hero_id': hero.id,
            'places_history': places_history,
            'might': account.might,
            'achievements': achievements_prototypes.AccountAchievementsPrototype.get_by_account_id(account.id).points,
            'collections': collections_prototypes.AccountItemsPrototype.get_by_account_id(account.id).get_items_count(),
            'referrals': account.referrals_number,
            'ratings': ratings,
            'permissions': {
                'can_affect_game': account.can_affect_game
            },
            'description': account.description_html,
            'clan': clan_info}


def get_transfer_commission(money):
    commission = int(math.floor(money * conf.settings.MONEY_SEND_COMMISSION))

    if commission == 0:
        commission = 1

    return commission


def initiate_transfer_money(sender_id, recipient_id, amount, comment):
    commission = get_transfer_commission(amount)

    task = postponed_tasks.TransferMoneyTask(sender_id=sender_id,
                                             recipient_id=recipient_id,
                                             amount=amount - commission,
                                             commission=commission,
                                             comment=comment)
    task = PostponedTaskPrototype.create(task)

    amqp_environment.environment.workers.refrigerator.cmd_wait_task(task.id)

    return task


def change_credentials(account, new_email=None, new_password=None, new_nick=None):
    if new_password:
        account._model.password = new_password
    if new_email:
        account._model.email = new_email
    if new_nick:
        account.nick = new_nick

    old_fast = account.is_fast  # pylint: disable=E0203

    account.is_fast = False

    account.save()

    if old_fast:
        cards_number = conf.settings.FREE_CARDS_FOR_REGISTRATION

        cards_logic.give_new_cards(account_id=account.id,
                                   operation_type='give-card-for-registration',
                                   allow_premium_cards=False,
                                   available_for_auction=False,
                                   number=cards_number)

        account.cmd_update_hero()

        if account.referral_of_id is not None:
            amqp_environment.environment.workers.accounts_manager.cmd_run_account_method(
                account_id=account.referral_of_id,
                method_name=account.update_referrals_number.__name__,
                data={})
