import smart_imports

smart_imports.all()


########################################
# processors
########################################

class ClanProcessor(dext_views.ArgumentProcessor):
    URL_NAME = 'clan'
    CONTEXT_NAME = 'current_clan'
    DEFAULT_VALUE = None
    ERROR_MESSAGE = 'Неверный идентификатор гильдии'

    def parse(self, context, raw_value):
        try:
            clan_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        clan = logic.load_clan(clan_id=clan_id)

        if clan is None:
            self.raise_wrong_value()

        return clan


class MembershipRequestProcessor(dext_views.ArgumentProcessor):
    GET_NAME = 'request'
    CONTEXT_NAME = 'membership_request'
    ERROR_MESSAGE = 'Неверный идентификатор запроса'

    ARG_EXPECTED_TYPE = dext_views.ProcessorArgument()

    def parse(self, context, raw_value):
        try:
            request_id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        request = logic.load_request(request_id=request_id)

        if request is None:
            self.raise_wrong_value()

        if self.expected_type is not None and request.type != self.expected_type:
            raise dext_views.ViewError(code='clans.wrong_request_type',
                                       message='Неверный тип запроса на вступление в гильдию')

        if context.current_clan.id != request.clan_id:
            raise dext_views.ViewError(code='clans.not_your_clan_request',
                                       message='Этот запрос относится к другому клану')

        return request


class ClanRightsProcessor(dext_views.BaseViewProcessor):
    ARG_CLAN_ATTRIBUTE = dext_views.ProcessorArgument()

    def preprocess(self, context):
        rights_attribute = self.clan_attribute + '_rights'

        clan = getattr(context, self.clan_attribute, None)

        if clan is None:
            setattr(context, rights_attribute, None)
            return

        setattr(context, rights_attribute, logic.operations_rights(initiator=context.account,
                                                                   clan=clan,
                                                                   is_moderator=context.account.has_perm('clans.moderate_clan')))


class ClanStaticOperationAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = 'clans.no_rights'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'

    ARG_PERMISSION = dext_views.ProcessorArgument()

    def validate(self, argument):
        return getattr(argument, self.permission)()

    def check(self, context):
        return getattr(context.current_clan_rights, self.permission)()


class ClanMemberOperationAccessProcessor(dext_views.AccessProcessor):
    ERROR_CODE = 'clans.no_rights'
    ERROR_MESSAGE = 'Вам запрещено проводить эту операцию'

    ARG_PERMISSION = dext_views.ProcessorArgument()

    def check(self, context):
        membership = logic.get_membership(context.target_account.id)

        if membership is None:
            return False

        return getattr(context.current_clan_rights, self.permission)(membership=membership)


class CanBeInvitedProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'clans.player_does_not_accept_invites_from_clans'
    ERROR_MESSAGE = 'Игрок не хочет прнимать приглашения от гильдий'
    ARGUMENT = 'target_account'

    def validate(self, argument):
        accept_invites_from_clans = accounts_tt_services.players_properties.cmd_get_object_property(object_id=argument.id,
                                                                                                    name='accept_invites_from_clans')
        return accept_invites_from_clans


class CanReceiveRequessProcessor(dext_views.FlaggedAccessProcessor):
    ERROR_CODE = 'clans.clan_does_not_accept_requests_from_players'
    ERROR_MESSAGE = 'Гильдия не принимает запросы на вступление от игроков.'
    ARGUMENT = 'current_clan'

    def validate(self, argument):
        accept_requests_from_players = tt_services.properties.cmd_get_object_property(object_id=argument.id,
                                                                                      name='accept_requests_from_players')
        return accept_requests_from_players


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='clans')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.AccountProcessor(get_name='account', context_name='target_account', default_value=None))
resource.add_processor(ClanProcessor())
resource.add_processor(ClanRightsProcessor(clan_attribute='current_clan'))
