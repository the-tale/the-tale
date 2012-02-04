# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate as django_authenticate, logout as django_logout

from dext.views.resources import BaseResource, handler
from dext.utils.decorators import nested_commit_on_success

from game.angels.prototypes import AngelPrototype
from game.heroes.prototypes import HeroPrototype

from game.bundles import BundlePrototype
from game.workers.environment import workers_environment


from .prototypes import AccountPrototype, get_account_by_id
from . import forms

class AccountsResource(BaseResource):

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
        registration_form = forms.RegistrationForm()
        return self.template('accounts/registration.html',
                             {'registration_form': registration_form} )


    @handler('registration', method='post')
    def register(self):
        registration_form = forms.RegistrationForm(self.request.POST)

        if registration_form.is_valid():

            with nested_commit_on_success():

                try:
                    User.objects.get(username=registration_form.c.nick)
                    return self.json(status='error', errors={'nick': [u'Пользователь с таким ником уже существует']})
                except User.DoesNotExist:
                    pass

                if User.objects.filter(email=registration_form.c.email).exists():
                    return self.json(status='error', errors={'email': [u'Пользователь с таким e-mail уже существует']})

                user = User.objects.create_user(registration_form.c.nick,
                                                registration_form.c.email,
                                                registration_form.c.password)

                account = AccountPrototype.create(user=user)
                angel = AngelPrototype.create(account=account, name=user.username)
                HeroPrototype.create(angel=angel)
            
                self.login_user(user.username, registration_form.c.password)

                bundle = BundlePrototype.create(angel)

            # send command after success commit
            # TODO: check if bumdle created
            workers_environment.supervisor.cmd_register_bundle(bundle.id)

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

