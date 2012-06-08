# -*- coding: utf-8 -*-
import sys
import uuid
import datetime

from django.contrib.auth.hashers import make_password

from dext.utils.decorators import nested_commit_on_success

from accounts.models import Account, RegistrationTask, REGISTRATION_TASK_STATE, ChangeCredentialsTask, CHANGE_CREDENTIALS_TASK_STATE
from accounts.conf import accounts_settings
from accounts.email import ChangeEmailNotification
from accounts.exceptions import AccountsException

class AccountPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, model_id):
        return AccountPrototype(model=Account.objects.get(id=model_id))

    @property
    def id(self): return self.model.id

    @property
    def user(self): return self.model.user

    @property
    def is_fast(self): return self.model.is_fast

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {}

    @classmethod
    def create(cls, user, is_fast):
        account_model = Account.objects.create(user=user, is_fast=is_fast)
        return AccountPrototype(model=account_model)


class RegistrationTaskPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, task_id):
        try:
            model = RegistrationTask.objects.get(id=task_id)
            return cls(model=model)
        except RegistrationTask.DoesNotExist:
            return None
    @classmethod
    def create(cls):
        model = RegistrationTask.objects.create()
        return cls(model=model)

    @property
    def id(self): return self.model.id

    @property
    def state(self): return self.model.state

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = AccountPrototype.get_by_id(self.model.account_id) if self.model.account_id is not None else None
        return self._account

    def get_unique_nick(self):
        return uuid.uuid4().hex

    def process(self, logger):
        from accounts.logic import register_user, REGISTER_USER_RESULT

        from game.workers.environment import workers_environment as game_workers_environment
        from game.models import Bundle

        if self.model.state != REGISTRATION_TASK_STATE.WAITING:
            return

        if self.model.created_at + datetime.timedelta(seconds=accounts_settings.REGISTRATION_TIMEOUT) < datetime.datetime.now():
            self.model.state = REGISTRATION_TASK_STATE.UNPROCESSED
            self.model.comment = 'timeout'
            self.model.save()
            return

        try:
            with nested_commit_on_success():

                result, account_id, bundle_id = register_user(nick=self.get_unique_nick())

                if result == REGISTER_USER_RESULT.OK:
                    pass
                else:
                    self.model.state = REGISTRATION_TASK_STATE.ERROR
                    self.model.comment = 'unknown error'
                    self.model.save()
                    return

            # send command to supervisor after success commit

            if not Bundle.objects.filter(id=bundle_id).exists():
                self.model.state = REGISTRATION_TASK_STATE.ERROR
                self.model.comment = 'bundle %d does not found' % bundle_id
                self.model.save()
                return

            game_workers_environment.supervisor.cmd_register_bundle(bundle_id)

            self.model.state = REGISTRATION_TASK_STATE.PROCESSED
            self.model.comment = 'success'
            self.model.account_id = int(account_id)
            self.model.save()

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.model.state = REGISTRATION_TASK_STATE.ERROR
            self.model.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.model.save()


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
    def create(cls, account, new_email=None, new_password=None):
        old_email = account.user.email
        if account.is_fast and new_email is None:
            raise AccountsException('new_email must be specified for fast account')
        if account.is_fast and new_password is None:
            raise AccountsException('password must be specified for fast account')
        model = ChangeCredentialsTask.objects.create(uuid=uuid.uuid4().hex,
                                                     account=account.model,
                                                     old_email=old_email,
                                                     new_email=new_email,
                                                     new_password=make_password(new_password) if new_password else '')
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
        if self.model.new_password:
            self.account.user.password = self.model.new_password
        if self.model.new_email:
            self.account.user.email = self.model.new_email
        self.account.user.save()

    def request_email_confirmation(self):
        if self.model.new_email is None:
            raise AccountsException('email not specified')
        email = ChangeEmailNotification({'task': self})
        email.send([self.model.new_email])

    @nested_commit_on_success
    def process(self, logger):

        if self.state not in (CHANGE_CREDENTIALS_TASK_STATE.WAITING, CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT):
            return

        if self.model.created_at + datetime.timedelta(seconds=accounts_settings.REGISTRATION_TIMEOUT) < datetime.datetime.now():
            self.model.state = CHANGE_CREDENTIALS_TASK_STATE.UNPROCESSED
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
                self.change_credentials()
                self.model.state = CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
                self.model.save()
                return

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
            self.model.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.model.save()
