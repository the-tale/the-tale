
import smart_imports

smart_imports.all()


class PlayerTimersClient(tt_api_timers.Client):

    def protobuf_to_type(self, type):
        return relations.PLAYER_TIMERS_TYPES(type)

    def type_to_protobuf(self, type):
        return type.value


players_timers = PlayerTimersClient(entry_point=conf.settings.TT_PLAYERS_TIMERS_ENTRY_POINT)


class PLAYER_PROPERTIES(tt_api_properties.PROPERTIES):
    records = (('accept_invites_from_clans', 0, 'принимать приглашения в гильдии',
                str, lambda value: value == 'True', True, tt_api_properties.TYPE.REPLACE),
               ('last_card_by_emissary', 1, 'время последнего получения Карты Судьбы по мероприятию эмиссара',
                str, float, 0, tt_api_properties.TYPE.REPLACE),
               ('last_premium_by_emissary', 2, 'время последнего получения подписки по мероприятию эмиссара',
                str, float, 0, tt_api_properties.TYPE.REPLACE),
               ('ip_address', 3, 'IP адресс, с которого был осуществлён вход',
                str, str, list, tt_api_properties.TYPE.APPEND))


class PlayersPropertiesClient(tt_api_properties.Client):
    pass


players_properties = PlayersPropertiesClient(entry_point=conf.settings.TT_PLAYERS_PROPERTIES_ENTRY_POINT,
                                             properties=PLAYER_PROPERTIES)


class DataProtectorClient(tt_api_data_protector.Client):
    pass


data_protector = DataProtectorClient(entry_point=conf.settings.TT_DATA_PROTECTOR_ENTRY_POINT)
