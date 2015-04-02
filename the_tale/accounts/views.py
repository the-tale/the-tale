# coding: utf-8
import uuid

from django.core.urlresolvers import reverse
from django.utils.log import getLogger

from dext.common.utils import views as dext_views
from dext.common.utils import exceptions as dext_exceptions
from dext.common.utils.urls import UrlBuilder
from dext.views import handler, validator, validate_argument


from the_tale.amqp_environment import environment

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.pagination import Paginator
from the_tale.common.utils.decorators import login_required
from the_tale.common.utils import api

from the_tale.game.heroes.models import Hero
from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.accounts.friends.prototypes import FriendshipPrototype
from the_tale.accounts.personal_messages.prototypes import MessagePrototype

from the_tale.accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype, AwardPrototype, ResetPasswordTaskPrototype
from the_tale.accounts.postponed_tasks import RegistrationTask
from the_tale.accounts import relations
from the_tale.accounts import forms
from the_tale.accounts.conf import accounts_settings
from the_tale.accounts import logic

from the_tale.accounts.clans.prototypes import ClanPrototype

from the_tale.accounts.third_party import decorators

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


current_account_processor = CurrentAccountProcessor()


class SuperuserProcessor(dext_views.BaseViewProcessor):
    __slots__ = ('required', )

    def __init__(self, required, **kwargs):
        super(SuperuserProcessor, self).__init__(**kwargs)
        self.required = required

    def preprocess(self, context):
        context.django_superuser = context.account.is_superuser

        if self.required and not context.django_superuser:
            raise dext_views.ViewError(code='common.superuser_required', message=u'У Вас нет прав для проведения данной операции')


class AccountProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            account_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        account = AccountPrototype.get_by_id(account_id)

        if account is None:
            self.raise_wrong_value(context=context)

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

login_required_processor = LoginRequiredProcessor()


class FullAccountProcessor(dext_views.BaseViewProcessor):

    def preprocess(self, context):
        if context.account.is_fast:
            raise dext_exceptions.ViewError(code='common.fast_account', message=u'Вы не закончили регистрацию и данная функция вам не доступна')

full_account_processor = FullAccountProcessor()


class BanGameProcessor(dext_views.BaseViewProcessor):

    def preprocess(self, context):
        if context.account.is_ban_game:
            raise dext_exceptions.ViewError(code='common.ban_game', message=u'Вам запрещено проводить эту операцию')

ban_game_processor = BanGameProcessor()


###############################
# end of new view processors
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

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:

            task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
            task = PostponedTaskPrototype.get_by_id(task_id)

            if task is not None:
                if task.state.is_processed:
                    return self.json_error('accounts.registration.fast.already_processed', u'Вы уже зарегистрированы, обновите страницу')
                if task.state.is_waiting:
                    return self.json_processing(task.status_url)
                # in other case create new task

        referer = None
        if accounts_settings.SESSION_REGISTRATION_REFERER_KEY in self.request.session:
            referer = self.request.session[accounts_settings.SESSION_REGISTRATION_REFERER_KEY]

        referral_of_id = None
        if accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY in self.request.session:
            referral_of_id = self.request.session[accounts_settings.SESSION_REGISTRATION_REFERRAL_KEY]

        action_id = None
        if accounts_settings.SESSION_REGISTRATION_ACTION_KEY in self.request.session:
            action_id = self.request.session[accounts_settings.SESSION_REGISTRATION_ACTION_KEY]

        registration_task = RegistrationTask(account_id=None, referer=referer, referral_of_id=referral_of_id, action_id=action_id)

        task = PostponedTaskPrototype.create(registration_task,
                                             live_time=accounts_settings.REGISTRATION_TIMEOUT)

        self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY] = task.id

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


class AccountResource(BaseAccountsResource):

    @validate_argument('account', AccountPrototype.get_by_id, 'accounts.account', u'Аккаунт не найден')
    def initialize(self, account=None, *args, **kwargs):
        super(AccountResource, self).initialize(*args, **kwargs)
        self.master_account = account
        self.can_moderate_accounts = self.account.has_perm('accounts.moderate_account')

    @validator(code='accounts.account.moderator_rights_required', message=u'Вы не являетесь модератором')
    def validate_moderator_rights(self, *args, **kwargs): return self.can_moderate_accounts

    @handler('', method='get')
    def index(self, page=1, prefix=''):

        accounts_query = AccountPrototype.live_query()

        if prefix:
            accounts_query = accounts_query.filter(nick__istartswith=prefix)

        accounts_count = accounts_query.count()

        url_builder = UrlBuilder(reverse('accounts:'), arguments={'page': page,
                                                                  'prefix': prefix})

        page = int(page) - 1

        paginator = Paginator(page, accounts_count, accounts_settings.ACCOUNTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        account_from, account_to = paginator.page_borders(page)

        accounts_models = accounts_query.select_related().order_by('nick')[account_from:account_to]

        accounts = [AccountPrototype(model) for model in accounts_models]

        accounts_ids = [ model.id for model in accounts_models]
        clans_ids = [ model.clan_id for model in accounts_models]

        heroes = dict( (model.account_id, HeroPrototype(model=model)) for model in Hero.objects.filter(account_id__in=accounts_ids))

        clans = {clan.id:clan for clan in ClanPrototype.get_list_by_id(clans_ids)}

        return self.template('accounts/index.html',
                             {'heroes': heroes,
                              'prefix': prefix,
                              'accounts': accounts,
                              'clans': clans,
                              'current_page_number': page,
                              'paginator': paginator  } )


    @handler('#account', name='show', method='get')
    def show(self): # pylint: disable=R0914
        from the_tale.game.ratings import relations as ratings_relations

        friendship = FriendshipPrototype.get_for_bidirectional(self.account, self.master_account)

        master_hero = HeroPrototype.get_by_account_id(self.master_account.id)

        return self.template('accounts/show.html',
                             {'master_hero': master_hero,
                              'account_info': logic.get_account_info(self.master_account, master_hero),
                              'master_account': self.master_account,
                              'accounts_settings': accounts_settings,
                              'RATING_TYPE': ratings_relations.RATING_TYPE,
                              'informer_link': accounts_settings.INFORMER_LINK % {'account_id': self.master_account.id},
                              'friendship': friendship} )

    @api.handler(versions=('1.0',))
    @handler('#account', 'api', 'show', name='api-show', method=['get'])
    def api_show(self, api_version):
        u'''
Получить информацию об игроке

- **адрес:** /accounts/&lt;account_id&gt;/api/show
- **http-метод:** GET
- **версии:** 1.0
- **параметры:**
    * URL account_id — идентификатор игрока
- **возможные ошибки**:
    * accounts.account.account.not_found — аккаунт с таким идентификатором не найден

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

        master_hero = HeroPrototype.get_by_account_id(self.master_account.id)

        return self.ok(data=logic.get_account_info(self.master_account, master_hero))


    @login_required
    @validate_moderator_rights()
    @handler('#account', 'admin', name='admin', method='get')
    def admin(self):
        from the_tale.accounts.payments.forms import GMForm
        return self.template('accounts/admin.html',
                             {'master_account': self.master_account,
                              'give_award_form': forms.GiveAwardForm(),
                              'give_money_form': GMForm(),
                              'ban_form': forms.BanForm()} )


    @validate_moderator_rights()
    @handler('#account', 'give-award', name='give-award', method='post')
    def give_award(self):

        form = forms.GiveAwardForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.account.give_award.form_errors', form.errors)

        AwardPrototype.create(description=form.c.description,
                              type=form.c.type,
                              account=self.master_account)

        return self.json_ok()



    @validate_moderator_rights()
    @handler('#account', 'reset-nick', name='reset-nick', method='post')
    def reset_nick(self):
        task = ChangeCredentialsTaskPrototype.create(account=self.master_account,
                                                     new_nick=u'%s (%s)' % (accounts_settings.RESET_NICK_PREFIX, uuid.uuid4().hex))

        postponed_task = task.process(logger)

        return self.json_processing(postponed_task.status_url)

    @validate_moderator_rights()
    @handler('#account', 'ban', name='ban', method='post')
    def ban(self):

        form = forms.BanForm(self.request.POST)

        if not form.is_valid():
            return self.json_error('accounts.account.ban.form_errors', form.errors)

        if form.c.ban_type.is_FORUM:
            self.master_account.ban_forum(form.c.ban_time.days)
            message = u'Вы лишены права общаться на форуме. Причина: \n\n%(message)s'
        elif form.c.ban_type.is_GAME:
            self.master_account.ban_game(form.c.ban_time.days)
            message = u'Ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'
        elif form.c.ban_type.is_TOTAL:
            self.master_account.ban_forum(form.c.ban_time.days)
            self.master_account.ban_game(form.c.ban_time.days)
            message = u'Вы лишены права общаться на форуме, ваш герой лишён возможности влиять на мир игры. Причина: \n\n%(message)s'
        else:
            return self.json_error('accounts.account.ban.unknown_ban_type', u'Неизвестный тип бана')

        MessagePrototype.create(logic.get_system_user(),
                                self.master_account,
                                message % {'message': form.c.description})

        return self.json_ok()

    @validate_moderator_rights()
    @handler('#account', 'reset-bans', method='post')
    def reset_bans(self):

        self.master_account.ban_forum(0)
        self.master_account.ban_game(0)

        MessagePrototype.create(logic.get_system_user(),
                                self.master_account,
                                u'С вас сняли все ограничения, наложенные ранее.')

        return self.json_ok()
