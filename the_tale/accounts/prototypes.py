# -*- coding: utf-8 -*-
import sys
import uuid
import datetime
import traceback

from django.contrib.auth.hashers import make_password
from django.db import models

from dext.utils.decorators import nested_commit_on_success

from common.utils.password import generate_password

from accounts.models import Account, ChangeCredentialsTask, CHANGE_CREDENTIALS_TASK_STATE
from accounts.conf import accounts_settings
from accounts.exceptions import AccountsException

from game.workers.environment import workers_environment as game_workers_environment

class AccountPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, model_id):
        try:
            return AccountPrototype(model=Account.objects.select_related().get(id=model_id))
        except Account.DoesNotExist:
            return None

    @classmethod
    def get_by_email(cls, email):
        if email is None:
            return None

        try:
            return cls(Account.objects.select_related().get(email=email))
        except Account.DoesNotExist:
            return None

    @classmethod
    def get_by_nick(cls, nick):
        if nick is None:
            return None

        try:
            return cls(Account.objects.select_related().get(nick=nick))
        except Account.DoesNotExist:
            return None

    def get_hero(self):
        from game.heroes.prototypes import HeroPrototype
        return HeroPrototype.get_by_account_id(self.id)

    @property
    def id(self): return self.model.id

    @property
    def user(self): return self.model.user

    @property
    def created_at(self): return self.model.created_at

    def get_is_fast(self): return self.model.is_fast
    def set_is_fast(self, value): self.model.is_fast = value
    is_fast = property(get_is_fast, set_is_fast)

    def get_nick(self): return self.model.nick
    def set_nick(self, value): self.model.nick = value
    nick = property(get_nick, set_nick)

    @property
    def nick_verbose(self): return self.model.nick if not self.model.is_fast else u'Игрок'

    def get_email(self): return self.model.email
    def set_email(self, value): self.model.email = value
    email = property(get_email, set_email)

    def get_last_news_remind_time(self): return self.model.last_news_remind_time
    def set_last_news_remind_time(self, value): self.model.last_news_remind_time = value
    last_news_remind_time = property(get_last_news_remind_time, set_last_news_remind_time)

    @property
    def new_messages_number(self): return self.model.new_messages_number
    def reset_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=0)
        self.model.new_messages_number = 0
    def increment_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=models.F('new_messages_number')+1)
        self.model.new_messages_number = self.model.new_messages_number + 1

    def reset_password(self):
        from accounts.email import ResetPasswordNotification
        new_password = generate_password(len_=accounts_settings.RESET_PASSWORD_LENGTH)
        self.user.set_password(new_password)
        self.user.save()
        email = ResetPasswordNotification({'password': new_password})
        email.send([self.user.email])

    @nested_commit_on_success
    def change_credentials(self, new_email=None, new_password=None, new_nick=None):
        from game.heroes.prototypes import HeroPrototype

        if new_password:
            self.user.password = new_password
        if new_email:
            self.user.email = new_email
            self.model.email = new_email
        if new_nick:
            self.user.username = new_nick
            self.nick = new_nick

        if self.is_fast:
            game_workers_environment.supervisor.cmd_mark_hero_as_not_fast(self.id, HeroPrototype.get_by_account_id(self.id).id)

        self.is_fast = False

        self.user.save()
        self.save()


    ###########################################
    # Object operations
    ###########################################

    def can_be_removed(self):
        return self.is_fast

    def remove(self):
        # registration_task = RegistrationTaskPrototype.get_by_account_id(self.id)
        # if registration_task:
        #     registration_task.unbind_from_account()

        return self.model.delete()

    def save(self): self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {}

    @classmethod
    def create(cls, user, nick, email, is_fast):
        account_model = Account.objects.create(user=user, nick=nick, email=email, is_fast=is_fast, last_news_remind_time=datetime.datetime.now())
        return AccountPrototype(model=account_model)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.model == other.model



class ChangeCredentialsTaskPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_uuid(cls, task_uuid):
        try:
            model = ChangeCredentialsTask.objects.get(uuid=task_uuid)
            return cls(model=model)
        except ChangeCredentialsTask.DoesNotExist:
            return None

    @classmethod
    def create(cls, account, new_email=None, new_password=None, new_nick=None):
        old_email = account.user.email
        if account.is_fast and new_email is None:
            raise AccountsException('new_email must be specified for fast account')
        if account.is_fast and new_password is None:
            raise AccountsException('password must be specified for fast account')
        if account.is_fast and new_nick is None:
            raise AccountsException('nick must be specified for fast account')

        if old_email == new_email:
            new_email = None

        model = ChangeCredentialsTask.objects.create(uuid=uuid.uuid4().hex,
                                                     account=account.model,
                                                     old_email=old_email,
                                                     new_email=new_email,
                                                     new_password=make_password(new_password) if new_password else '',
                                                     new_nick=new_nick)
        return cls(model=model)

    @property
    def id(self): return self.model.id

    @property
    def uuid(self): return self.model.uuid

    @property
    def state(self): return self.model.state

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = AccountPrototype.get_by_id(self.model.account_id)
        return self._account

    @property
    def email_changed(self):
        return self.model.new_email is not None and (self.model.old_email != self.model.new_email)

    def change_credentials(self):
        self.account.change_credentials(new_email=self.model.new_email, new_password=self.model.new_password, new_nick=self.model.new_nick)

    def request_email_confirmation(self):
        from accounts.email import ChangeEmailNotification
        if self.model.new_email is None:
            raise AccountsException('email not specified')
        email = ChangeEmailNotification({'task': self})
        email.send([self.model.new_email])

    @property
    def has_already_processed(self):
        return self.state not in (CHANGE_CREDENTIALS_TASK_STATE.WAITING, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)

    @nested_commit_on_success
    def process(self, logger):

        if self.has_already_processed:
            return

        if self.model.created_at + datetime.timedelta(seconds=accounts_settings.CHANGE_EMAIL_TIMEOUT) < datetime.datetime.now():
            self.model.state = CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT
            self.model.comment = 'timeout'
            self.model.save()
            return

        try:
            if self.state == CHANGE_CREDENTIALS_TASK_STATE.WAITING:
                if self.email_changed:
                    self.request_email_confirmation()
                    self.model.state = CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT
                    self.model.save()
                    return
                else:
                    self.change_credentials()
                    self.model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
                    self.model.save()
                    return

            if self.state == CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT:
                if AccountPrototype.get_by_email(self.model.new_email):
                    self.model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
                    self.model.comment = 'duplicate email'
                    self.model.save()
                    return

                self.change_credentials()
                self.model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
                self.model.save()
                return

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            traceback_strings = traceback.format_exception(*sys.exc_info())

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
            self.model.comment = u'%s' % traceback_strings
            self.model.save()
