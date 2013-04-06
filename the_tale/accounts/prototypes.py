# coding: utf-8
import sys
import uuid
import datetime
import traceback

from django.contrib.auth.hashers import make_password
from django.db import models

from dext.utils.decorators import nested_commit_on_success

from common.utils.password import generate_password
from common.utils.prototypes import BasePrototype
from common.utils.decorators import lazy_property

from accounts.models import Account, ChangeCredentialsTask, CHANGE_CREDENTIALS_TASK_STATE, Award, ResetPasswordTask
from accounts.conf import accounts_settings
from accounts.exceptions import AccountsException

class AccountPrototype(BasePrototype):
    _model_class = Account
    _readonly = ('id', 'is_authenticated', 'created_at', 'is_staff', 'is_active', 'is_superuser', 'has_perm')
    _bidirectional = ('is_fast', 'nick', 'email', 'last_news_remind_time')
    _get_by = ('id', 'email', 'nick')

    @property
    def nick_verbose(self): return self._model.nick if not self._model.is_fast else u'Игрок'

    @property
    def new_messages_number(self): return self._model.new_messages_number
    def reset_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=0)
        self._model.new_messages_number = 0
    def increment_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=models.F('new_messages_number')+1)
        self._model.new_messages_number = self._model.new_messages_number + 1

    def reset_password(self):
        new_password = generate_password(len_=accounts_settings.RESET_PASSWORD_LENGTH)
        self._model.set_password(new_password)
        self._model.save()

        return new_password

    def check_password(self, password):
        return self._model.check_password(password)

    @nested_commit_on_success
    def change_credentials(self, new_email=None, new_password=None, new_nick=None):
        from game.heroes.prototypes import HeroPrototype
        from game.workers.environment import workers_environment as game_workers_environment

        if new_password:
            self._model.password = new_password
        if new_email:
            self._model.email = new_email
        if new_nick:
            self.nick = new_nick

        if self.is_fast:
            game_workers_environment.supervisor.cmd_mark_hero_as_not_fast(self.id, HeroPrototype.get_by_account_id(self.id).id)

        self.is_fast = False

        self.save()

    ###########################################
    # Object operations
    ###########################################

    def can_be_removed(self):
        return self.is_fast

    def remove(self):
        return self._model.delete()

    def save(self): self._model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {}

    @classmethod
    def create(cls, nick, email, is_fast, password=None):
        return AccountPrototype(model=Account.objects.create_user(nick=nick, email=email, is_fast=is_fast, password=password))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._model == other._model



class ChangeCredentialsTaskPrototype(BasePrototype):
    _model_class = ChangeCredentialsTask
    _readonly = ('id', 'uuid', 'state')
    _bidirectional = ()
    _get_by = ('id', 'uuid')

    @classmethod
    def create(cls, account, new_email=None, new_password=None, new_nick=None):
        old_email = account.email
        if account.is_fast and new_email is None:
            raise AccountsException('new_email must be specified for fast account')
        if account.is_fast and new_password is None:
            raise AccountsException('password must be specified for fast account')
        if account.is_fast and new_nick is None:
            raise AccountsException('nick must be specified for fast account')

        if old_email == new_email:
            new_email = None

        model = ChangeCredentialsTask.objects.create(uuid=uuid.uuid4().hex,
                                                     account=account._model,
                                                     old_email=old_email,
                                                     new_email=new_email,
                                                     new_password=make_password(new_password) if new_password else '',
                                                     new_nick=new_nick)
        return cls(model=model)

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self._model.account_id)

    @property
    def email_changed(self):
        return self._model.new_email is not None and (self._model.old_email != self._model.new_email)

    def change_credentials(self):
        self.account.change_credentials(new_email=self._model.new_email, new_password=self._model.new_password, new_nick=self._model.new_nick)

    def request_email_confirmation(self):
        from post_service.prototypes import MessagePrototype
        from post_service.message_handlers import ChangeEmailNotificationHandler

        if self._model.new_email is None:
            raise AccountsException('email not specified')

        MessagePrototype.create(ChangeEmailNotificationHandler(task_id=self.id), now=True)


    @property
    def has_already_processed(self):
        return self.state not in (CHANGE_CREDENTIALS_TASK_STATE.WAITING, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT)

    @nested_commit_on_success
    def process(self, logger):

        if self.has_already_processed:
            return

        if self._model.created_at + datetime.timedelta(seconds=accounts_settings.CHANGE_EMAIL_TIMEOUT) < datetime.datetime.now():
            self._model.state = CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT
            self._model.comment = 'timeout'
            self._model.save()
            return

        try:
            if self.state == CHANGE_CREDENTIALS_TASK_STATE.WAITING:
                if self.email_changed:
                    self.request_email_confirmation()
                    self._model.state = CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT
                    self._model.save()
                    return
                else:
                    self.change_credentials()
                    self._model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
                    self._model.save()
                    return

            if self.state == CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT:
                if AccountPrototype.get_by_email(self._model.new_email):
                    self._model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
                    self._model.comment = 'duplicate email'
                    self._model.save()
                    return

                self.change_credentials()
                self._model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
                self._model.save()
                return

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            traceback_strings = traceback.format_exception(*sys.exc_info())

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self._model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
            self._model.comment = u'%s' % traceback_strings
            self._model.save()


class AwardPrototype(BasePrototype):
    _model_class = Award
    _readonly = ('id', 'type')
    _bidirectional = ()
    _get_by = ('id',)


    @classmethod
    def create(cls, description, type, account):
        return cls(model=Award.objects.create(description=description,
                                              type=type,
                                              account=account._model) )


class ResetPasswordTaskPrototype(BasePrototype):
    _model_class = ResetPasswordTask
    _readonly = ('uuid', 'is_processed')
    _bidirectional = ()
    _get_by = ('uuid',)

    @property
    def is_time_expired(self): return datetime.datetime.now() > self._model.created_at + datetime.timedelta(seconds=accounts_settings.RESET_PASSWORD_TASK_LIVE_TIME)

    @classmethod
    def create(cls, account):
        from post_service.prototypes import MessagePrototype
        from post_service.message_handlers import ResetPasswordHandler

        model = cls._model_class.objects.create(account=account._model,
                                                uuid=uuid.uuid4().hex)
        prototype = cls(model=model)

        MessagePrototype.create(ResetPasswordHandler(account_id=account.id, task_uuid=prototype.uuid), now=True)

        return prototype

    def process(self):
        account = AccountPrototype.get_by_id(self._model.account_id)
        new_password = account.reset_password()
        self._model.is_processed = True
        self.save()

        return new_password

    def save(self):
        self._model.save()
