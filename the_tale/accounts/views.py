# -*- coding: utf-8 -*-
import datetime

from django.core.urlresolvers import reverse
from django.contrib.auth import logout as django_logout
from django.utils.log import getLogger

from dext.views.resources import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype, RegistrationTaskPrototype, ChangeCredentialsTaskPrototype
from accounts.models import REGISTRATION_TASK_STATE, CHANGE_CREDENTIALS_TASK_STATE, Account
from accounts import forms
from accounts.conf import accounts_settings
from accounts.logic import logout_user, login_user, force_login_user

from game.heroes.models import Hero
from game.heroes.prototypes import HeroPrototype

from portal.workers.environment import workers_environment as infrastructure_workers_environment

logger = getLogger('django.request')

class RegistrationResource(Resource):

    @handler('fast', method='post')
    def fast(self):

        if not self.user.is_anonymous():
            return self.json_error('accounts.registration.fast.already_registered', u'Вы уже зарегистрированы')

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:
            task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
            task = RegistrationTaskPrototype.get_by_id(task_id)
            if task is not None:
                if task.state == REGISTRATION_TASK_STATE.PROCESSED:
                    return self.json_error('accounts.registration.fast.already_processed', u'Ваша регистрация уже обработана, обновите страницу')
                if task.state == REGISTRATION_TASK_STATE.WAITING:
                    return self.json_error('accounts.registration.fast.is_processing', u'Ваша регистрация уже обрабатывается, пожалуйста, подождите')

        registration_task = RegistrationTaskPrototype.create()

        self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY] = registration_task.id

        infrastructure_workers_environment.registration.cmd_register(registration_task.id)

        return self.json_processing(reverse('accounts:registration:fast-status'))


    @handler('fast-status', method='get')
    def fast_status(self):

        # if task already checked in middleware
        if not self.user.is_anonymous():
            return self.json_ok()

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in self.request.session:
            return self.json_error('accounts.registration.fast_status.wrong_request', u'Вы не пытались регистрироваться или уже зарегистрировались')

        task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]

        registration_task = RegistrationTaskPrototype.get_by_id(int(task_id))

        if registration_task.state == REGISTRATION_TASK_STATE.WAITING:
            return self.json_processing(reverse('accounts:registration:fast-status'))

        if registration_task.state == REGISTRATION_TASK_STATE.UNPROCESSED:
            return self.json_error('accounts.registration.fast_status.timeout', u'Таймаут при обработке запроса, повторите попытку')

        if registration_task.state == REGISTRATION_TASK_STATE.PROCESSED:
            return self.json_ok()

        return self.json_error('accounts.registration.fast_status.error', u'ошибка при регистрации, повторите попытку')


class AuthResource(Resource):

    @handler('login', method='get')
    def login_page(self, next_url='/'):
        if not self.user.is_anonymous():
            return self.redirect(next_url)

        login_form = forms.LoginForm()
        return self.template('accounts/login.html',
                             {'login_form': login_form,
                              'next_url': next_url} )

    @handler('login', method='post')
    def login(self, next_url='/'):
        login_form = forms.LoginForm(self.request.POST)

        if login_form.is_valid():

            account = AccountPrototype.get_by_email(login_form.c.email)
            if account is None:
                return self.json_error('accounts.auth.login.wrong_credentials', u'Неверный логин или пароль')

            if not account.user.check_password(login_form.c.password):
                return self.json_error('accounts.auth.login.wrong_credentials', u'Неверный логин или пароль')

            login_user(self.request, username=account.nick, password=login_form.c.password)

            return self.json_ok(data={'next_url': next_url})

        return self.json_error('accounts.auth.login.form_errors', login_form.errors)

    @handler('logout', method=['post'])
    def logout_post(self):
        logout_user(self.request)
        return self.json_ok()

    @handler('logout', method=['get'])
    def logout_get(self):
        django_logout(self.request)
        self.request.session.flush()
        return self.redirect('/')


class ProfileResource(Resource):

    @login_required
    @handler('', name='show', method='get')
    def profile(self):
        data = {'email': self.account.email if self.account.email else u'укажите email',
                'nick': self.account.nick if not self.account.is_fast and self.account.nick else u'укажите ваше имя'}
        edit_profile_form = forms.EditProfileForm(data)
        return self.template('accounts/profile.html',
                             {'edit_profile_form': edit_profile_form} )

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

        if edit_profile_form.is_valid():

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

            task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                         new_email=edit_profile_form.c.email,
                                                         new_password=edit_profile_form.c.password,
                                                         new_nick=edit_profile_form.c.nick)

            # print task.uuid

            task.process(logger)

            next_url = reverse('accounts:profile:edited')
            if task.email_changed:
                next_url = reverse('accounts:profile:confirm-email-request')

            return self.json_ok(data={'next_url': next_url})

        return self.json_error('accounts.profile.update.form_errors', edit_profile_form.errors)

    @handler('confirm-email', method='get')
    def confirm_email(self, uuid):

        task = ChangeCredentialsTaskPrototype.get_by_uuid(uuid)

        if task is None:
            return self.template('accounts/confirm_email.html',
                                 {'error': u'Неверная ссылка, убедитесь, что верно скопировали адрес'} )

        if task.has_already_processed:
            return self.template('accounts/confirm_email.html',
                                 {'already_processed': True} )

        task.process(logger)

        if task.state == CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT:
            return self.template('accounts/confirm_email.html',
                                 {'timout': True} )

        if task.state == CHANGE_CREDENTIALS_TASK_STATE.ERROR:
            return self.template('accounts/confirm_email.html',
                                 {'error_occured': True} )

        force_login_user(self.request, task.account.user)

        self._account = task.account

        return self.template('accounts/confirm_email.html',
                             {'task': task} )

    @handler('reset-password', method='get')
    def reset_password_page(self):
        if not self.user.is_anonymous():
            return self.redirect('/')

        reset_password_form = forms.ResetPasswordForm()
        return self.template('accounts/reset_password.html',
                             {'reset_password_form': reset_password_form} )

    @handler('reset-password-done', method='get')
    def reset_password_done(self):
        if not self.user.is_anonymous():
            return self.redirect('/')

        reset_password_form = forms.ResetPasswordForm()
        return self.template('accounts/reset_password_done.html',
                             {'reset_password_form': reset_password_form} )

    @handler('reset-password', method='post')
    def reset_password(self):

        if not self.user.is_anonymous():
            return self.json_error('accounts.profile.reset_password.already_logined', u'Вы уже вошли на сайт и можете просто изменить пароль')

        reset_password_form = forms.ResetPasswordForm(self.request.POST)

        if reset_password_form.is_valid():

            account = AccountPrototype.get_by_email(reset_password_form.c.email)

            if account is not None:
                account.reset_password()

            return self.json_ok()

        return self.json_error('accounts.profile.reset_password.form_errors', reset_password_form.errors)

    @handler('update-last-news-reminder-time', method='post')
    def update_last_news_reminder_time(self):

        self.account.last_news_remind_time = datetime.datetime.now()
        self.account.save()

        return self.json_ok()


class AccountResource(Resource):

    def initialize(self, account_id=None, *args, **kwargs):
        super(AccountResource, self).initialize(*args, **kwargs)

        if account_id:
            try:
                self.master_account_id = int(account_id)
            except:
                return self.auto_error('accounts.wrong_id', u'Неверный идентификатор игрока', status_code=404)

            if self.master_account is None:
                return self.auto_error('accounts.account_not_found', u'Игрок не найден', status_code=404)

    @property
    def master_account(self):
        if not hasattr(self, '_master_account'):
            self._master_account = AccountPrototype.get_by_id(self.master_account_id)
        return self._master_account

    @handler('', method='get')
    def index(self, page=1):

        accounts_count = Account.objects.filter(is_fast=False).count()

        url_builder = UrlBuilder(reverse('accounts:'), arguments={'page': page})

        page = int(page) - 1

        paginator = Paginator(page, accounts_count, accounts_settings.ACCOUNTS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        account_from, account_to = paginator.page_borders(page)

        accounts_models = Account.objects.filter(is_fast=False).select_related().order_by('nick')[account_from:account_to]

        accounts = [AccountPrototype(model) for model in accounts_models]

        accounts_ids = [ model.id for model in accounts_models]

        heroes = dict( (model.account_id, HeroPrototype(model)) for model in Hero.objects.filter(account_id__in=accounts_ids))

        return self.template('accounts/index.html',
                             {'heroes': heroes,
                              'accounts': accounts,
                              'current_page_number': page,
                              'paginator': paginator  } )

    @handler('#account_id', name='show', method='get')
    def show(self):
        from forum.models import Thread
        from game.bills.models import Bill
        from game.ratings.prototypes import RatingPlacesPrototype, RatingValuesPrototype

        bills_count = Bill.objects.filter(owner=self.master_account.model).count()

        threads_count = Thread.objects.filter(author=self.master_account.model).count()

        threads_with_posts = Thread.objects.filter(post__author=self.master_account.model).distinct().count()

        rating_places = RatingPlacesPrototype.get_for_account(self.master_account)

        rating_values = RatingValuesPrototype.get_for_account(self.master_account)

        return self.template('accounts/show.html',
                             {'master_hero': HeroPrototype.get_by_account_id(self.master_account_id),
                              'master_account': self.master_account,
                              'rating_places': rating_places,
                              'rating_values': rating_values,
                              'bills_count': bills_count,
                              'threads_with_posts': threads_with_posts,
                              'threads_count': threads_count} )
