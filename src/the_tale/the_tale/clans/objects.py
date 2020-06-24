

import smart_imports

smart_imports.all()


class MetaObjectMixin:

    def meta_object(self):
        return meta_relations.Clan.create_from_object(self)


class Clan(MetaObjectMixin):
    __slots__ = ('id',
                 'created_at',
                 'updated_at',
                 'members_number',
                 'active_members_number',
                 'premium_members_number',
                 'forum_subcategory_id',
                 'name',
                 'abbr',
                 'motto',
                 'description',
                 'might',
                 'statistics_refreshed_at',
                 'state',
                 'linguistics_name')

    def __init__(self,
                 id,
                 created_at,
                 updated_at,
                 members_number,
                 active_members_number,
                 premium_members_number,
                 forum_subcategory_id,
                 name,
                 abbr,
                 motto,
                 description,
                 might,
                 statistics_refreshed_at,
                 state,
                 linguistics_name):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.members_number = members_number
        self.active_members_number = active_members_number
        self.premium_members_number = premium_members_number
        self.forum_subcategory_id = forum_subcategory_id
        self.name = name
        self.abbr = abbr
        self.motto = motto
        self.description = description
        self.might = might
        self.statistics_refreshed_at = statistics_refreshed_at
        self.state = state
        self.linguistics_name = linguistics_name

    @property
    def description_html(self):
        return bbcode_renderers.default.render(self.description)


class Membership:
    __slots__ = ('clan_id', 'account_id', 'role', 'created_at', 'updated_at')

    def __init__(self, clan_id, account_id, role, created_at, updated_at):
        self.clan_id = clan_id
        self.account_id = account_id
        self.role = role
        self.created_at = created_at
        self.updated_at = updated_at

    def is_freezed(self):
        can_change_role_after = self.updated_at + datetime.timedelta(days=conf.settings.RECRUITE_FREEZE_PERIOD)
        return self.role.is_RECRUIT and datetime.datetime.now() < can_change_role_after

    def freeze_delta(self):
        return (self.updated_at +
                datetime.timedelta(days=conf.settings.RECRUITE_FREEZE_PERIOD) -
                datetime.datetime.now())


class MembershipRequest:
    __slots__ = ('id',
                 'created_at',
                 'updated_at',
                 'clan_id',
                 'account_id',
                 'initiator_id',
                 'text',
                 'type')

    def __init__(self, id, created_at, updated_at, clan_id, account_id, initiator_id, text, type):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.clan_id = clan_id
        self.account_id = account_id
        self.initiator_id = initiator_id
        self.text = text
        self.type = type

    @property
    def text_html(self):
        return bbcode_renderers.default.render(self.text)


def _construct_member_permission_checker(permission):
    def method(self, membership):
        return self._check_member_permission(permission,
                                             member_clan_id=membership.clan_id,
                                             member_role=membership.role)
    return method


def _construct_static_permission_checker(permission):
    def method(self):
        return self._check_static_permission(permission)
    return method


class OperationsMetaClass(type):

    def __new__(cls, name, bases, namespace, **kwds):
        for permission in relations.PERMISSION.records:

            if permission.on_member:
                method = _construct_member_permission_checker(permission)
            else:
                method = _construct_static_permission_checker(permission)

            method_name = 'can_{}'.format(permission.name.lower())

            if method_name in namespace:
                method_name = '_{}'.format(method_name)

            method.__name__ = method_name

            namespace[method_name] = method

        return super().__new__(cls, name, bases, dict(namespace))


class OperationsRights(metaclass=OperationsMetaClass):
    __slots__ = ('clan_id', 'initiator_role', 'is_moderator')

    def __init__(self, clan_id, initiator_role, is_moderator):
        self.clan_id = clan_id
        self.initiator_role = initiator_role
        self.is_moderator = is_moderator

    def _check_static_permission(self, permission):
        if permission.on_member:
            raise exceptions.NotStaticPermission(permission=permission)

        if self.clan_id is None:
            return False

        if self.is_moderator:
            return True

        if self.initiator_role is None:
            return False

        return permission in self.initiator_role.permissions

    def _check_member_permission(self, permission, member_clan_id, member_role):
        if not permission.on_member:
            raise exceptions.NotOnMemberPermission(permission=permission)

        if member_role is None:
            return False

        if member_clan_id is None:
            return False

        if self.clan_id != member_clan_id:
            return False

        if self.is_moderator:
            return True

        if self.initiator_role is None:
            return False

        if self.initiator_role.priority >= member_role.priority:
            return False

        return permission in self.initiator_role.permissions

    def can_edit_member(self, membership):
        return (self.can_change_role(membership) or
                self.can_remove_member(membership) or
                self.can_change_owner(membership))

    def can_change_role(self, membership):
        result = self._can_change_role(membership)

        if result:
            result = not membership.role.is_MASTER

        if result:
            # проверка важна для предотвращения выполнения заданий эмиссаров ботами
            result = not membership.is_freezed()

        return result

    def can_change_owner(self, membership):
        return self._can_change_owner(membership) and self.can_change_role(membership)

    def change_role_candidates(self):
        if self.is_moderator:
            return [role for role in relations.MEMBER_ROLE.records
                    if not role.is_MASTER]

        return [role for role in relations.MEMBER_ROLE.records
                if role.priority > self.initiator_role.priority and not role.is_MASTER]


class Attributes:
    __slots__ = ('fighters_maximum_level',
                 'emissary_maximum_level',
                 'free_quests_maximum_level',
                 'points_gain_level')

    def __init__(self,
                 fighters_maximum_level,
                 emissary_maximum_level,
                 free_quests_maximum_level,
                 points_gain_level):
        self.fighters_maximum_level = fighters_maximum_level
        self.emissary_maximum_level = emissary_maximum_level
        self.free_quests_maximum_level = free_quests_maximum_level
        self.points_gain_level = points_gain_level

    @property
    def fighters_maximum(self):
        return tt_clans_constants.INITIAL_FIGHTERS_MAXIMUM + self.fighters_maximum_level

    @property
    def emissary_maximum(self):
        return tt_clans_constants.INITIAL_EMISSARY_MAXIMUM + self.emissary_maximum_level

    @property
    def free_quests_maximum(self):
        return tt_clans_constants.INITIAL_FREE_QUESTS_MAXIMUM + self.free_quests_maximum_level

    @property
    def points_gain(self):
        return int(math.ceil((tt_clans_constants.INITIAL_POINTS_GAIN +
                              self.points_gain_level *
                              tt_clans_constants.POINTS_GAIN_INCREMENT_ON_LEVEL_UP) / 24))


class ClanInfo(MetaObjectMixin):
    __slots__ = ('id', 'name', 'linguistics_name', 'abbr', 'motto', '_utg_name_form__lazy', 'state')

    def __init__(self, id, name, linguistics_name, abbr, motto, state):
        self.id = id
        self.name = name
        self.linguistics_name = linguistics_name
        self.abbr = abbr
        self.motto = motto
        self.state = state

    @utils_decorators.lazy_property
    def utg_name_form(self):
        return utg_words.WordForm(self.linguistics_name)

    def linguistics_variables(self):
        return [('abbr', self.abbr),
                ('motto', self.motto)]

    def linguistics_restrictions(self):
        return ()

    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'abbr': self.abbr,
                'motto': self.motto}
