
import smart_imports

smart_imports.all()


class ClanPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Clan
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'members_number',
                 'forum_subcategory_id')
    _bidirectional = ('name', 'abbr', 'motto', 'description')
    _get_by = ('id',)

    @property
    def description_html(self):
        return utils_bbcode.render(self.description)

    @classmethod
    def get_forum_subcategory_caption(cls, clan_name):
        return 'Раздел гильдии «%s»' % clan_name

    @utils_decorators.lazy_property
    def forum_subcategory(self):
        return forum_prototypes.SubCategoryPrototype.get_by_id(self.forum_subcategory_id)

    @classmethod
    @django_transaction.atomic
    def create(cls, owner, abbr, name, motto, description):

        forum_category = forum_prototypes.CategoryPrototype.get_by_slug(conf.settings.FORUM_CATEGORY_SLUG)

        subcategory_order = forum_prototypes.SubCategoryPrototype._db_filter(category=forum_category.id).aggregate(django_models.Max('order'))['order__max']
        if subcategory_order is None:
            subcategory_order = 0
        else:
            subcategory_order += 1

        forum_subcategory = forum_prototypes.SubCategoryPrototype.create(category=forum_category,
                                                                         caption=cls.get_forum_subcategory_caption(name),
                                                                         order=subcategory_order,
                                                                         restricted=True)

        clan_model = cls._model_class.objects.create(name=name,
                                                     abbr=abbr,
                                                     motto=motto,
                                                     description=description,
                                                     members_number=1,
                                                     forum_subcategory=forum_subcategory._model)

        clan = cls(clan_model)

        MembershipPrototype.create(owner, clan, role=relations.MEMBER_ROLE.LEADER)

        owner.set_clan_id(clan.id)

        return clan

    @django_transaction.atomic
    def update(self, abbr, name, motto, description):
        self.abbr = abbr
        self.name = name
        self.motto = motto
        self.description = description

        self.forum_subcategory.caption = self.get_forum_subcategory_caption(name)
        self.forum_subcategory.save()

        self.save()

    @django_transaction.atomic
    def add_member(self, account):
        try:
            MembershipPrototype.create(account, self, role=relations.MEMBER_ROLE.MEMBER)
        except django_db_utils.IntegrityError:
            raise exceptions.AddMemberFromClanError(member_id=account.id, clan_id=self.id)

        MembershipRequestPrototype._db_filter(account_id=account.id).delete()

        account.set_clan_id(self.id)

        self._model.members_number = MembershipPrototype._db_filter(clan_id=self.id).count()
        self.save()

    @django_transaction.atomic
    def remove_member(self, account):
        membership = MembershipPrototype.get_by_account_id(account.id)
        if membership is None:
            raise exceptions.RemoveNotMemberFromClanError(member_id=account.id, clan_id=self.id)
        if membership.clan_id != self.id:
            raise exceptions.RemoveMemberFromWrongClanError(member_id=account.id, clan_id=self.id)
        if membership.role.is_LEADER:
            raise exceptions.RemoveLeaderFromClanError(member_id=account.id, clan_id=self.id)

        account.set_clan_id(None)

        membership.remove()

        self._model.members_number = MembershipPrototype._db_filter(clan_id=self.id).count()
        self.save()

    def create_remove_member_message(self, initiator, removed_account):
        message = '''
Игрок %(clan_leader_link)s исключил вас из гильдии %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
            'clan_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:clans:show', self.id), self.name)}

        personal_messages_logic.send_message(sender_id=initiator.id,
                                             recipients_ids=[removed_account.id],
                                             body=message)

    def save(self):
        self._model.save()

    @django_transaction.atomic
    def remove(self):
        for membership_model in MembershipPrototype._db_filter(clan_id=self.id):
            membership = MembershipPrototype(model=membership_model)
            membership.remove()

        forum_prototypes.SubCategoryPrototype.get_by_id(self.forum_subcategory_id).delete()

        self._model.delete()

    def get_leader(self):
        return accounts_prototypes.AccountPrototype.get_by_id(MembershipPrototype._model_class.objects.get(clan_id=self.id, role=relations.MEMBER_ROLE.LEADER).account_id)


class MembershipPrototype(utils_prototypes.BasePrototype):
    _model_class = models.Membership
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'role')
    _bidirectional = ()
    _get_by = ('clan_id', 'account_id')

    @classmethod
    @django_transaction.atomic
    def create(cls, account, clan, role):
        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                role=role)
        forum_prototypes.PermissionPrototype.create(account, forum_prototypes.SubCategoryPrototype.get_by_id(clan.forum_subcategory_id))
        return cls(model)

    def remove(self):
        forum_prototypes.PermissionPrototype.get_for(account_id=self.account_id, subcategory_id=ClanPrototype.get_by_id(self.clan_id).forum_subcategory_id).remove()
        self._model.delete()


class MembershipRequestPrototype(utils_prototypes.BasePrototype):
    _model_class = models.MembershipRequest
    _readonly = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'initiator_id',
                 'text')
    _bidirectional = ('type',)
    _get_by = ('id', 'clan_id', 'account_id')

    @classmethod
    def get_for(cls, clan_id, account_id):
        try:
            return cls(model=cls._model_class.objects.get(clan_id=clan_id, account_id=account_id))
        except cls._model_class.DoesNotExist:
            return None

    @utils_decorators.lazy_property
    def account(self): return accounts_prototypes.AccountPrototype.get_by_id(self.account_id)

    @utils_decorators.lazy_property
    def clan(self): return ClanPrototype.get_by_id(self.clan_id)

    def create_invite_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s предлагает вам вступить в гильдию %(clan_link)s:

%(text)s

----------
принять или отклонить предложение вы можете на этой странице: %(invites_link)s
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
            'text': self.text,
            'clan_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name),
            'invites_link': '[url="%s"]Приглашения в гильдию [/url]' % dext_urls.full_url('https', 'accounts:clans:membership:for-account')}

        personal_messages_logic.send_message(sender_id=initiator.id,
                                             recipients_ids=[self.account.id],
                                             body=message)

    def create_request_message(self, initiator):
        message = '''
Игрок %(account)s просит принять его в вашу гильдию:

%(text)s

----------
принять или отклонить предложение вы можете на этой странице: %(invites_link)s
''' % {'account': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', self.account.id), self.account.nick_verbose),
            'text': self.text,
            'invites_link': '[url="%s"]Заявки в гильдию[/url]' % dext_urls.full_url('https', 'accounts:clans:membership:for-clan')}

        personal_messages_logic.send_message(sender_id=initiator.id,
                                             recipients_ids=[self.clan.get_leader().id],
                                             body=message)

    def create_accept_request_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s принял вас в гильдию %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
            'clan_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name)}

        personal_messages_logic.send_message(sender_id=initiator.id,
                                             recipients_ids=[self.account.id],
                                             body=message)

    def create_reject_request_message(self, initiator):
        message = '''
Игрок %(clan_leader_link)s отказал вам в принятии в гильдию %(clan_link)s.
''' % {'clan_leader_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:show', initiator.id), initiator.nick_verbose),
            'clan_link': '[url="%s"]%s[/url]' % (dext_urls.full_url('https', 'accounts:clans:show', self.clan.id), self.clan.name)}

        personal_messages_logic.send_message(sender_id=initiator.id,
                                             recipients_ids=[self.account.id],
                                             body=message)

    @classmethod
    @django_transaction.atomic
    def create(cls, initiator, account, clan, text, type):

        model = cls._model_class.objects.create(clan=clan._model,
                                                account=account._model,
                                                initiator=initiator._model,
                                                type=type,
                                                text=text)
        return cls(model)

    @classmethod
    def get_for_clan(cls, clan_id):
        models = cls._db_filter(clan_id=clan_id, type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_ACCOUNT).order_by('created_at')
        return [cls(model=model) for model in models]

    @classmethod
    def get_for_account(cls, account_id):
        models = cls._db_filter(account_id=account_id, type=relations.MEMBERSHIP_REQUEST_TYPE.FROM_CLAN).order_by('created_at')
        return [cls(model=model) for model in models]

    @property
    def text_html(self):
        return utils_bbcode.render(self.text)

    def remove(self):
        self._model.delete()
