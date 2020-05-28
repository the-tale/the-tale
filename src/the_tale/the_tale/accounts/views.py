
import smart_imports

smart_imports.all()


###############################
# new view processors
###############################


# TODO: rename to UserAccountProcessor
class CurrentAccountProcessor(utils_views.BaseViewProcessor):
    def preprocess(self, context):
        if context.django_request.user.is_authenticated:
            context.account = prototypes.AccountPrototype(model=context.django_request.user)
        else:
            context.account = context.django_request.user

        if context.account.is_authenticated and context.account.is_update_active_state_needed:
            context.account.update_active_state()

            logic.store_client_ip(context.account.id, context.django_request.META['HTTP_X_FORWARDED_FOR'])


class SuperuserProcessor(utils_views.BaseViewProcessor):
    def preprocess(self, context):
        context.django_superuser = context.account.is_superuser

        if not context.django_superuser:
            raise utils_views.ViewError(code='common.superuser_required', message='У Вас нет прав для проведения данной операции')


class AccountProcessor(utils_views.ArgumentProcessor):
    ERROR_MESSAGE = 'аккаунт не найден'

    def parse(self, context, raw_value):
        try:
            account_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        account = prototypes.AccountPrototype.get_by_id(account_id)

        if account is None:
            self.raise_wrong_value()

        return account


class LoginRequiredProcessor(utils_views.BaseViewProcessor):
    ARG_ERROR_MESSAGE = utils_views.ProcessorArgument(default='У Вас нет прав для проведения данной операции')

    def login_page_url(self, target_url):
        return logic.login_page_url(target_url)

    def preprocess(self, context):
        if context.account.is_authenticated:
            return

        if context.django_request.is_ajax():
            raise utils_views.ViewError(code='common.login_required', message=self.error_message)

        return utils_views.Redirect(target_url=self.login_page_url(context.django_request.get_full_path()))


class FullAccountProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.fast_account'
    ERROR_MESSAGE = 'Вы не закончили регистрацию, данная функция вам недоступна'
    ARGUMENT = 'account'

    def validate(self, argument):
        return not argument.is_fast


class PremiumAccountProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.premium_account'
    ERROR_MESSAGE = 'Эта функциональность доступна только подписчикам'
    ARGUMENT = 'account'

    def validate(self, argument):
        return argument.is_premium


class BanGameProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_game'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument):
        return not argument.is_ban_game


class BanForumProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_forum'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument):
        return not argument.is_ban_forum


class BanAnyProcessor(utils_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_any'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument):
        return not argument.is_ban_any


class ModerateAccountProcessor(utils_views.PermissionProcessor):
    PERMISSION = 'accounts.moderate_account'
    CONTEXT_NAME = 'can_moderate_accounts'


class ModerateAccessProcessor(utils_views.AccessProcessor):
    ERROR_CODE = 'accounts.no_moderation_rights'
    ERROR_MESSAGE = 'Вы не являетесь модератором'

    def check(self, context):
        return context.can_moderate_accounts


class NextUrlProcessor(utils_views.ArgumentProcessor):
    CONTEXT_NAME = 'next_url'
    GET_NAME = 'next_url'
    DEFAULT_VALUE = '/'


########################################
# resource and global processors
########################################
resource = utils_views.Resource(name='')
resource.add_processor(CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

###############################
# new views
###############################

accounts_resource = utils_views.Resource(name='accounts')
accounts_resource.add_processor(AccountProcessor(error_message='Аккаунт не найден',
                                                 url_name='account',
                                                 context_name='master_account',
                                                 default_value=None))
accounts_resource.add_processor(ModerateAccountProcessor())
resource.add_child(accounts_resource)

registration_resource = utils_views.Resource(name='registration')
resource.add_child(registration_resource)

auth_resource = utils_views.Resource(name='auth')
resource.add_child(auth_resource)

profile_resource = utils_views.Resource(name='profile')
profile_resource.add_processor(third_party_views.RefuseThirdPartyProcessor())
resource.add_child(profile_resource)

technical_resource = utils_views.Resource(name='profile')


@utils_views.TextFilterProcessor(context_name='prefix', get_name='prefix', default_value=None)
@utils_views.PageNumberProcessor()
@accounts_resource('')
def index(context):

    accounts_query = prototypes.AccountPrototype.live_query()

    if context.prefix:
        accounts_query = accounts_query.filter(nick__istartswith=context.prefix)

    accounts_count = accounts_query.count()

    url_builder = utils_urls.UrlBuilder(django_reverse('accounts:'), arguments={'page': context.page,
                                                                               'prefix': context.prefix})

    paginator = utils_pagination.Paginator(context.page, accounts_count, conf.settings.ACCOUNTS_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return utils_views.Redirect(paginator.last_page_url, permanent=False)

    account_from, account_to = paginator.page_borders(context.page)

    accounts_models = accounts_query.select_related().order_by('nick')[account_from:account_to]

    accounts = [prototypes.AccountPrototype(model) for model in accounts_models]

    accounts_ids = [model.id for model in accounts_models]
    clans_ids = [model.clan_id for model in accounts_models]

    heroes = dict((model.account_id, heroes_logic.load_hero(hero_model=model)) for model in heroes_models.Hero.objects.filter(account_id__in=accounts_ids))

    clans = {clan.id: clan for clan in clans_logic.load_clans(clans_ids)}

    return utils_views.Page('accounts/index.html',
                            content={'heroes': heroes,
                                     'prefix': context.prefix,
                                     'accounts': accounts,
                                     'clans': clans,
                                     'resource': context.resource,
                                     'current_page_number': context.page,
                                     'paginator': paginator})


@accounts_resource('#account', name='show')
def show(context):
    friendship = friends_prototypes.FriendshipPrototype.get_for_bidirectional(context.account, context.master_account)

    master_hero = heroes_logic.load_hero(account_id=context.master_account.id)

    bills_count = bills_prototypes.BillPrototype.accepted_bills_count(context.master_account.id)

    templates_count = linguistics_prototypes.ContributionPrototype._db_filter(account_id=context.master_account.id,
                                                                              type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE).count()
    words_count = linguistics_prototypes.ContributionPrototype._db_filter(account_id=context.master_account.id,
                                                                          type=linguistics_relations.CONTRIBUTION_TYPE.WORD).count()
    folclor_posts_count = blogs_models.Post.objects.filter(author=context.master_account._model,
                                                           state=blogs_relations.POST_STATE.ACCEPTED).count()

    threads_count = forum_models.Thread.objects.filter(author=context.master_account._model).count()

    threads_with_posts = forum_models.Thread.objects.filter(post__author=context.master_account._model).distinct().count()

    master_clan = None
    master_clan_membership = None
    master_account_membership_request = None

    if context.master_account.clan_id is not None:
        master_clan = clans_logic.load_clan(clan_id=context.master_account.clan_id)
        master_clan_membership = clans_logic.get_membership(context.master_account.id)

    user_clan = None
    user_clan_rights = None

    if context.account.is_authenticated and context.account.clan_id is not None:
        user_clan = clans_logic.load_clan(clan_id=context.account.clan_id)
        user_clan_rights = clans_logic.operations_rights(initiator=context.account,
                                                         clan=user_clan,
                                                         is_moderator=context.account.has_perm('clans.moderate_clan'))

        master_account_membership_request = clans_logic.request_for_clan_and_account(clan_id=user_clan.id,
                                                                                     account_id=context.master_account.id)

    master_account_properties = tt_services.players_properties.cmd_get_all_object_properties(context.master_account.id)

    return utils_views.Page('accounts/show.html',
                            content={'master_hero': master_hero,
                                     'account_meta_object': meta_relations.Account.create_from_object(context.master_account),
                                     'account_info': logic.get_account_info(context.master_account, master_hero),
                                     'master_account': context.master_account,
                                     'accounts_settings': conf.settings,
                                     'RATING_TYPE': ratings_relations.RATING_TYPE,
                                     'resource': context.resource,
                                     'ratings_on_page': ratings_conf.settings.ACCOUNTS_ON_PAGE,
                                     'informer_link': conf.settings.INFORMER_LINK % {'account_id': context.master_account.id},
                                     'friendship': friendship,
                                     'bills_count': bills_count,
                                     'templates_count': templates_count,
                                     'words_count': words_count,
                                     'folclor_posts_count': folclor_posts_count,
                                     'threads_count': threads_count,
                                     'threads_with_posts': threads_with_posts,
                                     'master_clan': master_clan,
                                     'master_clan_membership': master_clan_membership,
                                     'master_account_membership_request': master_account_membership_request,
                                     'user_clan': user_clan,
                                     'user_clan_rights': user_clan_rights,
                                     'master_account_properties': master_account_properties})


@utils_api.Processor(versions=('1.0', ))
@accounts_resource('#account', 'api', 'show', name='api-show')
def api_show(context):
    master_hero = heroes_logic.load_hero(account_id=context.master_account.id)
    return utils_views.AjaxOk(content=logic.get_account_info(context.master_account, master_hero))


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'admin', name='admin')
def admin(context):
    return utils_views.Page('accounts/admin.html',
                            content={'master_account': context.master_account,
                                     'give_award_form': forms.GiveAwardForm(),
                                     'resource': context.resource,
                                     'give_money_form': shop_forms.GMForm(),
                                     'ban_form': forms.BanForm()})


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@utils_views.FormProcessor(form_class=forms.GiveAwardForm)
@accounts_resource('#account', 'give-award', name='give-award', method='post')
def give_award(context):
    prototypes.AwardPrototype.create(description=context.form.c.description,
                                     type=context.form.c.type,
                                     account=context.master_account)

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'reset-nick', name='reset-nick', method='post')
def reset_nick(context):

    logic.change_credentials(account=context.master_account,
                             new_nick=logic.reset_nick_value())

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@utils_views.FormProcessor(form_class=forms.BanForm)
@accounts_resource('#account', 'ban', name='ban', method='post')
def ban(context):

    if context.form.c.ban_type.is_FORUM:
        context.master_account.ban_forum(context.form.c.ban_time.days)
        message = 'Вы лишены права общаться на форуме. Причина: \n\n%(message)s'

    elif context.form.c.ban_type.is_GAME:
        context.master_account.ban_game(context.form.c.ban_time.days)
        message = 'Ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'

    elif context.form.c.ban_type.is_TOTAL:
        context.master_account.ban_forum(context.form.c.ban_time.days)
        context.master_account.ban_game(context.form.c.ban_time.days)
        message = 'Вы лишены права общаться на форуме, ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'

    else:
        raise utils_views.ViewError(code='unknown_ban_type', message='Неизвестный тип бана')

    personal_messages_logic.send_message(sender_id=logic.get_system_user_id(),
                                         recipients_ids=[context.master_account.id],
                                         body=message % {'message': context.form.c.description})

    portal_logic.sync_with_discord(context.master_account)

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'reset-bans', method='post')
def reset_bans(context):

    context.master_account.reset_ban_forum()
    context.master_account.reset_ban_game()

    personal_messages_logic.send_message(sender_id=logic.get_system_user_id(),
                                         recipients_ids=[context.master_account.id],
                                         body='С вас сняли все ограничения, наложенные ранее.')

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@FullAccountProcessor()
@FullAccountProcessor(argument='master_account', error_code='receiver_is_fast', error_message='Нельзя перевести печеньки игроку, не завершившему регистрацию')
@BanAnyProcessor()
@BanAnyProcessor(argument='master_account', error_code='receiver_banned', error_message='Нельзя перевести печеньки забаненому игроку')
@accounts_resource('#account', 'transfer-money-dialog')
def transfer_money_dialog(context):
    if context.account.id == context.master_account.id:
        raise utils_views.ViewError(code='own_account', message='Нельзя переводить печеньки самому себе')

    max_money_to_transfer = logic.max_money_to_transfer(context.account)

    return utils_views.Page('accounts/transfer_money.html',
                            content={'commission': conf.settings.MONEY_SEND_COMMISSION,
                                     'form': forms.SendMoneyForm(),
                                     'max_money_to_transfer': max_money_to_transfer})


@LoginRequiredProcessor()
@FullAccountProcessor()
@FullAccountProcessor(argument='master_account', error_code='receiver_is_fast', error_message='Нельзя перевести печеньки игроку, не завершившему регистрацию')
@BanAnyProcessor()
@BanAnyProcessor(argument='master_account', error_code='receiver_banned', error_message='Нельзя перевести печеньки забаненому игроку')
@utils_views.FormProcessor(form_class=forms.SendMoneyForm)
@accounts_resource('#account', 'transfer-money', method='POST')
def transfer_money(context):

    if context.account.id == context.master_account.id:
        raise utils_views.ViewError(code='own_account', message='Нельзя переводить печеньки самому себе')

    max_money_to_transfer = logic.max_money_to_transfer(context.account)

    if context.form.c.money - logic.get_transfer_commission(context.form.c.money) > max_money_to_transfer:
        raise utils_views.ViewError(code='money_limit', message='Вы достигли лимита перевода печенек')

    if context.form.c.money > context.account.bank_account.amount:
        raise utils_views.ViewError(code='not_enough_money', message='Недостаточно печенек для перевода')

    task = logic.initiate_transfer_money(sender_id=context.account.id,
                                         recipient_id=context.master_account.id,
                                         amount=context.form.c.money,
                                         comment=context.form.c.comment)
    return utils_views.AjaxProcessing(task.status_url)


@registration_resource('create-hero', method='GET')
def create_hero_view(context):

    if context.account.is_authenticated:
        return utils_views.Redirect(target_url=utils_urls.url('game:'))

    return utils_views.Page('accounts/create_hero.html',
                            content={'resource': context.resource,
                                     'create_hero': create_hero})


def hero_story_attributes(view):
    from the_tale.game import views as game_views
    view.add_processor(utils_views.RelationArgumentProcessor(relation=game_relations.GENDER, error_message='Неверно указан пол героя',
                                                            context_name='gender', post_name='gender'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=game_relations.RACE,
                                                            error_message='Неверно указана раса героя',
                                                            context_name='race', post_name='race'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=game_relations.ARCHETYPE,
                                                            error_message='Неверно указана архетип героя',
                                                            context_name='archetype', post_name='archetype'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=game_relations.HABIT_HONOR_INTERVAL,
                                                            error_message='Неверно указана честь героя',
                                                            context_name='honor', post_name='honor'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=game_relations.HABIT_PEACEFULNESS_INTERVAL,
                                                            error_message='Неверно указано миролюбие героя',
                                                            context_name='peacefulness', post_name='peacefulness'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=tt_beings_relations.UPBRINGING,
                                                            error_message='Неверно указано происхождение героя',
                                                            context_name='upbringing', post_name='upbringing'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=tt_beings_relations.FIRST_DEATH,
                                                            error_message='Неверно указана первая смерть героя',
                                                            context_name='first_death', post_name='first_death'))
    view.add_processor(utils_views.RelationArgumentProcessor(relation=tt_beings_relations.AGE,
                                                            error_message='Неверно указан возраст первой смерти героя',
                                                            context_name='age', post_name='age'))
    view.add_processor(game_views.NameProcessor())

    return view


@hero_story_attributes
@utils_api.Processor(versions=('1.0',))
@registration_resource('api', 'register', method='POST', name='api-register')
def register(context):
    from the_tale.game import logic as game_logic

    if context.account.is_authenticated:
        raise utils_views.ViewError(code='accounts.registration.register.already_registered',
                                    message='Вы уже зарегистрированы')

    texts = game_logic.generate_history(name_forms=context.name_forms,
                                        gender=context.gender,
                                        race=context.race,
                                        honor=context.honor,
                                        peacefulness=context.peacefulness,
                                        archetype=context.archetype,
                                        upbringing=context.upbringing,
                                        first_death=context.first_death,
                                        age=context.age)

    referer = context.django_request.session.get(conf.settings.SESSION_REGISTRATION_REFERER_KEY)
    referral_of_id = context.django_request.session.get(conf.settings.SESSION_REGISTRATION_REFERRAL_KEY)
    action_id = context.django_request.session.get(conf.settings.SESSION_REGISTRATION_ACTION_KEY)

    account_nick = uuid.uuid4().hex[:prototypes.AccountPrototype._model_class.MAX_NICK_LENGTH]

    peacefulness_points = c.HABITS_NEW_HERO_POINTS * context.peacefulness.direction
    honor_points = c.HABITS_NEW_HERO_POINTS * context.honor.direction

    hero_attributes = {'name': game_logic.hero_name_from_forms(context.name_forms,
                                                               context.gender).word,
                       'gender': context.gender,
                       'race': context.race,
                       'honor': honor_points,
                       'peacefulness': peacefulness_points,
                       'archetype': context.archetype,
                       'upbringing': context.upbringing,
                       'first_death': context.first_death,
                       'death_age': context.age}

    result, account_id, bundle_id = logic.register_user(nick=account_nick,
                                                        referer=referer,
                                                        referral_of_id=referral_of_id,
                                                        action_id=action_id,
                                                        hero_attributes=hero_attributes)

    if not result.is_OK:
        raise utils_views.ViewError(code='accounts.registration.fast.registration_error',
                                    message=result.text)

    heroes_logic.set_hero_description(account_id, '\n\n'.join('[rl]' + text for text in texts if text).strip())

    amqp_environment.environment.workers.supervisor.cmd_register_new_account(account_id=account_id)

    logic.login_user(context.django_request,
                     nick=prototypes.AccountPrototype.get_by_id(account_id).nick,
                     password=conf.settings.FAST_REGISTRATION_USER_PASSWORD)

    return utils_views.AjaxOk()


@NextUrlProcessor()
@auth_resource('login', name='page-login')
def login_page(context):

    if context.account.is_authenticated:
        return utils_views.Redirect(target_url=context.next_url)

    login_form = forms.LoginForm()

    return utils_views.Page('accounts/login.html',
                            content={'resource': context.resource,
                                     'login_form': login_form,
                                     'next_url': context.next_url})


@NextUrlProcessor()
@utils_views.FormProcessor(form_class=forms.LoginForm)
@utils_api.Processor(versions=('1.0',))
@auth_resource('api', 'login', name='api-login', method='POST')
def api_login(context):

    account = prototypes.AccountPrototype.get_by_email(context.form.c.email)
    if account is None:
        raise utils_views.ViewError(code='accounts.auth.login.wrong_credentials',
                                   message='Неверный логин или пароль')

    if not account.check_password(context.form.c.password):
        raise utils_views.ViewError(code='accounts.auth.login.wrong_credentials',
                                   message='Неверный логин или пароль')

    logic.login_user(context.django_request,
                     nick=account.nick,
                     password=context.form.c.password,
                     remember=context.form.c.remember)

    return utils_views.AjaxOk(content={'next_url': context.next_url,
                                       'account_id': account.id,
                                       'account_name': account.nick_verbose,
                                       'session_expire_at': logic.get_session_expire_at_timestamp(context.django_request)})


@utils_api.Processor(versions=('1.0',))
@auth_resource('api', 'logout', name='api-logout', method=('POST', 'GET'))
def api_logout(context):
    logic.logout_user(context.django_request)

    if context.django_request.method.upper() == 'GET':
        return utils_views.Redirect(target_url='/')

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@profile_resource('', name='show')
def profile(context):
    data = {'email': context.account.email if context.account.email else 'укажите email',
            'nick': context.account.nick if not context.account.is_fast and context.account.nick else 'укажите ваше имя'}

    edit_profile_form = forms.EditProfileForm(data)

    player_properties = tt_services.players_properties.cmd_get_all_object_properties(context.account.id)

    settings_form = forms.SettingsForm({'personal_messages_subscription': context.account.personal_messages_subscription,
                                        'news_subscription': context.account.news_subscription,
                                        'description': context.account.description,
                                        'gender': context.account.gender,
                                        'accept_invites_from_clans': player_properties.accept_invites_from_clans})

    return utils_views.Page('accounts/profile.html',
                            content={'edit_profile_form': edit_profile_form,
                                     'settings_form': settings_form,
                                     'resource': context.resource})


@LoginRequiredProcessor()
@profile_resource('edited', name='edited')
def edit_profile_done(context):
    return utils_views.Page('accounts/profile_edited.html',
                            content={'resource': context.resource})


@LoginRequiredProcessor()
@profile_resource('confirm-email-request')
def confirm_email_request(context):
    return utils_views.Page('accounts/confirm_email_request.html',
                            content={'resource': context.resource})


@LoginRequiredProcessor()
@utils_views.FormProcessor(form_class=forms.EditProfileForm)
@profile_resource('update', name='update', method='POST')
def update_profile(context):

    if context.account.is_fast and not (context.form.c.email and context.form.c.password and context.form.c.nick):
        raise utils_views.ViewError(code='accounts.profile.update.empty_fields',
                                    message='Необходимо заполнить все поля')

    if context.form.c.email:
        existed_account = prototypes.AccountPrototype.get_by_email(context.form.c.email)
        if existed_account and existed_account.id != context.account.id:
            raise utils_views.ViewError(code='accounts.profile.update.used_email',
                                        message={'email': ['На этот адрес уже зарегистрирован аккаунт']})

    if context.form.c.nick:
        existed_account = prototypes.AccountPrototype.get_by_nick(context.form.c.nick)
        if existed_account and existed_account.id != context.account.id:
            raise utils_views.ViewError(code='accounts.profile.update.used_nick',
                                        message={'nick': ['Это имя уже занято']})

    if context.form.c.nick != context.account.nick and context.account.is_ban_any:
        raise utils_views.ViewError(code='accounts.profile.update.banned',
                                    message={'nick': ['Вы не можете менять ник пока забанены']})

    task = prototypes.ChangeCredentialsTaskPrototype.create(account=context.account,
                                                            new_email=context.form.c.email,
                                                            new_password=context.form.c.password,
                                                            new_nick=context.form.c.nick)

    result, error_code, error_message = task.process()

    if result.is_PROCESSED:
        # force login independent from current login status to prevent session corruption on password changing
        # for details see https://docs.djangoproject.com/en/2.1/topics/auth/default/#session-invalidation-on-password-change
        logic.force_login_user(context.django_request, task.account._model)

        return utils_views.AjaxOk(content={'next_url': utils_urls.url('accounts:profile:edited')})

    if result.is_EMAIL_SENT:
        return utils_views.AjaxOk(content={'next_url': utils_urls.url('accounts:profile:confirm-email-request')})

    raise utils_views.ViewError(code='accounts.profile.update.' + error_code,
                                message=error_message)


@utils_views.ArgumentProcessor(context_name='uuid', get_name='uuid', default_value=None)
@profile_resource('confirm-email')
def confirm_email(context):  # pylint: disable=W0621

    if context.uuid is None:
        raise utils_views.ViewError(code='accounts.profile.confirm_email.no_uid',
                                   message='Вы неверно скопировали url. Пожалуйста, внимательно прочтите письмо ещё раз.')

    task = prototypes.ChangeCredentialsTaskPrototype.get_by_uuid(context.uuid)

    content = {'already_processed': False,
               'timeout': False,
               'error_occured': False,
               'task': None,
               'resource': context.resource}

    if task is None:
        content['wrong_link'] = True
        return utils_views.Page('accounts/confirm_email.html',
                                content=content)

    if task.has_already_processed:
        content['already_processed'] = True
        return utils_views.Page('accounts/confirm_email.html',
                                content=content)

    if context.account.is_authenticated and context.account.id != task.account_id:
        task.on_error(state=relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR,
                      comment='try to access task from other account')
        raise utils_views.ViewError(code='not_your_task',
                                    message='Вы пытаетесь обратиться к данным другого игрока, их изменение отменено')

    result, error_code, error_message = task.process()

    if result.is_PROCESSED:
        # force login independent from current login status to prevent session corruption on password changing
        # for details see https://docs.djangoproject.com/en/2.1/topics/auth/default/#session-invalidation-on-password-change
        logic.force_login_user(context.django_request, task.account._model)

        return utils_views.Redirect(target_url=utils_urls.url('accounts:profile:edited'))

    if task.state == relations.CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT:
        content['timeout'] = True
        return utils_views.Page('accounts/confirm_email.html',
                                content=content)

    content['error_occured'] = True
    return utils_views.Page('accounts/confirm_email.html',
                            content=content)


@LoginRequiredProcessor()
@utils_views.FormProcessor(form_class=forms.SettingsForm)
@profile_resource('update-settings', name='update-settings', method='POST')
def update_settings(context):

    if context.account.is_ban_forum and context.form.c.description != context.account.description:
        raise utils_views.ViewError(code='common.ban_forum',
                                    message='Вы не можете менять описание аккаунта')

    context.account.update_settings(context.form)

    tt_services.players_properties.cmd_set_property(object_id=context.account.id,
                                                    name=tt_services.PLAYER_PROPERTIES.accept_invites_from_clans,
                                                    value=context.form.c.accept_invites_from_clans)

    return utils_views.AjaxOk(content={'next_url': utils_urls.url('accounts:profile:edited')})


@profile_resource('reset-password')
def reset_password_page(context):
    if context.account.is_authenticated:
        return utils_views.Redirect(target_url='/')

    reset_password_form = forms.ResetPasswordForm()

    return utils_views.Page('accounts/reset_password.html',
                            content={'reset_password_form': reset_password_form,
                                     'resource': context.resource})


@profile_resource('reset-password-done')
def reset_password_done(context):
    if context.account.is_authenticated:
        return utils_views.Redirect(target_url='/')

    return utils_views.Page('accounts/reset_password_done.html',
                            content={'resource': context.resource})


@utils_views.ArgumentProcessor(context_name='task_uid', get_name='task', default_value=None)
@profile_resource('reset-password-processed')
def reset_password_processed(context):

    task = prototypes.ResetPasswordTaskPrototype.get_by_uuid(context.task_uid)

    if task is None:
        raise utils_views.ViewError(code='accounts.profile.reset_password_done',
                                    message='Не получилось сбросить пароль, возможно вы используете неверную ссылку')

    if context.account.is_authenticated:
        return utils_views.Redirect(target_url='/')

    if task.is_time_expired:
        raise utils_views.ViewError(code='accounts.profile.reset_password_processed.time_expired',
                                    message='Срок действия ссылки закончился, попробуйте восстановить пароль ещё раз')

    if task.is_processed:
        raise utils_views.ViewError(code='accounts.profile.reset_password_processed.already_processed',
                                    message='Эта ссылка уже была использована для восстановления пароля,'
                                            'одну ссылку можно использовать только один раз')

    password = task.process()

    return utils_views.Page('accounts/reset_password_processed.html',
                           content={'password': password,
                                    'resource': context.resource})


@utils_views.FormProcessor(form_class=forms.ResetPasswordForm)
@profile_resource('do-reset-password', method='POST')
def reset_password(context):

    if context.account.is_authenticated:
        raise utils_views.ViewError(code='accounts.profile.reset_password.already_logined',
                                    message='Вы уже вошли на сайт и можете просто изменить пароль')

    account = prototypes.AccountPrototype.get_by_email(context.form.c.email)

    if account is None:
        raise utils_views.ViewError(code='accounts.profile.reset_password.wrong_email',
                                    message='На указанный email аккаунт не зарегистрирован')

    prototypes.ResetPasswordTaskPrototype.create(account)

    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@profile_resource('update-last-news-reminder-time', method='POST')
def update_last_news_reminder_time(context):
    context.account.update_last_news_remind_time()
    return utils_views.AjaxOk()


@LoginRequiredProcessor()
@profile_resource('data-protection-get-data-dialog')
def data_protection_get_data_dialog(context):

    report_id = tt_services.data_protector.cmd_request_report(ids=data_protection.ids_list(context.account))

    report_url = utils_urls.full_url('https', 'accounts:profile:data-protection-report', report_id.hex)

    return utils_views.Page('accounts/data_protection_dialog.html',
                            content={'resource': context.resource,
                                     'report_url': report_url})


@utils_views.ArgumentProcessor(context_name='mode', get_name='mode', default_value='readable')
@utils_views.UUIDArgumentProcessor(context_name='report_id', url_name='id')
@profile_resource('data-protection-report', '#id', name='data-protection-report')
def data_protection_report(context):
    report = tt_services.data_protector.cmd_get_report(id=context.report_id)

    if report.state == tt_api_data_protector.REPORT_STATE.PROCESSING:
        raise utils_views.ViewError(code='accounts.profile.data_protection_report.report_processing',
                                    message='Отчёт ещё не сформирован. Обновите страницу через несколько минут.')

    if report.state == tt_api_data_protector.REPORT_STATE.NOT_EXISTS:
        raise utils_views.ViewError(code='accounts.profile.data_protection_report.report_not_exists',
                                    message='Отчёт не найден (не запрашивался, уже удалён или вы неверно скопировали ссылку).')

    technical_url = utils_urls.full_url('https', 'accounts:profile:data-protection-report', context.report_id.hex, mode="technical")

    if context.mode == 'technical':
        return utils_views.AjaxOk(content={'report': report.data,
                                           'completed_at': report.completed_at.isoformat(),
                                           'expire_at': report.expire_at.isoformat()})
    else:
        report.postprocess_records(data_protection.postprocess_record)

        return utils_views.Page('accounts/data_protection_report.html',
                                content={'resource': context.resource,
                                         'report': report.data_by_source(),
                                         'technical_url': technical_url,
                                         'completed_at': report.completed_at,
                                         'expire_at': report.expire_at})


@tt_api_views.RequestProcessor(request_class=tt_protocol_data_protector_pb2.PluginReportRequest)
@tt_api_views.SecretProcessor(secret=django_settings.TT_SECRET)
@technical_resource('tt', 'data-protection-collect-data', name='tt-data-protection-collect-data', method='post')
@django_decorators.csrf.csrf_exempt
def data_protection_collect_data(context):

    account_id = int(context.tt_request.account_id)

    if django_settings.DEBUG and not models.Account.objects.filter(id=account_id).exists():
        # in develop environment it is normal behaviour
        # but in productions it MUST be an error
        result = tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS
        return tt_api_views.ProtobufOk(content=tt_protocol_data_protector_pb2.PluginDeletionResponse(result=result))

    report = data_protection.collect_full_data(account_id)

    result = tt_protocol_data_protector_pb2.PluginReportResponse.ResultType.SUCCESS

    return tt_api_views.ProtobufOk(content=tt_protocol_data_protector_pb2.PluginReportResponse(result=result,
                                                                                               data=s11n.to_json(report)))


@LoginRequiredProcessor()
@profile_resource('data-protection-request-deletion', method='POST')
def data_protection_request_deletion(context):
    data_protection.first_step_removing(context.account)
    return utils_views.AjaxOk()


@tt_api_views.RequestProcessor(request_class=tt_protocol_data_protector_pb2.PluginDeletionRequest)
@tt_api_views.SecretProcessor(secret=django_settings.TT_SECRET)
@technical_resource('tt', 'data-protection-delete-data', name='tt-data-protection-delete-data', method='post')
@django_decorators.csrf.csrf_exempt
def data_protection_delete_data(context):
    account_id = int(context.tt_request.account_id)

    if django_settings.DEBUG and not models.Account.objects.filter(id=account_id).exists():
        # in develop environment it is normal behaviour
        # but in productions it MUST be an error
        result = tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS
        return tt_api_views.ProtobufOk(content=tt_protocol_data_protector_pb2.PluginDeletionResponse(result=result))

    if data_protection.remove_data(account_id):
        result = tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.SUCCESS
    else:
        result = tt_protocol_data_protector_pb2.PluginDeletionResponse.ResultType.FAILED

    return tt_api_views.ProtobufOk(content=tt_protocol_data_protector_pb2.PluginDeletionResponse(result=result))


################################################
# old views decorators (for other applications)
################################################

@old_views.validator(code='common.fast_account', message='Вы не закончили регистрацию и данная функция вам не доступна')
def validate_fast_account(self, *args, **kwargs):
    return not self.account.is_fast


@old_views.validator(code='common.ban_forum', message='Вам запрещено проводить эту операцию')
def validate_ban_forum(self, *args, **kwargs):
    return not self.account.is_ban_forum


@old_views.validator(code='common.ban_game', message='Вам запрещено проводить эту операцию')
def validate_ban_game(self, *args, **kwargs):
    return not self.account.is_ban_game


@old_views.validator(code='common.ban_any', message='Вам запрещено проводить эту операцию')
def validate_ban_any(self, *args, **kwargs):
    return not self.account.is_ban_any
