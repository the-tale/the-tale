# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as django_logout
from django.utils.log import getLogger

from dext.views.resources import handler

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype, RegistrationTaskPrototype, ChangeCredentialsTaskPrototype
from accounts.models import REGISTRATION_TASK_STATE, CHANGE_CREDENTIALS_TASK_STATE
from accounts import forms
from accounts.conf import accounts_settings
from accounts.logic import logout_user, login_user, force_login_user

from portal.workers.environment import workers_environment as infrastructure_workers_environment

logger = getLogger('django.request')

class AccountsResource(Resource):

    def initialize(self, account_id=None, *args, **kwargs):
        super(AccountsResource, self).initialize(*args, **kwargs)
        self.current_account_id = account_id

    @property
    def current_account(self):
        if not hasattr(self, '_account'):
            self._current_account = AccountPrototype.get_by_id(int(self.current_account_id)) if self.current_account_id else None

        return self._current_account

    @handler('fast-registration', method='post')
    def fast_registration(self):

        if not self.user.is_anonymous():
            return self.json_error('accounts.fast_registration.already_registered', u'Вы уже зарегистрированы')

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:
            task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]
            task = RegistrationTaskPrototype.get_by_id(task_id)
            if task is not None:
                if task.state == REGISTRATION_TASK_STATE.PROCESSED:
                    return self.json_error('accounts.fast_registration.already_processed', u'Ваша регистрация уже обработана, обновите страницу')
                if task.state == REGISTRATION_TASK_STATE.WAITING:
                    return self.json_error('accounts.fast_registration.is_processing', u'Ваша регистрация уже обрабатывается, пожалуйста, подождите')

        registration_task = RegistrationTaskPrototype.create()

        self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY] = registration_task.id

        infrastructure_workers_environment.registration.cmd_register(registration_task.id)

        return self.json_processing(reverse('accounts:fast-registration-status'))


    @handler('fast-registration-status', method='get')
    def fast_registration_status(self):

        # if task already checked in middleware
        if not self.user.is_anonymous():
            return self.json_ok()

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in self.request.session:
            return self.json_error('accounts.fast_registration_status.wrong_request', u'Вы не пытались регистрироваться или уже зарегистрировались')

        task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]

        registration_task = RegistrationTaskPrototype.get_by_id(int(task_id))

        if registration_task.state == REGISTRATION_TASK_STATE.WAITING:
            return self.json_processing(reverse('accounts:fast-registration-status'))

        if registration_task.state == REGISTRATION_TASK_STATE.UNPROCESSED:
            return self.json_error('accounts.fast_registration_status.timeout', u'Таймаут при обработке запроса, повторите попытку')

        if registration_task.state == REGISTRATION_TASK_STATE.PROCESSED:
            return self.json_ok()

        return self.json_error('accounts.fast_registration_status.error', u'ошибка при регистрации, повторите попытку')

    @login_required
    @handler('profile', method='get')
    def profile(self):
        data = {'email': self.account.email if self.account.email else u'укажите email',
                'nick': self.account.nick if not self.account.is_fast and self.account.nick else u'укажите ваше имя'}
        edit_profile_form = forms.EditProfileForm(data)
        return self.template('accounts/profile.html',
                             {'edit_profile_form': edit_profile_form} )

    @login_required
    @handler('profile', 'edited', name='profile-edited', method='get')
    def edit_profile_done(self):
        return self.template('accounts/profile_edited.html')

    @login_required
    @handler('profile', 'confirm-email-request', method='get')
    def confirm_email_request(self):
        return self.template('accounts/confirm_email_request.html')

    @login_required
    @handler('profile', 'update', name='profile-update', method='post')
    def update_profile(self):

        edit_profile_form = forms.EditProfileForm(self.request.POST)

        if edit_profile_form.is_valid():

            if self.account.is_fast and not (edit_profile_form.c.email and edit_profile_form.c.password and edit_profile_form.c.nick):
                return self.json(status='error', error=u'Необходимо заполнить все поля')

            if edit_profile_form.c.email:
                existed_account = AccountPrototype.get_by_email(edit_profile_form.c.email)
                if existed_account and existed_account.id != self.account.id:
                    return self.json(status='error', errors={'email': [u'На этот адрес уже зарегистрирован аккаунт']})

            if edit_profile_form.c.nick:
                existed_account = AccountPrototype.get_by_nick(edit_profile_form.c.nick)
                if existed_account and existed_account.id != self.account.id:
                    return self.json(status='error', errors={'nick': [u'Это имя уже занято']})

            task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                         new_email=edit_profile_form.c.email,
                                                         new_password=edit_profile_form.c.password,
                                                         new_nick=edit_profile_form.c.nick)

            # print task.uuid

            task.process(logger)

            next_url = reverse('accounts:profile-edited')
            if task.email_changed:
                next_url = reverse('accounts:confirm-email-request')

            return self.json(status='ok', data={'next_url': next_url})

        return self.json(status='error', errors=edit_profile_form.errors)

    @handler('profile', 'confirm-email', method='get')
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
            return self.json(status='error', error=u'Вы уже вошли на сайт и можете просто изменить пароль')

        reset_password_form = forms.ResetPasswordForm(self.request.POST)

        if reset_password_form.is_valid():

            account = AccountPrototype.get_by_email(reset_password_form.c.email)

            if account is not None:
                account.reset_password()

            return self.json(status='ok')

        return self.json(status='error', errors=reset_password_form.errors)


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
                return self.json(status='error', error=u'Неверный логин или пароль')

            if not account.user.check_password(login_form.c.password):
                return self.json(status='error', error=u'Неверный логин или пароль')

            login_user(self.request, username=account.nick, password=login_form.c.password)

            return self.json_ok(data={'next_url': next_url})

        return self.json(status='error', errors=login_form.errors)

    @handler('logout', method=['post'])
    def logout_post(self):
        logout_user(self.request)
        return self.json(status='ok')

    @handler('logout', method=['get'])
    def logout_get(self):
        django_logout(self.request)
        self.request.session.flush()
        return self.redirect('/')
