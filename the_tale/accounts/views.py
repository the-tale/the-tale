# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.contrib.auth import logout as django_logout

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource

from accounts.prototypes import get_account_by_id, RegistrationTaskPrototype
from accounts.models import REGISTRATION_TASK_STATE
from accounts import forms
from accounts.conf import accounts_settings
from accounts.logic import logout_user, login_user

from portal.workers.environment import workers_environment as infrastructure_workers_environment


class AccountsResource(Resource):

    def __init__(self, request, account_id=None, *args, **kwargs):
        self.account_id = account_id
        super(AccountsResource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = get_account_by_id(int(self.account_id))

        return self._account

    @handler('introduction', method='get')
    def introduction(self):
        return self.template('accounts/introduction.html')


    @handler('fast_registration', method='post')
    def fast_registration(self):

        if not self.user.is_anonymous():
            raise Error(u'Вы уже зарегистрированы')

        if accounts_settings.SESSION_REGISTRATION_TASK_ID_KEY in self.request.session:
            raise Error(u'Ваша регистрация уже обрабатывается, пожалуйста, подождите')

        registration_task = RegistrationTaskPrototype.create()

        infrastructure_workers_environment.registration.cmd_register(registration_task.id)

        return self.json(status='processing', status_url=reverse('accounts:fast_registration_status') )


    @handler('fast_registration_status', method='get')
    def fast_registration_status(self, task_id):

        # if task already checked in middleware
        if not self.user.is_anonymous():
            return self.json(status='ok')

        registration_task = RegistrationTaskPrototype.get_by_id(int(task_id))

        if registration_task is None:
            raise Error(u'неверный запрос на регистрацию, повторите попытку ещё раз')

        if registration_task.state == REGISTRATION_TASK_STATE.WAITING:
            return self.json(status='processing',
                             status_url=reverse('accounts:fast_registration_status') + '?task_id=%d' % registration_task.id )

        if registration_task.state == REGISTRATION_TASK_STATE.UNPROCESSED:
            raise Error(u'Таймаут при обработке запроса, повторите попытку')

        if registration_task.state == REGISTRATION_TASK_STATE.PROCESSED:
            return self.json(status='ok')

        raise Error(u'ошибка при регистрации, повторите попытку')

    @handler('profile', method='get')
    def profile(self):
        edit_profile_form = forms.EditProfileForm()
        return self.template('accounts/profile.html',
                             {'edit_profile_form': edit_profile_form} )

    @handler('profile', 'edit', method='post')
    def edit_profile(self):

        edit_profile_form = forms.EditProfileForm(self.request.POST)

        if edit_profile_form.is_valid():
            if edit_profile_form.c.password:
                self.user.set_password(edit_profile_form.password)
            self.user.email = edit_profile_form.email
            self.user.save()

            return self.json(status='ok')

        return self.json(status='error', errors=edit_profile_form.errors)


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
