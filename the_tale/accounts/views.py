# coding: utf-8
import uuid

from django.core.urlresolvers import reverse
from django.utils.log import getLogger

from dext.common.utils import views as dext_views
from dext.common.utils import exceptions as dext_exceptions
from dext.common.utils.urls import UrlBuilder
from dext.views import handler, validator, validate_argument

from the_tale.common.utils import views as utils_views

from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils import api

from the_tale.game.heroes.models import Hero
from the_tale.game.heroes import logic as heroes_logic

from the_tale.accounts.friends.prototypes import FriendshipPrototype
from the_tale.accounts.personal_messages.prototypes import MessagePrototype
from the_tale.accounts.clans.prototypes import ClanPrototype
from the_tale.accounts.third_party import decorators

from .prototypes import AccountPrototype, ChangeCredentialsTaskPrototype, AwardPrototype, ResetPasswordTaskPrototype
from . import postponed_tasks
from . import relations
from . import forms
from . import conf
from . import logic
from . import meta_relations



###############################
# new view processors
###############################

class CurrentAccountProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.account = AccountPrototype(model=context.django_request.user) if context.django_request.user.is_authenticated() else context.django_request.user

        if context.account.is_authenticated() and context.account.is_update_active_state_needed:
            environment.workers.accounts_manager.cmd_run_account_method(account_id=context.account.id,
                                                                        method_name=AccountPrototype.update_active_state.__name__,
                                                                        data={})


class SuperuserProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.django_superuser = context.account.is_superuser

        if not context.django_superuser:
            raise dext_views.ViewError(code='common.superuser_required', message=u'У Вас нет прав для проведения данной операции')


class AccountProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            account_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        account = AccountPrototype.get_by_id(account_id)

        if account is None:
            self.raise_wrong_value()

        return account


class LoginRequiredProcessor(dext_views.BaseViewProcessor):

    def login_page_url(self, target_url):
        return logic.login_page_url(target_url)

    def preprocess(self, context):
        if context.account.is_authenticated():
            return

        if context.django_request.is_ajax():
            raise dext_exceptions.ViewError(code='common.login_required', message=u'У Вас нет прав для проведения данной операции')

        return dext_views.Redirect(target_url=self.login_page_url(context.django_request.get_full_path()))


class FullAccountProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.fast_account'
    ERROR_MESSAGE = u'Вы не закончили регистрацию и данная функция вам не доступна'
    ARGUMENT = 'account'

    def validate(self, argument): return not argument.is_fast


class BanGameProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_game'
    ERROR_MESSAGE = u'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument): return not argument.is_ban_game


class BanForumProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_forum'
    ERROR_MESSAGE = u'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument): return not argument.is_ban_forum


class BanAnyProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'common.ban_any'
    ERROR_MESSAGE = u'Вам запрещено проводить эту операцию'
    ARGUMENT = 'account'

    def validate(self, argument): return not argument.is_ban_any


class ModerateAccountProcessor(dext_views.PermissionProcessor):
    PERMISSION = 'accounts.moderate_account'
    CONTEXT_NAME = 'can_moderate_accounts'

class ModerateAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = u'accounts.no_moderation_rights'
    ERROR_MESSAGE = u'Вы не являетесь модератором'

    def check(self, context):
        return context.can_moderate_accounts


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='')
resource.add_processor(CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())

###############################
# new views
###############################

accounts_resource = dext_views.Resource(name='accounts')
accounts_resource.add_processor(AccountProcessor(error_message=u'Аккаунт не найден', url_name='account', context_name='master_account', default_value=None))
accounts_resource.add_processor(ModerateAccountProcessor())

resource.add_child(accounts_resource)


@utils_views.TextFilterProcessor(context_name='prefix', get_name='prefix', default_value=None)
@utils_views.PageNumberProcessor()
@accounts_resource('')
def index(context):

    accounts_query = AccountPrototype.live_query()

    if context.prefix:
        accounts_query = accounts_query.filter(nick__istartswith=context.prefix)

    accounts_count = accounts_query.count()

    url_builder = UrlBuilder(reverse('accounts:'), arguments={'page': context.page,
                                                              'prefix': context.prefix})

    paginator = Paginator(context.page, accounts_count, conf.accounts_settings.ACCOUNTS_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url, permanent=False)

    account_from, account_to = paginator.page_borders(context.page)

    accounts_models = accounts_query.select_related().order_by('nick')[account_from:account_to]

    accounts = [AccountPrototype(model) for model in accounts_models]

    accounts_ids = [ model.id for model in accounts_models]
    clans_ids = [ model.clan_id for model in accounts_models]

    heroes = dict( (model.account_id, heroes_logic.load_hero(hero_model=model)) for model in Hero.objects.filter(account_id__in=accounts_ids))

    clans = {clan.id:clan for clan in ClanPrototype.get_list_by_id(clans_ids)}

    return dext_views.Page('accounts/index.html',
                           content={'heroes': heroes,
                                    'prefix': context.prefix,
                                    'accounts': accounts,
                                    'clans': clans,
                                    'resource': context.resource,
                                    'current_page_number': context.page,
                                    'paginator': paginator  } )


@accounts_resource('#account', name='show')
def show(context):
    from the_tale.game.ratings import relations as ratings_relations
    from the_tale.game.ratings import conf as ratings_conf

    friendship = FriendshipPrototype.get_for_bidirectional(context.account, context.master_account)

    master_hero = heroes_logic.load_hero(context.master_account.id)

    return dext_views.Page('accounts/show.html',
                           content={'master_hero': master_hero,
                                    'account_meta_object': meta_relations.Account.create_from_object(context.master_account),
                                    'account_info': logic.get_account_info(context.master_account, master_hero),
                                    'master_account': context.master_account,
                                    'accounts_settings': conf.accounts_settings,
                                    'RATING_TYPE': ratings_relations.RATING_TYPE,
                                    'resource': context.resource,
                                    'ratings_on_page': ratings_conf.ratings_settings.ACCOUNTS_ON_PAGE,
                                    'informer_link': conf.accounts_settings.INFORMER_LINK % {'account_id': context.master_account.id},
                                    'friendship': friendship} )

@api.Processor(versions=('1.0', ))
@accounts_resource('#account', 'api', 'show', name='api-show')
def api_show(context):
    u'''
Получить информацию об игроке

- **адрес:** /accounts/&lt;account&gt;/api/show
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**
* URL account — идентификатор игрока
- **возможные ошибки**:
* account.wrong_value — аккаунт с таким идентификатором не найден

формат данных в ответе:

    {
      "id": <целое число>,           // идентификатор игрока
      "registered": true|false,      // маркер завершения регистрации
      "name": "строка",              // имя игрока
      "hero_id": <целое число>,      // идентификатор героя
      "places_history": [            // список истории помощи городам
        "place": {                   // город
          "id": <целое число>,       // идентификатор города
          "name": "строка"           // название города
        },
        "count": <целое число>       // количество фактов помощи
      ],
      "might": <дробное число>,      // могущество
      "achievements": <целое число>, // очки достижений
      "collections": <целое число>,  // количество предметов в коллекции
      "referrals": <целое число>,    // количество последователей (рефералов)
      "ratings": {                                // рейтинги
        "строка": {                               // идентификатор рейтинга:
          "name": "строка",                       // название рейтинга: иинформация о рейтинге
          "place": <целое число>,                 // место
          "value": <целое число>|<дробное число>  // величина рейтингового значения
        }
      },
      "permissions": {                // права на выполнение различных операций
        "can_affect_game": true|false // оказывает ли влияние на игру
      },
      "description": "строка"         // описание игока, введённое им сами (в формате html)
    }
    '''

    master_hero = heroes_logic.load_hero(account_id=context.master_account.id)

    return dext_views.AjaxOk(content=logic.get_account_info(context.master_account, master_hero))


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'admin', name='admin')
def admin(context):
    from the_tale.finances.shop.forms import GMForm
    return dext_views.Page('accounts/admin.html',
                           content={'master_account': context.master_account,
                                    'give_award_form': forms.GiveAwardForm(),
                                    'resource': context.resource,
                                    'give_money_form': GMForm(),
                                    'ban_form': forms.BanForm()} )


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@dext_views.FormProcessor(form_class=forms.GiveAwardForm)
@accounts_resource('#account', 'give-award', name='give-award', method='post')
def give_award(context):
    AwardPrototype.create(description=context.form.c.description,
                          type=context.form.c.type,
                          account=context.master_account)

    return dext_views.AjaxOk()



@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'reset-nick', name='reset-nick', method='post')
def reset_nick(context):
    task = ChangeCredentialsTaskPrototype.create(account=context.master_account,
                                                 new_nick=u'%s (%s)' % (conf.accounts_settings.RESET_NICK_PREFIX, uuid.uuid4().hex))

    postponed_task = task.process(logger)

    return dext_views.AjaxProcessing(postponed_task.status_url)


@LoginRequiredProcessor()
@ModerateAccessProcessor()
@dext_views.FormProcessor(form_class=forms.BanForm)
@accounts_resource('#account', 'ban', name='ban', method='post')
def ban(context):

    if context.form.c.ban_type.is_FORUM:
        context.master_account.ban_forum(context.form.c.ban_time.days)
        message = u'Вы лишены права общаться на форуме. Причина: \n\n%(message)s'
    elif context.form.c.ban_type.is_GAME:
        context.master_account.ban_game(context.form.c.ban_time.days)
        message = u'Ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'
    elif context.form.c.ban_type.is_TOTAL:
        context.master_account.ban_forum(context.form.c.ban_time.days)
        context.master_account.ban_game(context.form.c.ban_time.days)
        message = u'Вы лишены права общаться на форуме, ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'
    else:
        raise dext_views.ViewError(code='unknown_ban_type', message=u'Неизвестный тип бана')

    MessagePrototype.create(logic.get_system_user(),
                            context.master_account,
                            message % {'message': context.form.c.description})

    return dext_views.AjaxOk()

@LoginRequiredProcessor()
@ModerateAccessProcessor()
@accounts_resource('#account', 'reset-bans', method='post')
def reset_bans(context):

    context.master_account.reset_ban_forum()
    context.master_account.reset_ban_game()

    MessagePrototype.create(logic.get_system_user(),
                            context.master_account,
                            u'С вас сняли все ограничения, наложенные ранее.')

    return dext_views.AjaxOk()


@LoginRequiredProcessor()
@FullAccountProcessor()
@FullAccountProcessor(argument='master_account', error_code=u'receiver_is_fast', error_message=u'Нельзя перевести печеньки игроку, не завершившему регистрацию')
@BanAnyProcessor()
@BanAnyProcessor(argument='master_account', error_code=u'receiver_banned', error_message=u'Нельзя перевести печеньки забаненому игроку')
@accounts_resource('#account', 'transfer-money-dialog')
def transfer_money_dialog(context):
    if context.account.id == context.master_account.id:
        raise dext_views.ViewError(code='own_account', message=u'Нельзя переводить печеньки самому себе')

    return dext_views.Page('accounts/transfer_money.html',
                           content={'commission': conf.accounts_settings.MONEY_SEND_COMMISSION,
                                    'form': forms.SendMoneyForm()} )

@LoginRequiredProcessor()
@FullAccountProcessor()
@FullAccountProcessor(argument='master_account', error_code=u'receiver_is_fast', error_message=u'Нельзя перевести печеньки игроку, не завершившему регистрацию')
@BanAnyProcessor()
@BanAnyProcessor(argument='master_account', error_code=u'receiver_banned', error_message=u'Нельзя перевести печеньки забаненому игроку')
@dext_views.FormProcessor(form_class=forms.SendMoneyForm)
@accounts_resource('#account', 'transfer-money', method='POST')
def transfer_money(context):
    if context.account.id == context.master_account.id:
        raise dext_views.ViewError(code='own_account', message=u'Нельзя переводить печеньки самому себе')

    if context.form.c.money > context.account.bank_account.amount:
        raise dext_views.ViewError(code='not_enough_money', message=u'Недостаточно печенек для перевода')

    task = logic.initiate_transfer_money(sender_id=context.account.id,
                                         recipient_id=context.master_account.id,
                                         amount=context.form.c.money,
                                         comment=context.form.c.comment)
    return dext_views.AjaxProcessing(task.status_url)


###############################
# end of new views
###############################

logger = getLogger('django.request')

@validator(code='common.fast_account', message=u'Вы не закончили регистрацию и данная функция вам не доступна')
def validate_fast_account(self, *args, **kwargs): return not self.account.is_fast

@validator(code='common.ban_forum', message=u'Вам запрещено проводить эту операцию')
def validate_ban_forum(self, *args, **kwargs): return not self.account.is_ban_forum

@validator(code='common.ban_game', message=u'Вам запрещено проводить эту операцию')
def validate_ban_game(self, *args, **kwargs): return not self.account.is_ban_game

@validator(code='common.ban_any', message=u'Вам запрещено проводить эту операцию')
def validate_ban_any(self, *args, **kwargs): return not self.account.is_ban_any


class BaseAccountsResource(Resource):

    def initialize(self, *argv, **kwargs):
        super(BaseAccountsResource, self).initialize(*argv, **kwargs)


class RegistrationResource(BaseAccountsResource):

    @handler('fast', method='post')
    def fast(self):

        if self.account.is_authenticated():
            return self.json_error('accounts.registration.fast.already_registered', u'Вы уже зарегистрированы')

        if conf.accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:

            task_id = self.request.session[conf.accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
            task = PostponedTaskPrototype.get_by_id(task_id)

            if task is not None:
                if task.state.is_processed:
                    return self.json_error('accounts.registration.fast.already_processed', u'Вы уже зарегистрированы, обновите страницу')
                if task.state.is_waiting:
                    return self.json_processing(task.status_url)
                # in other case create new task

        referer = None
        if conf.accounts_settings.SESSION_REGISTRATION_REFERER_KEY in self.request.session:
            referer = self.request.session[conf.accounts_settings.SESSION_REGISTRATION_REFERER_KEY]

        referral_of_id = None
        if conf.accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY in self.request.session:
            referral_of_id = self.request.session[conf.accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY]

        action_id = None
        if conf.accounts_settings.SESSION_REGISTRATION_ACTION_KEY in self.request.session:
            action_id = self.request.session[conf.accounts_settings.SESSION_REGISTRATION_ACTION_KEY]

        registration_task = postponed_tasks.RegistrationTask(account_id=None, referer=referer, referral_of_id=referral_of_id, action_id=action_id)

        task = PostponedTaskPrototype.create(registration_task,
                                             live_time=conf.accounts_settings.REGISTRATION_TIMEOUT)

        self.request.session[conf.accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY] = task.id

        environment.workers.registration.cmd_task(task.id)

        return self.json_processing(task.status_url)


class AuthResource(BaseAccountsResource):

    @handler('login', name='page-login', method='get')
    def login_page(self, next_url='/'):
        if self.account.is_authenticated():
            return self.redirect(next_url)

        login_form = forms.LoginForm()
        return self.template('accounts/login.html',
                             {'login_form': login_form,
                              'next_url': next_url} )

    @api.handler(versions=('1.0',))
    @handler('api', 'login', name='api-login', method='post')
    def api_login(self, api_version, next_url='/'):
        u'''
Вход в игру. Используйте этот метод только если разрабатываете приложение для себя и друзей. В остальных случаях пользуйтесь «авторизацией в игре».

- **адрес:** /accounts/auth/api/login
- **http-метод:** POST
- **версии:** 1.0
- **параметры:**
    * GET: next_url — вернётся в ответе метода в случае успешного входа, по умолчанию равен "/"
    * POST: email — email адрес пользователя
    * POST: password — пароль пользователя
    * POST: remember — если флаг указан, сессия игрока будет сохранена на длительное время
- **возможные ошибки**:
    * accounts.auth.login.wrong_credentials — неверный логин или пароль
    * accounts.auth.login.form_errors — ошибка(-и) в заполнении полей

формат данных в ответе:

    {
      "next_url": "относительный url", // адрес, переданный при вызове метода или "/"
      "account_id": <целое число>,     // идентификатор аккаунта
      "account_name": <строка>,        // имя игрока
      "session_expire_at": <timestamp> // время окончания сессии пользователя
    }

При успешном выполнении запроса, будет установлено значение cookie с именем sessionid, которая и является идентификатором сессии пользователя.

В случае, если от имени не вошедшего в игру пользователя будет произведён запрос функционала, доступного только авторизованным пользователям, API вернёт ошибку с кодом "common.login_required" (см. секцию с описанием общих ошибок).
        '''

        login_form = forms.LoginForm(self.request.POST)

        if login_form.is_valid():

            account = AccountPrototype.get_by_email(login_form.c.email)
            if account is None:
                return self.error('accounts.auth.login.wrong_credentials', u'Неверный логин или пароль')

            if not account.check_password(login_form.c.password):
                return self.error('accounts.auth.login.wrong_credentials', u'Неверный логин или пароль')

            logic.login_user(self.request, nick=account.nick, password=login_form.c.password, remember=login_form.c.remember)

            return self.ok(data={'next_url': next_url,
                                 'account_id': account.id,
                                 'account_name': account.nick_verbose,
                                 'session_expire_at': logic.get_session_expire_at_timestamp(self.request)})

        return self.error('accounts.auth.login.form_errors', login_form.errors)

    @api.handler(versions=('1.0',))
    @handler('api', 'logout', name='api-logout', method=['post'])
    def api_logout(self, api_version):
        u'''
Выйти из игры

- **адрес:** /accounts/auth/api/logout
- **http-метод:** POST
- **версии:** 1.0
- **параметры:** нет
- **возможные ошибки**: нет
        '''

        logic.logout_user(self.request)
        return self.ok()

    @api.handler(versions=('1.0',))
    @handler('api', 'logout', name='api-logout', method=['get'])
    def logout_get(self, api_version):
        logic.logout_user(self.request)
        return self.redirect('/')


class ProfileResource(BaseAccountsResource):

    @decorators.refuse_third_party
    def initialize(self, *argv, **kwargs):
        super(ProfileResource, self).initialize(*argv, **kwargs)

    @login_required
    @handler('', name='show', method='get')
    def profile(self):
        data = {'email': self.account.email if self.account.email else u'укажите email',
                'nick': self.account.nick if not self.account.is_fast and self.account.nick else u'укажите ваше имя'}
        edit_profile_form = forms.EditProfileForm(data)

        settings_form = forms.SettingsForm({'personal_messages_subscription': self.account.personal_messages_subscription,
                                            'news_subscription': self.account.news_subscription,
                                            'description': self.account.description})

        return self.template('accounts/profile.html',
                             {'edit_profile_form': edit_profile_form,
                              'settings_form': settings_form} )

    @login_required
    @handler('edited', name='edited', method='get')
    def edit_profile_done(self):
        return self.template('accounts/profile_edited.html')

    @login_required
    @handler('confirm-email-request', method='get')
    def confirm_email_request(self):
        return self.template('accounts/confirm_email_request.html')

    @login_required
    @handler('update', name='update', method='post')
    def update_profile(self):

        edit_profile_form = forms.EditProfileForm(self.request.POST)

        if not edit_profile_form.is_valid():
            return self.json_error('accounts.profile.update.form_errors', edit_profile_form.errors)

        if self.account.is_fast and not (edit_profile_form.c.email and edit_profile_form.c.password and edit_profile_form.c.nick):
            return self.json_error('accounts.profile.update.empty_fields', u'Необходимо заполнить все поля')

        if edit_profile_form.c.email:
            existed_account = AccountPrototype.get_by_email(edit_profile_form.c.email)
            if existed_account and existed_account.id != self.account.id:
                return self.json_error('accounts.profile.update.used_email', {'email': [u'На этот адрес уже зарегистрирован аккаунт']})

        if edit_profile_form.c.nick:
            existed_account = AccountPrototype.get_by_nick(edit_profile_form.c.nick)
            if existed_account and existed_account.id != self.account.id:
                return self.json_error('accounts.profile.update.used_nick', {'nick': [u'Это имя уже занято']})

        if edit_profile_form.c.nick != self.account.nick and self.account.is_ban_any:
            return self.json_error('accounts.profile.update.banned', {'nick': [u'Вы не можете менять ник пока забанены']})

        task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                     new_email=edit_profile_form.c.email,
                                                     new_password=edit_profile_form.c.password,
                                                     new_nick=edit_profile_form.c.nick,
                                                     relogin_required=True)

        postponed_task = task.process(logger)

        if postponed_task is not None:
            return self.json_processing(postponed_task.status_url)

        return self.json_ok(data={'next_url': reverse('accounts:profile:confirm-email-request')})


    @handler('confirm-email', method='get')
    def confirm_email(self, uuid): # pylint: disable=W0621

        task = ChangeCredentialsTaskPrototype.get_by_uuid(uuid)

        context = {'already_processed': False,
                   'timeout': False,
                   'error_occured': False,
                   'task': None}

        if task is None:
            context['wrong_link'] = True
            return self.template('accounts/confirm_email.html', context)

        if task.has_already_processed:
            context['already_processed'] = True
            return self.template('accounts/confirm_email.html', context)

        postponed_task = task.process(logger)

        if task.state == relations.CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT:
            context['timeout'] = True
            return self.template('accounts/confirm_email.html', context)

        if task.state == relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR:
            context['error_occured'] = True
            return self.template('accounts/confirm_email.html', context)

        return self.redirect(postponed_task.wait_url)

    @login_required
    @handler('update-settings', name='update-settings', method='post')
    def update_settings(self):

        settings_form = forms.SettingsForm(self.request.POST)

        if not settings_form.is_valid():
            return self.json_error('accounts.profile.update_settings.form_errors', settings_form.errors)

        self.account.update_settings(settings_form)

        return self.json_ok(data={'next_url': reverse('accounts:profile:edited')})

    @handler('reset-password', method='get')
    def reset_password_page(self):
        if self.account.is_authenticated():
            return self.redirect('/')

        reset_password_form = forms.ResetPasswordForm()
        return self.template('accounts/reset_password.html',
                             {'reset_password_form': reset_password_form} )

    @handler('reset-password-done', method='get')
    def reset_password_done(self):
        if self.account.is_authenticated():
            return self.redirect('/')

        return self.template('accounts/reset_password_done.html', {} )

    @validate_argument('task', ResetPasswordTaskPrototype.get_by_uuid,
                       'accounts.profile.reset_password_done', u'Не получилось сбросить пароль, возможно вы используете неверную ссылку')
    @handler('reset-password-processed', method='get')
    def reset_password_processed(self, task):
        if self.account.is_authenticated():
            return self.redirect('/')

        if task.is_time_expired:
            return self.auto_error('accounts.profile.reset_password_processed.time_expired', u'Срок действия ссылки закончился, попробуйте восстановить пароль ещё раз')

        if task.is_processed:
            return self.auto_error('accounts.profile.reset_password_processed.already_processed',
                                   u'Эта ссылка уже была использована для восстановления пароля, одну ссылку можно использовать только один раз')

        password = task.process(logger=logger)

        return self.template('accounts/reset_password_processed.html', {'password': password} )

    @handler('reset-password', method='post')
    def reset_password(self):

        if self.account.is_authenticated():
            return self.json_error('accounts.profile.reset_password.already_logined', u'Вы уже вошли на сайт и можете просто изменить пароль')

        reset_password_form = forms.ResetPasswordForm(self.request.POST)

        if not reset_password_form.is_valid():
            return self.json_error('accounts.profile.reset_password.form_errors', reset_password_form.errors)

        account = AccountPrototype.get_by_email(reset_password_form.c.email)

        if account is None:
            return self.auto_error('accounts.profile.reset_password.wrong_email', u'На указанный email аккаунт не зарегистрирован')

        ResetPasswordTaskPrototype.create(account)

        return self.json_ok()

    @login_required
    @handler('update-last-news-reminder-time', method='post')
    def update_last_news_reminder_time(self):
        self.account.update_last_news_remind_time()
        return self.json_ok()
