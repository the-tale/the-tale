# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout

from django_next.views.resources import BaseResource, handler
from django_next.utils.decorators import nested_commit_on_success

from game.angels.models import Angel
from game.cards.prototypes import FirstHeroCard, PushToQuestCard

from .models import Account
from . import forms

class AccountsResource(BaseResource):

    def __init__(self, request, account_id=None, *args, **kwargs):
        self.account_id = account_id
        super(AccountsResource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = None
            try:
                self._account = Account.objects.get(id=int(self.account_id))
            except Account.DoesNotExist:
                pass
                
        return self._account

    @handler('registration', method='get')
    def register_page(self):
        registration_form = forms.RegistrationForm()
        return self.template('accounts/registration.html',
                             {'registration_form': registration_form} )


    @handler('registration', method='post')
    @nested_commit_on_success
    def register(self):
        registration_form = forms.RegistrationForm(self.request.POST)

        if registration_form.is_valid():

            try:
                User.objects.get(username=registration_form.c.nick)
                return self.json(status='error', errors={'nick': [u'Пользователь с таким ником уже существует']})
            except User.DoesNotExist:
                pass

            user = User.objects.create_user(registration_form.c.nick,
                                            registration_form.c.email,
                                            registration_form.c.password)

            account = Account.objects.create(user=user)
            angel = Angel.objects.create(account=account, name=user.username)
            first_card = FirstHeroCard.create(angel)
            push_card = PushToQuestCard.create(angel)

            self.login_user(user.username, registration_form.c.password)

            return self.json(status='ok')

        return self.json(status='error', errors=registration_form.errors)


    @handler('login', method='get')
    def login_page(self):
        login_form = forms.LoginForm()
        return self.template('accounts/login.html',
                             {'login_form': login_form} )

    def login_user(self, username, password):
        user = django_authenticate(username=username, password=password)
        django_login(self.request, user)

    @handler('login', method='post')
    def login(self):
        login_form = forms.LoginForm(self.request.POST)

        if login_form.is_valid():

            try:
                user = User.objects.get(email=login_form.c.email)
            except User.DoesNotExist:
                return self.json(status='error', errors={'nick': [u'Пользователь не найден']})

            if not user.check_password(login_form.c.password):
                return self.json(status='error', errors={'nick': [u'Неверный пароль']})

            self.login_user(username=user.username, password=login_form.c.password)

            return self.json(status='ok')

        return self.json(status='error', errors=login_form.errors)

    @handler('logout', method=['post'])
    def logout_post(self):
        django_logout(self.request)
        return self.json(status='ok')

    @handler('logout', method=['get'])
    def logout_get(self):
        django_logout(self.request)
        return self.redirect('/')

