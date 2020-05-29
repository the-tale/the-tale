
import smart_imports

smart_imports.all()


class AccountManager(django_auth_models.BaseUserManager):

    @classmethod
    def normalize_email(cls, email):
        email = super(AccountManager, cls).normalize_email(email)
        return email if email else None

    def create_user(self, nick, email, is_fast=None, password=None, active_end_at=None, referer=None, referer_domain=None, referral_of=None, action_id=None, is_bot=False, gender=game_relations.GENDER.MALE):

        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email),
                             nick=nick,
                             is_fast=is_fast,
                             active_end_at=active_end_at,
                             referer=referer,
                             referer_domain=referer_domain,
                             is_bot=is_bot,
                             referral_of=referral_of,
                             last_login=datetime.datetime.now(),
                             action_id=action_id,
                             gender=gender)
        account.set_password(password)
        account.save(using=self._db)
        return account

    def create_superuser(self, nick, email, password):
        if not nick:
            raise ValueError('Users must have nick')

        account = self.model(email=self.normalize_email(email),
                             nick=nick,
                             is_fast=False,
                             is_superuser=True,
                             is_staff=True)
        account.set_password(password)
        account.save(using=self._db)
        return account


class Account(django_auth_models.AbstractBaseUser, django_auth_models.PermissionsMixin):

    objects = AccountManager()

    MAX_NICK_LENGTH = 128
    MAX_EMAIL_LENGTH = 254
    MAX_ACTION_LENGTH = 128

    nick = django_models.CharField(null=False, default='', max_length=MAX_NICK_LENGTH, unique=True, db_index=True)

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = django_models.DateTimeField(auto_now=True, db_index=True)

    removed_at = django_models.DateTimeField(null=True, default=None, blank=True)

    premium_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    active_end_at = django_models.DateTimeField(db_index=True)

    premium_expired_notification_send_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    is_fast = django_models.BooleanField(default=True, db_index=True)
    is_bot = django_models.BooleanField(default=False)

    # duplicate django user email - add unique constraints
    email = django_models.EmailField(max_length=MAX_EMAIL_LENGTH, null=True, unique=True, blank=True)

    gender = rels_django.RelationIntegerField(relation=game_relations.GENDER, relation_column='value')

    cards_receive_mode = rels_django.RelationIntegerField(relation=cards_relations.RECEIVE_MODE,
                                                          relation_column='value',
                                                          default=cards_relations.RECEIVE_MODE.ALL.value)

    last_news_remind_time = django_models.DateTimeField(auto_now_add=True)

    clan = django_models.ForeignKey('clans.Clan', null=True, default=None, related_name='+', on_delete=django_models.SET_NULL)

    is_staff = django_models.BooleanField('staff status', default=False, help_text='Designates whether the user can log into this admin site.')
    is_active = django_models.BooleanField('active', default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')

    personal_messages_subscription = django_models.BooleanField(blank=True, default=True)
    news_subscription = django_models.BooleanField(blank=True, default=True)

    description = django_models.TextField(blank=True, default='')

    ban_game_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))
    ban_forum_end_at = django_models.DateTimeField(db_index=True, default=datetime.datetime.fromtimestamp(0))

    referer_domain = django_models.CharField(max_length=256, null=True, default=None, db_index=True)
    referer = django_models.CharField(max_length=4 * 1024, null=True, default=None)

    referral_of = django_models.ForeignKey('accounts.Account', null=True, blank=True, db_index=True, default=None, on_delete=django_models.SET_NULL)
    referrals_number = django_models.IntegerField(default=0)

    action_id = django_models.CharField(null=True, blank=True, db_index=True, default=None, max_length=MAX_ACTION_LENGTH)

    permanent_purchases = django_models.TextField(default='[]')

    might = django_models.FloatField(default=0.0)
    actual_bills = django_models.TextField(default='[]')

    USERNAME_FIELD = 'nick'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ['nick']
        permissions = (("moderate_account", "Может редактировать аккаунты и т.п."), )

    def __str__(self): return self.nick

    def get_full_name(self): return self.nick

    def get_short_name(self): return self.nick


class Award(django_models.Model):

    account = django_models.ForeignKey(Account, related_name='+', null=False, on_delete=django_models.CASCADE)

    type = rels_django.RelationIntegerField(relation=relations.AWARD_TYPE, relation_column='value', db_index=True)

    description = django_models.TextField(default='', blank=True)

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = django_models.DateTimeField(auto_now=True, db_index=True)


class ResetPasswordTask(django_models.Model):
    account = django_models.ForeignKey(Account, related_name='+', null=False, on_delete=django_models.CASCADE)
    uuid = django_models.CharField(max_length=32)
    created_at = django_models.DateTimeField(auto_now_add=True)
    is_processed = django_models.BooleanField(default=False, db_index=True)


class ChangeCredentialsTask(django_models.Model):
    MAX_COMMENT_LENGTH = 256

    created_at = django_models.DateTimeField(auto_now_add=True, db_index=True)

    updated_at = django_models.DateTimeField(auto_now=True, db_index=True)

    state = rels_django.RelationIntegerField(relation=relations.CHANGE_CREDENTIALS_TASK_STATE, relation_column='value', db_index=True)

    comment = django_models.CharField(max_length=256, blank=True, null=True, default='')

    account = django_models.ForeignKey(Account, related_name='+', on_delete=django_models.CASCADE)

    old_email = django_models.EmailField(max_length=254, null=True)

    new_email = django_models.EmailField(max_length=254, null=True)

    new_password = django_models.TextField(default=None, null=True)  # django password hash

    new_nick = django_models.CharField(default=None, null=True, max_length=Account.MAX_NICK_LENGTH)

    uuid = django_models.CharField(max_length=32, db_index=True)
