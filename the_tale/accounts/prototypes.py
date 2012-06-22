# -*- coding: utf-8 -*-
import sys
import uuid
import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from dext.utils.decorators import nested_commit_on_success

from common.utils.password import generate_password

from accounts.models import Account, RegistrationTask, REGISTRATION_TASK_STATE, ChangeCredentialsTask, CHANGE_CREDENTIALS_TASK_STATE
from accounts.conf import accounts_settings
from accounts.email import ChangeEmailNotification, ResetPasswordNotification
from accounts.exceptions import AccountsException

from game.angels.prototypes import AngelPrototype
from game.bundles import BundlePrototype

class AccountPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, model_id):
        return AccountPrototype(model=Account.objects.get(id=model_id))

    @classmethod
    def get_by_email(cls, email):
        if email is None:
            return None

        try:
            user = User.objects.get(email=email)
            return cls(user.get_profile())
        except User.DoesNotExist:
            return None

    @classmethod
    def get_by_nick(cls, nick):
        if nick is None:
            return None

        try:
            user = User.objects.get(username=nick)
            return cls(user.get_profile())
        except User.DoesNotExist:
            return None

    @property
    def angel(self):
        if not hasattr(self, '_angel'):
            self._angel = AngelPrototype.get_by_account(self)
        return self._angel

    @property
    def id(self): return self.model.id

    @property
    def user(self): return self.model.user

    def get_is_fast(self): return self.model.is_fast
    def set_is_fast(self, value): self.model.is_fast = value
    is_fast = property(get_is_fast, set_is_fast)

    def reset_password(self):
        new_password = generate_password(len_=accounts_settings.RESET_PASSWORD_LENGTH)
        self.user.set_password(new_password)
        self.user.save()
        email = ResetPasswordNotification({'password': new_password})
        email.send([self.user.email])

    @nested_commit_on_success
    def change_credentials(self, new_email=None, new_password=None, new_nick=None):
        if new_password:
            self.user.password = new_password
        if new_email:
            self.user.email = new_email
            self.model.email = new_email
        if new_nick:
            self.user.username = new_nick
        self.is_fast = False

        self.user.save()
        self.save()


    ###########################################
    # Object operations
    ###########################################

    def can_be_removed(self):
        bundle = BundlePrototype.get_by_angel(self.angel)
        return bundle.is_single

    def remove(self):
        registration_task = RegistrationTaskPrototype.get_by_account(self)
        if registration_task:
            registration_task.unbind_from_account()

        self.angel.remove()
        return self.model.delete()

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
    def get_by_account(cls, account):
        try:
            model = RegistrationTask.objects.get(account_id=account.id)
            return cls(model=model)
        except RegistrationTask.DoesNotExist:
            return None

    @classmethod
    def create(cls):
        model = RegistrationTask.objects.create()
        return cls(model=model)

    @classmethod
    def stop_old_tasks(cls):
        RegistrationTask.objects.filter(state=REGISTRATION_TASK_STATE.WAITING).update(state=REGISTRATION_TASK_STATE.ERROR, comment='stop old tasks')

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
        return uuid.uuid4().hex[:30] # 30 - is django user len limitation

    def unbind_from_account(self):
        self.model.comment = u'unbind from account "%s"' % self.account.user.username
        if hasattr(self, '_account'):
            delattr(self, '_account')
        self.model.account = None
        self.model.save()

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

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.model.state = CHANGE_CREDENTIALS_TASK_STATE.ERROR
            self.model.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.model.save()
