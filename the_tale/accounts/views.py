# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout

from dext.views.resources import handler

from common.utils.resources import Resource

from game.workers.environment import workers_environment

from .prototypes import get_account_by_id
from . import forms

from accounts.logic import register_user, REGISTER_USER_RESULT

class AccountsResource(Resource):

    def __init__(self, request, account_id=None, *args, **kwargs):
        self.account_id = account_id
        super(AccountsResource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = get_account_by_id(int(self.account_id))

        return self._account

    @handler('registration', method='get')
    def register_page(self):
        if not self.user.is_anonymous():
            return self.redirect('/')

        registration_form = forms.RegistrationForm()
        return self.template('accounts/registration.html',
                             {'registration_form': registration_form} )


    @handler('registration', method='post')
    def register(self):

        if not self.user.is_anonymous():
            return self.json(status='error', error=u'Вы уже зарегистрированы')

        registration_form = forms.RegistrationForm(self.request.POST)

        if registration_form.is_valid():

            result, bundle_id = register_user(nick=registration_form.c.nick,
                                              email=registration_form.c.email,
                                              password=registration_form.c.password)

            if result == REGISTER_USER_RESULT.DUPLICATE_EMAIL:
                return self.json(status='error', errors={'email': [u'Пользователь с таким e-mail уже существует']})
            elif result == REGISTER_USER_RESULT.DUPLICATE_USERNAME:
                return self.json(status='error', errors={'nick': [u'Пользователь с таким ником уже существует']})
            elif result == REGISTER_USER_RESULT.OK:
                pass
            else:
                return self.json(status='error', errors={'nick': [u'Неизвестная ошибка']})

            self.login_user(registration_form.c.nick, registration_form.c.password)

            # send command after success commit
            # TODO: check if bundle created
            workers_environment.supervisor.cmd_register_bundle(bundle_id)

            return self.json(status='ok')

        return self.json(status='error', errors=registration_form.errors)


    @handler('login', method='get')
    def login_page(self):
        if not self.user.is_anonymous():
            return self.redirect('/')

        login_form = forms.LoginForm()
        return self.template('accounts/login.html',
                             {'login_form': login_form} )

    def login_user(self, username, password):
        self.request.session.flush()
        user = django_authenticate(username=username, password=password)
        django_login(self.request, user)

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

            self.login_user(username=user.username, password=login_form.c.password)

            return self.json(status='ok')

        return self.json(status='error', errors=login_form.errors)

    @handler('logout', method=['post'])
    def logout_post(self):
        django_logout(self.request)
        self.request.session.flush()
        return self.json(status='ok')

    @handler('logout', method=['get'])
    def logout_get(self):
        django_logout(self.request)
        self.request.session.flush()
        return self.redirect('/')
