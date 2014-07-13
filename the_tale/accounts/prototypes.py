# coding: utf-8
import sys
import uuid
import datetime
import traceback
import random

from urlparse import urlparse

from django.contrib.auth.hashers import make_password
from django.db import models, transaction

from dext.utils.urls import full_url
from dext.utils import s11n

from the_tale.common.postponed_tasks import PostponedTaskPrototype
from the_tale.common.utils.logic import verbose_timedelta

from the_tale.common.utils.password import generate_password
from the_tale.common.utils.prototypes import BasePrototype
from the_tale.common.utils.decorators import lazy_property

from the_tale.accounts.models import Account, ChangeCredentialsTask, Award, ResetPasswordTask, RandomPremiumRequest
from the_tale.accounts.conf import accounts_settings
from the_tale.accounts import exceptions
from the_tale.accounts import relations


class AccountPrototype(BasePrototype): #pylint: disable=R0904
    _model_class = Account
    _readonly = ('id',
                 'is_authenticated',
                 'created_at',
                 'is_staff',
                 'is_superuser',
                 'is_bot',
                 'has_perm',
                 'premium_end_at',
                 'active_end_at',
                 'ban_game_end_at',
                 'ban_forum_end_at',
                 'referer',
                 'referer_domain',
                 'referral_of_id',
                 'action_id',
                 'clan_id',
                 'referrals_number',
                 'might')
    _bidirectional = ('is_fast', 'nick', 'email', 'last_news_remind_time', 'personal_messages_subscription')
    _get_by = ('id', 'email', 'nick')

    @property
    def account_id(self): return self.id

    @classmethod
    def live_query(cls): return cls._model_class.objects.filter(is_fast=False, is_bot=False).select_related('clan')

    @lazy_property
    def is_system_user(self):
        return self.nick == accounts_settings.SYSTEM_USER_NICK

    @lazy_property
    def is_developer(self):
        return self.id in accounts_settings.DEVELOPERS_IDS

    @lazy_property
    def permanent_purchases(self):
        from the_tale.accounts.payments.logic import PermanentRelationsStorage
        return PermanentRelationsStorage.deserialize(s11n.from_json(self._model.permanent_purchases))

    @property
    def nick_verbose(self):
        if self._model.nick.startswith(accounts_settings.RESET_NICK_PREFIX):
            return accounts_settings.RESET_NICK_PREFIX
        return self._model.nick if not self._model.is_fast else u'Игрок'

    def update_last_news_remind_time(self):
        current_time = datetime.datetime.now()
        self._model_class.objects.filter(id=self.id).update(last_news_remind_time=current_time)
        self._model.last_news_remind_time = current_time

    def update_referrals_number(self):
        self._model.referrals_number = self._model_class.objects.filter(referral_of_id=self.id, is_fast=False).count()

    def update_settings(self, form):
        self._model_class.objects.filter(id=self.id).update(personal_messages_subscription=form.c.personal_messages_subscription)
        self._model.personal_messages_subscription = form.c.personal_messages_subscription

    def prolong_premium(self, days):
        from the_tale.game.heroes.prototypes import HeroPrototype

        self._model.premium_end_at = max(self.premium_end_at, datetime.datetime.now()) + datetime.timedelta(days=days)

        HeroPrototype.get_by_account_id(self.id).cmd_update_with_account_data(self)

    @property
    def is_premium(self): return self.premium_end_at > datetime.datetime.now()

    @property
    def is_ban_game(self): return self.ban_game_end_at > datetime.datetime.now()

    @property
    def is_ban_forum(self): return self.ban_forum_end_at > datetime.datetime.now()

    @property
    def is_ban_any(self): return self.is_ban_game or self.is_ban_forum

    def ban_game(self, days):
        from the_tale.game.heroes.prototypes import HeroPrototype

        end_time = datetime.datetime.now() + datetime.timedelta(days=days)
        self._model_class.objects.filter(id=self.id).update(ban_game_end_at=end_time)
        self._model.ban_game_end_at = end_time

        HeroPrototype.get_by_account_id(self.id).cmd_update_with_account_data(self)

    def ban_forum(self, days):
        end_time = datetime.datetime.now() + datetime.timedelta(days=days)
        self._model_class.objects.filter(id=self.id).update(ban_forum_end_at=end_time)
        self._model.ban_forum_end_at = end_time

    @classmethod
    def send_premium_expired_notifications(cls):
        current_time = datetime.datetime.now()
        accounts_query = cls._model_class.objects.filter(premium_end_at__gt=current_time,
                                                         premium_end_at__lt=current_time + accounts_settings.PREMIUM_EXPIRED_NOTIFICATION_IN,
                                                         premium_expired_notification_send_at__lt=current_time-accounts_settings.PREMIUM_EXPIRED_NOTIFICATION_IN)
        for account_model in accounts_query:
            account = cls(model=account_model)
            account.notify_about_premium_expiration()

        accounts_query.update(premium_expired_notification_send_at=current_time)

    def notify_about_premium_expiration(self):
        from the_tale.accounts.personal_messages.prototypes import MessagePrototype as PersonalMessagePrototype
        from the_tale.accounts.logic import get_system_user

        current_time = datetime.datetime.now()

        message = u'''
До окончания подписки осталось: %(verbose_timedelta)s.

Вы можете продлить подписку на странице нашего %(shop_link)s.
''' % {'verbose_timedelta': verbose_timedelta(self.premium_end_at - current_time),
       'shop_link': u'[url="%s"]магазина[/url]' % full_url('http', 'accounts:payments:shop')}

        PersonalMessagePrototype.create(get_system_user(), self, message)

    @lazy_property
    def bank_account(self):
        from the_tale.bank.prototypes import AccountPrototype as BankAccountPrototype
        from the_tale.bank.relations import ENTITY_TYPE, CURRENCY_TYPE

        bank_account = BankAccountPrototype.get_for(entity_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                    entity_id=self.id,
                                                    currency=CURRENCY_TYPE.PREMIUM,
                                                    null_object=True)

        if accounts_settings.CREATE_DEBUG_BANK_ACCOUNTS and bank_account.is_fake:
            bank_account = BankAccountPrototype.get_for_or_create(entity_type=ENTITY_TYPE.GAME_ACCOUNT,
                                                                  entity_id=self.id,
                                                                  currency=CURRENCY_TYPE.PREMIUM)
            bank_account.amount = 10000
            bank_account.save()

        return bank_account

    @property
    def new_messages_number(self): return self._model.new_messages_number
    def reset_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=0)
        self._model.new_messages_number = 0
    def increment_new_messages_number(self):
        Account.objects.filter(id=self.id).update(new_messages_number=models.F('new_messages_number')+1)
        self._model.new_messages_number = self._model.new_messages_number + 1

    def set_clan_id(self, clan_id):
        Account.objects.filter(id=self.id).update(clan=clan_id)
        self._model.clan_id = clan_id

    @lazy_property
    def clan(self):
        from the_tale.accounts.clans.prototypes import ClanPrototype

        if self.clan_id is None:
            return None

        return ClanPrototype(model=self._model.clan)

    def set_might(self, might):
        from the_tale.accounts.achievements.relations import ACHIEVEMENT_TYPE
        from the_tale.accounts.achievements.storage import achievements_storage

        Account.objects.filter(id=self.id).update(might=might)

        with achievements_storage.verify(type=ACHIEVEMENT_TYPE.KEEPER_MIGHT, object=self):
            self._model.might = might

    def check_password(self, password):
        return self._model.check_password(password)

    def change_credentials(self, new_email=None, new_password=None, new_nick=None):
        from the_tale.game.heroes.prototypes import HeroPrototype
        from the_tale.accounts.workers.environment import workers_environment

        if new_password:
            self._model.password = new_password
        if new_email:
            self._model.email = new_email
        if new_nick:
            self.nick = new_nick

        old_fast = self.is_fast # pylint: disable=E0203

        self.is_fast = False

        self.save()

        if old_fast:
            HeroPrototype.get_by_account_id(self.id).cmd_update_with_account_data(self)

            if self.referral_of_id is not None:
                workers_environment.accounts_manager.cmd_run_account_method(account_id=self.referral_of_id,
                                                                            method_name=self.update_referrals_number.__name__,
                                                                            data={})



    ###########################################
    # Object operations
    ###########################################

    def can_be_removed(self):
        return self.is_fast

    def remove(self):
        return self._model.delete()

    def save(self):
        self._model.permanent_purchases = s11n.to_json(self.permanent_purchases.serialize())
        self._model.save(force_update=True)

    @classmethod
    def _next_active_end_at(cls):
        return datetime.datetime.now() + datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)

    @property
    def is_update_active_state_needed(self):
        return datetime.datetime.now() + datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT - accounts_settings.ACTIVE_STATE_REFRESH_PERIOD) > self.active_end_at

    def update_active_state(self):
        from the_tale.game.heroes.prototypes import HeroPrototype

        self._model.active_end_at = self._next_active_end_at()
        self.save()

        HeroPrototype.get_by_account_id(self.id).cmd_update_with_account_data(self)

    @property
    def was_in_game_at(self): return self.active_end_at - datetime.timedelta(seconds=accounts_settings.ACTIVE_STATE_TIMEOUT)

    @property
    def is_active(self): return self.active_end_at > datetime.datetime.now()

    def get_achievement_account_id(self):
        return self.id

    def get_achievement_type_value(self, achievement_type):
        from the_tale.game.bills.prototypes import BillPrototype, VotePrototype

        if achievement_type.is_POLITICS_ACCEPTED_BILLS:
            return BillPrototype.accepted_bills_count(self.id)
        elif achievement_type.is_POLITICS_VOTES_TOTAL:
            return VotePrototype.votes_count(self.id)
        elif achievement_type.is_POLITICS_VOTES_FOR:
            return VotePrototype.votes_for_count(self.id)
        elif achievement_type.is_POLITICS_VOTES_AGAINST:
            return VotePrototype.votes_against_count(self.id)
        elif achievement_type.is_KEEPER_MIGHT:
            return self.might

        raise exceptions.UnkwnownAchievementTypeError(achievement_type=achievement_type)


    @classmethod
    def create(cls, nick, email, is_fast, password=None, referer=None, referral_of=None, action_id=None, is_bot=False):
        referer_domain = None
        if referer:
            referer_info = urlparse(referer)
            referer_domain = referer_info.netloc

        return AccountPrototype(model=Account.objects.create_user(nick=nick,
                                                                  email=email,
                                                                  is_fast=is_fast,
                                                                  is_bot=is_bot,
                                                                  password=password,
                                                                  active_end_at=cls._next_active_end_at(),
                                                                  referer=referer,
                                                                  referer_domain=referer_domain,
                                                                  referral_of=referral_of._model if referral_of else None,
                                                                  action_id=action_id))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self._model == other._model



class ChangeCredentialsTaskPrototype(BasePrototype):
    _model_class = ChangeCredentialsTask
    _readonly = ('id', 'uuid', 'state', 'new_email', 'new_nick', 'new_password', 'relogin_required')
    _bidirectional = ()
    _get_by = ('id', 'uuid')

    @classmethod
    def create(cls, account, new_email=None, new_password=None, new_nick=None, relogin_required=False):
        old_email = account.email
        if account.is_fast and new_email is None:
            raise exceptions.MailNotSpecifiedForFastAccountError()
        if account.is_fast and new_password is None:
            raise exceptions.PasswordNotSpecifiedForFastAccountError()
        if account.is_fast and new_nick is None:
            raise exceptions.NickNotSpecifiedForFastAccountError()

        if old_email == new_email:
            new_email = None

        model = ChangeCredentialsTask.objects.create(uuid=uuid.uuid4().hex,
                                                     account=account._model,
                                                     old_email=old_email,
                                                     new_email=new_email,
                                                     new_password=make_password(new_password) if new_password else '',
                                                     state=relations.CHANGE_CREDENTIALS_TASK_STATE.WAITING,
                                                     new_nick=new_nick,
                                                     relogin_required=relogin_required)
        return cls(model=model)

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self._model.account_id)

    @property
    def email_changed(self):
        return self._model.new_email is not None and (self._model.old_email != self._model.new_email)

    def change_credentials(self):
        from the_tale.accounts.postponed_tasks import ChangeCredentials
        from the_tale.accounts.workers.environment import workers_environment

        change_credentials_task = ChangeCredentials(task_id=self.id)
        task = PostponedTaskPrototype.create(change_credentials_task)

        workers_environment.accounts_manager.cmd_task(task.id)

        return task

    def request_email_confirmation(self):
        from the_tale.post_service.prototypes import MessagePrototype
        from the_tale.post_service.message_handlers import ChangeEmailNotificationHandler

        if self._model.new_email is None:
            raise exceptions.NewEmailNotSpecifiedError()

        MessagePrototype.create(ChangeEmailNotificationHandler(task_id=self.id), now=True)

    @property
    def has_already_processed(self):
        return not (self.state.is_WAITING or self.state.is_EMAIL_SENT)

    def mark_as_processed(self):
        self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.PROCESSED
        self._model.save()

    def process(self, logger):

        if self.has_already_processed:
            return

        if self._model.created_at + datetime.timedelta(seconds=accounts_settings.CHANGE_EMAIL_TIMEOUT) < datetime.datetime.now():
            self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.TIMEOUT
            self._model.comment = 'timeout'
            self._model.save()
            return

        try:
            if self.state.is_WAITING:
                if self.email_changed:
                    self.request_email_confirmation()
                    self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.EMAIL_SENT
                    self._model.save()
                    return
                else:
                    postponed_task = self.change_credentials()
                    self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING
                    self._model.save()
                    return postponed_task

            if self.state.is_EMAIL_SENT:
                if AccountPrototype.get_by_email(self._model.new_email):
                    self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR
                    self._model.comment = 'duplicate email'
                    self._model.save()
                    return

                postponed_task = self.change_credentials()
                self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.CHANGING
                self._model.save()
                return postponed_task

        except Exception, e: # pylint: disable=W0703
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            traceback_strings = traceback.format_exception(*sys.exc_info())

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self._model.state = relations.CHANGE_CREDENTIALS_TASK_STATE.ERROR
            self._model.comment = u'%s' % traceback_strings
            self._model.save()


class AwardPrototype(BasePrototype):
    _model_class = Award
    _readonly = ('id', 'type')
    _bidirectional = ()
    _get_by = ('id',)


    @classmethod
    def create(cls, description, type, account): # pylint: disable=W0622
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
        from the_tale.post_service.prototypes import MessagePrototype
        from the_tale.post_service.message_handlers import ResetPasswordHandler

        model = cls._model_class.objects.create(account=account._model,
                                                uuid=uuid.uuid4().hex)
        prototype = cls(model=model)

        MessagePrototype.create(ResetPasswordHandler(account_id=account.id, task_uuid=prototype.uuid), now=True)

        return prototype

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self._model.account_id)

    def process(self, logger):

        new_password = generate_password(len_=accounts_settings.RESET_PASSWORD_LENGTH)

        task = ChangeCredentialsTaskPrototype.create(account=self.account,
                                                     new_password=new_password)

        # here postponed task is created, but we will not wait for it processed, just  display new password
        task.process(logger)

        self._model.is_processed = True
        self.save()

        return new_password

    def save(self):
        self._model.save()


class RandomPremiumRequestPrototype(BasePrototype):
    _model_class = RandomPremiumRequest
    _readonly = ('days', 'id')
    _bidirectional = ('state', 'initiator_id', 'receiver_id')
    _get_by = ()

    MESSAGE = u'''
Поздравляем!

Один из игроков подарил вам подписку на %(days)s дней!
'''


    @classmethod
    def create(cls, initiator_id, days):
        model = cls._model_class.objects.create(initiator_id=initiator_id,
                                                days=days,
                                                state=relations.RANDOM_PREMIUM_REQUEST_STATE.WAITING)
        prototype = cls(model=model)

        return prototype

    @classmethod
    def get_unprocessed(cls):
        try:
            return cls(model=cls._db_filter(state=relations.RANDOM_PREMIUM_REQUEST_STATE.WAITING).order_by('id')[0])
        except IndexError:
            return None

    def process(self):
        from the_tale.accounts.personal_messages.prototypes import MessagePrototype as PersonalMessagePrototype
        from the_tale.accounts.logic import get_system_user

        accounts_ids = AccountPrototype.live_query().filter(is_fast=False,
                                                            created_at__lt=datetime.datetime.now() - accounts_settings.RANDOM_PREMIUM_CREATED_AT_BARRIER,
                                                            active_end_at__gt=datetime.datetime.now(),
                                                            premium_end_at__lt=datetime.datetime.now()).exclude(id=self.initiator_id).values_list('id', flat=True)

        if not accounts_ids:
            return False

        account = AccountPrototype.get_by_id(random.choice(accounts_ids))

        with transaction.atomic():
            account.prolong_premium(self.days)
            account.save()

            PersonalMessagePrototype.create(get_system_user(), account, self.MESSAGE % {'days': self.days})

            self.receiver_id = account.id
            self.state = relations.RANDOM_PREMIUM_REQUEST_STATE.PROCESSED
            self.save()

        return True
