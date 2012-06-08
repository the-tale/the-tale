# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as django_logout

from dext.views.resources import handler

from common.utils.resources import Resource
from common.utils.decorators import login_required

from accounts.prototypes import AccountPrototype, RegistrationTaskPrototype, ChangeCredentialsTaskPrototype
from accounts.models import REGISTRATION_TASK_STATE
from accounts import forms
from accounts.conf import accounts_settings
from accounts.logic import logout_user, login_user

from portal.workers.environment import workers_environment as infrastructure_workers_environment


class AccountsResource(Resource):

    def __init__(self, request, account_id=None, *args, **kwargs):
        self.current_account_id = account_id
        super(AccountsResource, self).__init__(request, *args, **kwargs)

    @property
    def current_account(self):
        if not hasattr(self, '_account'):
            self._current_account = AccountPrototype.get_by_id(int(self.current_account_id)) if self.current_account_id else None

        return self._current_account

    @handler('introduction', method='get')
    def introduction(self):
        return self.template('accounts/introduction.html')


    @handler('fast_registration', method='post')
    def fast_registration(self):

        if not self.user.is_anonymous():
            return self.json(status='error', errors=u'Вы уже зарегистрированы')

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:
            return self.json(status='error', errors=u'Ваша регистрация уже обрабатывается, пожалуйста, подождите')

        registration_task = RegistrationTaskPrototype.create()

        self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY] = registration_task.id

        infrastructure_workers_environment.registration.cmd_register(registration_task.id)

        return self.json(status='processing', status_url=reverse('accounts:fast_registration_status') )


    @handler('fast_registration_status', method='get')
    def fast_registration_status(self):

        # if task already checked in middleware
        if not self.user.is_anonymous():
            return self.json(status='ok')

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY not in self.request.session:
            return self.json(status='error', errors=u'Вы не пытались регистрироваться или уже зарегистрировались')

        task_id = self.request.session[accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY]

        registration_task = RegistrationTaskPrototype.get_by_id(int(task_id))

        if registration_task.state == REGISTRATION_TASK_STATE.WAITING:
            return self.json(status='processing', status_url=reverse('accounts:fast_registration_status'))

        if registration_task.state == REGISTRATION_TASK_STATE.UNPROCESSED:
            return self.json(status='error', errors=u'Таймаут при обработке запроса, повторите попытку')

        if registration_task.state == REGISTRATION_TASK_STATE.PROCESSED:
            return self.json(status='ok')

        return self.json(status='error', errors=u'ошибка при регистрации, повторите попытку')

    @login_required
    @handler('profile', method='get')
    def profile(self):
        edit_profile_form = forms.EditProfileForm()
        return self.template('accounts/profile.html',
                             {'edit_profile_form': edit_profile_form} )

    @login_required
    @handler('profile', 'edited', name='profile_edited', method='get')
    def edit_profile_done(self):
        return self.template('accounts/profile_edited.html')

    @login_required
    @handler('profile', 'password_changed', name='password_changed', method='get')
    def password_changed(self):
        return self.template('accounts/password_changed.html')

    @login_required
    @handler('profile', 'email_changed', name='email_changed', method='get')
    def email_changed(self):
        return self.template('accounts/email_changed.html')

    @login_required
    @handler('profile', 'edit', name='profile_edit', method='post')
    def edit_profile(self):

        edit_profile_form = forms.EditProfileForm(self.request.POST)

        if edit_profile_form.is_valid():

            task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                         old_email=self.user.email,
                                                         new_email=edit_profile_form.c.email,
                                                         new_password=edit_profile_form.c.password)

            task.process()

            next_url = reverse('accounts:password_changed')
            if task.email_changed:
                next_url = reverse('accounts:email_changed')

            return self.json(status='ok', data={'next_url': next_url})

        return self.json(status='error', errors=edit_profile_form.errors)

    @handler('profile', 'confirm_email', method='get')
    def confirm_email(self, uuid):

        task = ChangeCredentialsTaskPrototype.get_by_uuid(uuid)

        if task is None:
            return self.template('accounts/confirm_email.html',
                                 {'error': u'неверная ссылка, убедитесь, что верно скопировали адрес',
                                  'task': None} )

        task.process()

        return self.template('accounts/confirm_email.html',
                             {'task': task} )

    @handler('login', method='get')
    def login_page(self):
        if not self.user.is_anonymous():
            return self.redirect('/')

        login_form = forms.LoginForm()
        return self.template('accounts/login.html',
                             {'login_form': login_form} )

    @handler('login', method='post')
    def login(self):
        login_form = forms.LoginForm(self.request.POST)

        if login_form.is_valid():

            try:
                user = User.objects.get(email=login_form.c.email)
            except User.DoesNotExist:
                return self.json(status='error', errors={'__all__': [u'Неверный логин или пароль']})

            if not user.check_password(login_form.c.password):
                return self.json(status='error', errors={'__all__': [u'Неверный логин или пароль']})

            login_user(self.request, username=user.username, password=login_form.c.password)

            return self.json(status='ok')

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
