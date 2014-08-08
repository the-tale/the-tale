# coding: utf-8
import uuid

import rels
from rels.django import DjangoEnum

from django.core.urlresolvers import reverse
from django.db import transaction

from the_tale.amqp_environment import environment

from the_tale.common.utils.enum import create_enum
from the_tale.common.utils.decorators import lazy_property

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype


REGISTRATION_TASK_STATE = create_enum('REGISTRATION_TASK_STATE', ( ('UNPROCESSED', 0, u'ожидает обработки'),
                                                                   ('PROCESSED', 1, u'обработкана'),
                                                                   ('UNKNOWN_ERROR', 2, u'неизвестная ошибка'),
                                                                   ('BUNDLE_NOT_FOUND', 3, u'аккаунт не создан'),))

class RegistrationTask(PostponedLogic):

    TYPE = 'registration'

    def __init__(self, account_id, referer, referral_of_id, action_id, state=REGISTRATION_TASK_STATE.UNPROCESSED):
        super(RegistrationTask, self).__init__()
        self.account_id = account_id
        self.referer = referer
        self.referral_of_id = referral_of_id
        self.action_id = action_id
        self.state = state

    def serialize(self):
        return { 'state': self.state,
                 'account_id': self.account_id,
                 'referer': self.referer,
                 'referral_of_id': self.referral_of_id,
                 'action_id': self.action_id}

    @property
    def error_message(self): return REGISTRATION_TASK_STATE._CHOICES[self.state][1]

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

    def get_unique_nick(self):
        return uuid.uuid4().hex[:AccountPrototype._model_class.MAX_NICK_LENGTH]

    def process(self, main_task):
        from the_tale.accounts.logic import register_user, REGISTER_USER_RESULT
        from the_tale.game.models import Bundle

        with transaction.atomic():

            result, account_id, bundle_id = register_user(nick=self.get_unique_nick(), referer=self.referer, referral_of_id=self.referral_of_id, action_id=self.action_id)

            if result != REGISTER_USER_RESULT.OK:
                main_task.comment = 'unknown error'
                self.state = REGISTRATION_TASK_STATE.UNKNOWN_ERROR
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not Bundle.objects.filter(id=bundle_id).exists():
            main_task.comment = 'bundle %d does not found' % bundle_id
            self.state = REGISTRATION_TASK_STATE.BUNDLE_NOT_FOUND
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        environment.workers.supervisor.cmd_register_new_account(account_id)

        self.state = REGISTRATION_TASK_STATE.PROCESSED
        self.account_id = int(account_id)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class CHANGE_CREDENTIALS_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 1, u'необработана'),
                 ('PROCESSED', 2, u'обработана'),
                 ('WRONG_STATE', 3, u'неверное состояние задачи'))


class ChangeCredentials(PostponedLogic):

    TYPE = 'change-credentials'

    def __init__(self, task_id, state=CHANGE_CREDENTIALS_STATE.UNPROCESSED):
        super(ChangeCredentials, self).__init__()
        self.task_id = task_id
        self.state = state if isinstance(state, rels.Record) else CHANGE_CREDENTIALS_STATE.index_value[state]

    def serialize(self):
        return { 'state': self.state.value,
                 'task_id': self.task_id}

    @property
    def processed_data(self): return {'next_url': reverse('accounts:profile:edited') }

    def processed_view(self, resource):
        from the_tale.accounts.logic import force_login_user

        if not self.task.relogin_required:
            return

        force_login_user(resource.request, self.task.account._model)

        # update account settuped on start of this request processing
        resource.account = self.task.account

    @property
    def error_message(self): return self.state.text

    @lazy_property
    def task(self): return ChangeCredentialsTaskPrototype.get_by_id(self.task_id)

    def process(self, main_task):
        if self.state.is_UNPROCESSED:
            self.task.account.change_credentials(new_email=self.task.new_email,
                                                 new_password=self.task.new_password,
                                                 new_nick=self.task.new_nick)
            self.task.mark_as_processed()
            self.state = CHANGE_CREDENTIALS_STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = CHANGE_CREDENTIALS_STATE.WRONG_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


class UPDATE_ACCOUNT_STATE(DjangoEnum):
    records = ( ('UNPROCESSED', 1, u'необработана'),
                 ('PROCESSED', 2, u'обработана'),
                 ('WRONG_STATE', 3, u'неверное состояние задачи'))


class UpdateAccount(PostponedLogic):

    TYPE = 'update-account'

    def __init__(self, account_id, method, data, state=UPDATE_ACCOUNT_STATE.UNPROCESSED):
        super(UpdateAccount, self).__init__()
        self.account_id = account_id
        self.method = method.__name__ if callable(method) else method
        self.data = data
        self.state = state if isinstance(state, rels.Record) else UPDATE_ACCOUNT_STATE.index_value[state]

    def serialize(self):
        return { 'state': self.state.value,
                 'method': self.method,
                 'data': self.data,
                 'account_id': self.account_id}

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id)

    @property
    def error_message(self): return self.state.text

    def process(self, main_task):
        if self.state.is_UNPROCESSED:
            getattr(self.account, self.method)(**self.data)
            self.account.save()
            self.state = UPDATE_ACCOUNT_STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = UPDATE_ACCOUNT_STATE.WRONG_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
